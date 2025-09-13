import argparse, html, re
from pathlib import Path


def args():
    p = argparse.ArgumentParser(description="Scrub company/repo refs, simplify filenames, optionally merge two posts.")
    p.add_argument("--posts-dir", default="blog/posts", help="Directory with generated post HTML files")
    p.add_argument("--merge", help="First post filename to merge")
    p.add_argument("--merge-with", dest="merge_with", help="Second post filename to merge")
    p.add_argument("--merge-title", dest="merge_title", default="DevOps Automation in Telecom: SIM and EPC")
    p.add_argument("--merge-slug", dest="merge_slug", default="devops-automation-telecom.html")
    return p.parse_args()


COMPANY_PATS = [re.compile(r"\bTelnyx\b", re.I)]
REPO_TERMS = [
    'wireless-ims-cscf-1','deploy-core-wireless-main','wireless-epc','wireless-sim-tool',
    'infra-svc-prometheus','wireless-pwg-dns','wireless-stp','wireless-fulfillment-scripts',
    'wireless-fulfillment-scripts-new','wireless-query-exporter-1','tlnx-cloud-router-setup-1',
    'local_testing','ansible'
]
REPO_PATS = [re.compile(re.escape(t), re.I) for t in REPO_TERMS]


def scrub(s: str) -> str:
    for pat in COMPANY_PATS:
        s = pat.sub('', s)
    for pat in REPO_PATS:
        s = pat.sub('project', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s


def simplify_name(stem: str) -> str:
    return stem.split('--', 1)[1] if '--' in stem else stem


def extract_body(html_text: str) -> str:
    m = re.search(r'<div class="content markdown">(.*)</div>\s*</article>', html_text, re.S)
    return m.group(1).strip() if m else ''


def main():
    a = args()
    posts = Path(a.posts_dir)
    assert posts.is_dir(), f"Not found: {posts}"

    # Scrub & rename
    for p in sorted(posts.glob('*.html')):
        s = p.read_text(encoding='utf-8', errors='ignore')
        s2 = scrub(s)
        if s2 != s:
            p.write_text(s2, encoding='utf-8')
        newname = simplify_name(p.stem) + '.html'
        if newname != p.name:
            q = p.with_name(newname)
            idx = 2
            while q.exists():
                q = p.with_name(f"{simplify_name(p.stem)}-{idx}.html")
                idx += 1
            p.rename(q)

    # Merge if requested
    if a.merge and a.merge_with:
        f1 = posts / a.merge
        f2 = posts / a.merge_with
        bodies = []
        if f1.exists():
            bodies.append(f"<section><h3>Section 1</h3>{extract_body(f1.read_text(encoding='utf-8', errors='ignore'))}</section>")
        if f2.exists():
            bodies.append(f"<section><h3>Section 2</h3>{extract_body(f2.read_text(encoding='utf-8', errors='ignore'))}</section>")
        if bodies:
            page = f"""<!DOCTYPE HTML>
<html>
  <head>
    <title>{html.escape(a.merge_title)} - Future Imperfect</title>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, user-scalable=no\" />
    <link rel=\"stylesheet\" href=\"../assets/css/main.css\" />
    <link rel=\"stylesheet\" href=\"../assets/css/codehilite.css\" />
  </head>
  <body class=\"single is-preload\">\n    <div id=\"wrapper\">\n      <header id=\"header\"><h1><a href=\"../index.html\">Future Imperfect</a></h1></header>\n      <div id=\"main\">\n        <article class=\"post\">\n          <header><div class=\"title\"><h2>{html.escape(a.merge_title)}</h2><p>Practical automation approaches for telecom workflows.</p></div><div class=\"meta\"><span class=\"published\">DevOps</span></div></header>\n          <div class=\"content markdown\">{''.join(bodies)}</div>\n        </article>\n      </div>\n    </div>\n  </body>\n</html>"""
            (posts / a.merge_slug).write_text(page, encoding='utf-8')
            if f1.exists(): f1.unlink()
            if f2.exists(): f2.unlink()

    print("Sanitization complete.")


if __name__ == "__main__":
    main()

