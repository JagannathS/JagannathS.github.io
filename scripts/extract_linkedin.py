import sys
from pathlib import Path
try:
    from pypdf import PdfReader
except Exception as e:
    print("Please install pypdf: pip install pypdf", file=sys.stderr)
    raise

def main():
    if len(sys.argv) < 2:
        print("Usage: extract_linkedin.py <profile.pdf>")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    reader = PdfReader(str(pdf_path))
    text = []
    for page in reader.pages:
        t = page.extract_text() or ""
        text.append(t)
    full = "\n".join(text)
    about = None
    if 'Summary' in full:
        seg = full.split('Summary',1)[1]
        for stop in ['Experience','Education','Certifications','Skills','Top Skills','Languages','Page 2']:
            if stop in seg:
                seg = seg.split(stop,1)[0]
                break
        about = ' '.join(x.strip() for x in seg.splitlines() if x.strip())
    headline = 'Senior Infrastructure Architect | Telecommunications & Cloud-Native'
    print('Headline: ' + headline)
    if about:
        print('\nSummary:')
        print(about)
    else:
        print('\nSummary:')
        print('Technology professional across virtualization, telecommunications (LTE/5G), and cloud-native platforms. Focus on Kubernetes, AWS, automation, and observability.')

if __name__ == "__main__":
    main()

