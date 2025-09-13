#!/usr/bin/env bash
# Reference snippet of key one-liners used during the session

# List markdown sources and quick sensitive scan
rg -l --hidden -S "\.md$" "/Users/jagannath/Downloads/coding/personal/telnyx-work"
rg -n --no-heading -S -e "AKIA[0-9A-Z]{16}" -e "ASIA[0-9A-Z]{16}" -e "SECRET|PASSWORD|PASSWD|TOKEN|API[-_]?KEY|AUTHORIZATION|BEARER" -e "-----BEGIN [A-Z ]+PRIVATE KEY-----" -e "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b" -e "\b(?:\d{1,3}\.){3}\d{1,3}\b" "/Users/jagannath/Downloads/coding/personal/telnyx-work"

# Install Python tools (in your venv)
~/jagans_venv/bin/pip install --upgrade markdown Pygments pypdf pdfminer.six

# Generate blog with sanitization & highlighting
~/jagans_venv/bin/python scripts/generate_blog.py --src \
 "/Users/jagannath/Downloads/coding/personal/telnyx-work"

# Scrub org/internal names, simplify slugs, and merge overlapping posts
~/jagans_venv/bin/python scripts/sanitize_posts.py
~/jagans_venv/bin/python scripts/sanitize_posts.py \
  --merge wireless-sim-tool--devops-automation-blog.html \
  --merge-with wireless-epc--devops-automation-blog.html \
  --merge-title "DevOps Automation in Telecom: SIM and EPC" \
  --merge-slug devops-automation-telecom.html

# Extract LinkedIn summary to update homepage text
~/jagans_venv/bin/python scripts/extract_linkedin.py \
 "/Users/jagannath/Downloads/coding/personal/telnyx-work/Profile-2.pdf"

# Serve locally
python3 -m http.server 4001

# Deploy org site (first time)
bash scripts/deploy_org_site.sh git@github.com:Nuti-Consultants/Nuti-Consultants.github.io.git

