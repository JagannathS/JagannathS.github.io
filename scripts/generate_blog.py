import argparse, html, ipaddress, re, shutil, sys
from pathlib import Path
from markdown import markdown


def build_args():
    p = argparse.ArgumentParser(description="Generate blog from Markdown with sanitization and filters")
    p.add_argument("--src", required=True, help="Source root directory containing markdown files")
    p.add_argument("--out", default="blog", help="Blog output directory (default: blog)")
    return p.parse_args()


ALLOWED_IPS = {ipaddress.ip_address(x) for x in [
    '8.8.8.8','8.8.4.4','1.1.1.1','1.0.0.1','0.0.0.0','255.255.255.255'
]}
ALLOWED_NETS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('192.0.2.0/24'),
    ipaddress.ip_network('198.51.100.0/24'),
    ipaddress.ip_network('203.0.113.0/24'),
]

BEARER_RE = re.compile(r'(Authorization:\s*Bearer)\s+[^\n\r]+', re.I)
KV_RE = re.compile(r'\b(SECRET|TOKEN|PASSWORD|PASSWD|API[_-]?KEY)\b(\s*[:=]\s*)([^\s\"\']+)', re.I)
IP_RE = re.compile(r'\b(\d{1,3}(?:\.\d{1,3}){3})\b')
IMG_MD_RE = re.compile(r'(!\[[^\]]*\]\()([^\)]+)(\))')
IMG_HTML_RE = re.compile(r'(<img[^>]+src=["\'])([^"\']+)(["\'])', re.I)

CATEGORY_MAP = [
    ('aws', 'aws'),
    ('k8s', 'containers'), ('kubernetes', 'containers'), ('container', 'containers'), ('docker','containers'),
    ('monitor', 'monitoring'), ('observab', 'monitoring'), ('prometheus','monitoring'),
    ('infra', 'infra'), ('infrastructure', 'infra'), ('network', 'infra'), ('dns','infra'), ('ims','telecom'), ('epc','telecom'), ('stp','telecom'), ('diameter','telecom'), ('gtp','telecom'), ('telecom','telecom'),
    ('devops','devops'), ('cicd','devops'), ('ansible','automation'), ('automation','automation'),
    ('security','security'), ('vault','security')
]

CATEGORY_LABELS = {
    'infra':'Infra', 'automation':'Automation', 'aws':'AWS', 'monitoring':'Monitoring',
    'telecom':'Telecom', 'containers':'Containers', 'devops':'DevOps', 'security':'Security', 'other':'Other'
}

EXCLUDE_PATTERNS = ['linkedin', 'workdone', 'work-done', 'summary']


def ip_safe(s: str) -> bool:
    try:
        ip = ipaddress.ip_address(s)
    except ValueError:
        return False
    return ip in ALLOWED_IPS or any(ip in net for net in ALLOWED_NETS)


def sanitize(text: str) -> str:
    text = BEARER_RE.sub(r'\1 <REDACTED>', text)
    text = KV_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}<REDACTED>", text)
    text = text.replace('89.221.38.84', '203.0.113.100')
    def ip_sub(m):
        return m.group(1) if ip_safe(m.group(1)) else '203.0.113.100'
    return IP_RE.sub(ip_sub, text)


def pick_category(path: Path) -> str:
    name = path.name.lower()
    for key, cat in CATEGORY_MAP:
        if key in name:
            return cat
    pstr = path.as_posix().lower()
    for key, cat in CATEGORY_MAP:
        if key in pstr:
            return cat
    return 'other'


