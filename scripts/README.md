# Scripts: Blog Import, Sanitization, Org Site, and Homepage Updates

These scripts reproduce what we did in this session: import and sanitize blog posts, render Markdown to HTML with highlighting, rebuild the blog index with category filters, scrub org‑specific references, optionally merge overlapping posts, extract summary from a LinkedIn PDF, and deploy the org site.

## Prerequisites
- Python 3.10+
- Use your venv: `~/jagans_venv`
- Install tools:
  - `~/jagans_venv/bin/pip install markdown Pygments pypdf pdfminer.six`

## 1) Generate Blog from Markdown
Render sanitized posts (only files with "blog" in filename; excludes linkedin/work summaries) and rebuild index with filters + sidebar.

Command:
- `~/jagans_venv/bin/python scripts/generate_blog.py --src \
  "/Users/jagannath/Downloads/coding/personal/telnyx-work"`

Notes:
- Outputs to `blog/posts/`, `blog/images/<slug>/`, and rewrites `blog/index.html`.
- Sanitizes bearer tokens/keys and replaces non‑private IPv4s with `203.0.113.100`.
- Category filters via URL hash: `blog/index.html#infra`, `#devops`, `#monitoring`, `#telecom`, `#containers`, `#security`.

## 2) Sanitize & Rename Generated Posts
Scrub company/repo names, simplify filenames, and (optionally) merge two posts into one.

Examples:
- Scrub & rename: `~/jagans_venv/bin/python scripts/sanitize_posts.py`
- Merge two posts:
  `~/jagans_venv/bin/python scripts/sanitize_posts.py \
   --merge wireless-sim-tool--devops-automation-blog.html \
   --merge-with wireless-epc--devops-automation-blog.html \
   --merge-title "DevOps Automation in Telecom: SIM and EPC" \
   --merge-slug devops-automation-telecom.html`

## 3) Extract Summary from LinkedIn PDF
Extracts a concise summary text block for homepage updates.

- `~/jagans_venv/bin/python scripts/extract_linkedin.py \
   "/Users/jagannath/Downloads/coding/personal/telnyx-work/Profile-2.pdf"`

## 4) Deploy Org Site (Nuti-Consultants)
Initial push for GitHub Pages org site (run from `Nuti-Consultants.github.io`).

- `bash scripts/deploy_org_site.sh git@github.com:Nuti-Consultants/Nuti-Consultants.github.io.git`

## 5) Session Commands Log
See `scripts/commands.sh` for the main one‑liners used during this session (for reference/replay).

Caution: These scripts write files in `blog/` and `Nuti-Consultants.github.io/`. Commit your work before running if you want an easy rollback.