def main():
    args = build_args()
    src = Path(args.src)
    out_root = Path(args.out)
    posts_dir = out_root / 'posts'
    images_root = out_root / 'images'
    posts_dir.mkdir(parents=True, exist_ok=True)
    images_root.mkdir(parents=True, exist_ok=True)

    # Discover eligible markdown files
    files = []
    for p in src.rglob('*.md'):
        name = p.name.lower()
        if 'blog' not in name:
            continue
        if any(x in name for x in EXCLUDE_PATTERNS):
            continue
        files.append(p)
    files.sort()

    posts = []
    for f in files:
        raw = f.read_text(encoding='utf-8', errors='ignore')
        raw = sanitize(raw)

        # Rewrite images
        rel = f.relative_to(src).as_posix()
        slug = rel.replace('/', '--').rsplit('.md', 1)[0]
        img_dir = images_root / slug
        img_dir.mkdir(parents=True, exist_ok=True)

        def rewrite_img(path_str: str) -> str:
            p = path_str.strip()
            if p.startswith(('http://','https://','data:')):
                return p
            src_path = (f.parent / p).resolve()
            if src_path.is_file():
                dest = img_dir / src_path.name
                if not dest.exists():
                    try:
                        shutil.copy2(src_path, dest)
                    except Exception:
                        pass
                return f"../images/{slug}/{src_path.name}"
            return p

        raw = IMG_MD_RE.sub(lambda m: m.group(1) + rewrite_img(m.group(2)) + m.group(3), raw)
        raw = IMG_HTML_RE.sub(lambda m: m.group(1) + rewrite_img(m.group(2)) + m.group(3), raw)

        # Title/teaser/category
        m = re.search(r'^#\s+(.+)$', raw, re.M)
        title = m.group(1).strip() if m else f.stem
        teaser = ''
        for line in raw.splitlines():
            if line.strip().startswith('#') or not line.strip():
                continue
            teaser = line.strip()
            break
        category = pick_category(f)

        body_html = markdown(raw, extensions=['extra','fenced_code','tables','codehilite'])

        out = posts_dir / f"{slug}.html"
        page = f"""<!DOCTYPE HTML>
<html>
  <head>
    <title>{html.escape(title)} - Future Imperfect</title>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, user-scalable=no\" />
    <link rel=\"stylesheet\" href=\"../assets/css/main.css\" />
    <link rel=\"stylesheet\" href=\"../assets/css/codehilite.css\" />
  </head>
  <body class=\"single is-preload\">
    <div id=\"wrapper\">
      <header id=\"header\"><h1><a href=\"../index.html\">Future Imperfect</a></h1></header>
      <div id=\"main\">
        <article class=\"post\">
          <header><div class=\"title\"><h2>{html.escape(title)}</h2><p>{html.escape(teaser)}</p></div><div class=\"meta\"><span class=\"published\">{CATEGORY_LABELS.get(category, 'Other')}</span></div></header>
          <div class=\"content markdown\">{body_html}</div>
          <footer><ul class=\"stats\"><li><a href=\"../index.html\">Back to posts</a></li></ul></footer>
        </article>
      </div>
      <section id=\"sidebar\">
        <section><header><h3>About</h3></header><p>Notes on telecom, infra, and automation.</p></section>
      </section>
      <section id=\"footer\"><p class=\"copyright\">&copy;</p></section>
    </div>
    <script src=\"../assets/js/jquery.min.js\"></script>
    <script src=\"../assets/js/browser.min.js\"></script>
    <script src=\"../assets/js/breakpoints.min.js\"></script>
    <script src=\"../assets/js/util.js\"></script>
    <script src=\"../assets/js/main.js\"></script>
  </body>
</html>"""
        out.write_text(page, encoding='utf-8')
        posts.append((slug, title, teaser, category))

    # Build index with filters + sidebar
    cats = {}
    for _, _, _, c in posts:
        cats[c] = cats.get(c, 0) + 1

    header = [
        "<!DOCTYPE HTML>",
        "<html>",
        "  <head>",
        "    <title>Future Imperfect</title>",
        "    <meta charset=\"utf-8\" />",
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, user-scalable=no\" />",
        "    <link rel=\"stylesheet\" href=\"assets/css/main.css\" />",
        "  </head>",
        "  <body class=\"is-preload\">",
        "    <div id=\"wrapper\">",
        "      <header id=\"header\">",
        "        <h1><a href=\"index.html\">Future Imperfect</a></h1>",
        "        <nav class=\"links\"><ul>",
        "          <li><a href=\"#\" data-filter=\"all\">All</a></li>",
    ]
    for c, n in cats.items():
        header.append(f"          <li><a href='#' data-filter='{c}'>{CATEGORY_LABELS.get(c, c.title())} ({n})</a></li>")
    header += [
        "        </ul></nav>",
        "      </header>",
        "      <div id=\"main\">",
    ]

    posts_html = []
    for slug, title, teaser, category in posts:
        posts_html.append(
            f"""
        <article class=\"post\" data-category=\"{category}\">
          <header>
            <div class=\"title\"><h2><a href=\"posts/{slug}.html\">{html.escape(title)}</a></h2><p>{html.escape(teaser)}</p></div>
            <div class=\"meta\"><span class=\"published\">{CATEGORY_LABELS.get(category,'Other')}</span></div>
          </header>
          <footer>
            <ul class=\"actions\"><li><a href=\"posts/{slug}.html\" class=\"button large\">Continue Reading</a></li></ul>
            <ul class=\"stats\"><li><a href=\"#\">{CATEGORY_LABELS.get(category,'Other')}</a></li></ul>
          </footer>
        </article>
            """
        )

    sidebar = [
        "      </div>",
        "      <section id=\"sidebar\">",
        "        <section><header><h3>About</h3></header><p>Notes on telecom, infra, and automation.</p></section>",
        "        <section><header><h3>Categories</h3></header><ul class=\"posts\">",
    ]
    for c, n in cats.items():
        sidebar.append(f"          <li><a href='#' data-filter='{c}'>{CATEGORY_LABELS.get(c,c.title())}</a> <span class='published'>({n})</span></li>")
    sidebar += [
        "        </ul></section>",
        "      </section>",
        "      <section id=\"footer\"><p class=\"copyright\">&copy;</p></section>",
        "    </div>",
        "    <script src=\"assets/js/jquery.min.js\"></script>",
        "    <script src=\"assets/js/browser.min.js\"></script>",
        "    <script src=\"assets/js/breakpoints.min.js\"></script>",
        "    <script src=\"assets/js/util.js\"></script>",
        "    <script src=\"assets/js/main.js\"></script>",
        "    <script>",
        "      (function(){",
        "        function setFilter(cat){",
        "          document.querySelectorAll('#header nav.links a').forEach(function(a){a.classList.toggle('active', a.getAttribute('data-filter')===cat);});",
        "          document.querySelectorAll('#main article.post').forEach(function(el){",
        "            var c = el.getAttribute('data-category');",
        "            el.style.display = (cat==='all' || c===cat) ? '' : 'none';",
        "          });",
        "        }",
        "        function applyFromHash(){",
        "          var h=(location.hash||'').replace('#','').toLowerCase();",
        "          var cats=['all','infra','automation','aws','monitoring','telecom','containers','devops','security','other'];",
        "          if(cats.indexOf(h)>=0){ setFilter(h); } else { setFilter('all'); }",
        "        }",
        "        document.querySelectorAll('#header nav.links a, #sidebar a[data-filter]').forEach(function(a){",
        "          var f=a.getAttribute('data-filter'); if(!f) return;",
        "          a.addEventListener('click', function(e){ e.preventDefault(); history.replaceState(null,'','#'+f); setFilter(f); });",
        "        });",
        "        window.addEventListener('hashchange', applyFromHash);",
        "        applyFromHash();",
        "      })();",
        "    </script>",
        "  </body>",
        "</html>",
    ]

    index_html = "\n".join(header + posts_html + sidebar)
    (out_root / 'index.html').write_text(index_html, encoding='utf-8')
    print(f"Rendered {len(posts)} posts to {posts_dir} and rebuilt {out_root/'index.html'}")


if __name__ == "__main__":
    main()

