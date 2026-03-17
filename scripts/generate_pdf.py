#!/usr/bin/env python3
"""Generate PDF from the seminar Markdown article.

Requirements (install via uv):
    uv run --with playwright --with pymupdf python generate_pdf.py

First-time setup:
    uv run --with playwright python -m playwright install chromium
"""

import os
import re
import subprocess
import sys
import tempfile

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
ARTICLE_DIR = os.path.join(PROJECT_DIR, "article")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
MD_FILE = os.path.join(ARTICLE_DIR, "Seminar N. Metropolskaya. Aerodynamics of Sail.md")
PDF_FILE = os.path.join(OUT_DIR, "Seminar N. Metropolskaya. Aerodynamics of Sail.pdf")

FOOTER_LEFT = "Аэродинамика паруса — Н. Митропольская, 16.03.2026"

CSS = """
<style>
@page { size: A4; margin: 25mm 15mm 22mm 15mm; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 11pt; line-height: 1.5; color: #222;
    max-width: 700px; margin: 0 auto;
}
h1 { font-size: 22pt; }
h2 {
    font-size: 16pt;
    page-break-before: always; break-before: page;
    page-break-after: avoid; break-after: avoid;
    margin-top: 0; padding-top: 0.5em;
}
/* Содержание: no forced page break (stays on title page) */
h1 ~ h2:first-of-type { page-break-before: auto; break-before: auto; }
#содержание { page-break-before: auto; break-before: auto; }
h3 { font-size: 13pt; page-break-after: avoid; break-after: avoid; }
img { max-width: 100%; height: auto; page-break-inside: avoid; }
figure { page-break-inside: avoid; }
/* Hide image alt-text that pandoc renders as figcaption or visible text */
figure figcaption { display: none; }
img[alt] { /* alt text is not rendered in HTML, but pandoc wraps in figure */ }
p:has(> img) { page-break-inside: avoid; margin-bottom: 0; }
/* Italic captions: stay with image, add spacing after */
p:has(> img) + p > em:only-child,
p > em:only-child {
    page-break-before: avoid;
    display: block;
    margin-top: 2px;
    margin-bottom: 1em;
    font-size: 10pt;
    color: #555;
}
a { color: #1565c0; text-decoration: none; }
/* Hide pandoc-generated TOC */
#TOC, nav#TOC { display: none; }
/* Back-to-TOC links: small, muted */
a[href="#содержание"] { font-size: 9pt; color: #999; }
</style>
"""


def md_to_html(md_path: str, html_path: str) -> None:
    """Convert Markdown to HTML using pandoc with KaTeX math."""
    subprocess.run(
        [
            "pandoc", md_path,
            "-t", "html5",
            "--standalone",
            "--katex",
            "--metadata", "title=",
            "--resource-path", ARTICLE_DIR,
            "-o", html_path,
        ],
        check=True,
    )
    with open(html_path, "r") as f:
        html = f.read()

    # Inject CSS and fix image paths to absolute
    html = html.replace("</head>", CSS + "</head>")
    html = html.replace('src="images/', f'src="file://{ARTICLE_DIR}/images/')

    # Fix TOC: pandoc merges bare links into one <p>. Split them with <br>.
    # Pattern: </a> <a  ->  </a><br>\n<a
    html = re.sub(r"(</a>)\s*\n?\s*(<a\s)", r"\1<br>\n\2", html)

    # Fix numbered heading anchors: pandoc strips "N." prefix from IDs.
    # E.g. "## 1. Аэродинамическая сила" gets id="аэродинамическая-сила"
    # but TOC links use "#1-аэродинамическая-сила". Add duplicate anchor.
    # Use DOTALL since pandoc may put spans/katex inside h2.
    def add_numbered_anchor(m: re.Match) -> str:
        tag = m.group(0)
        existing_id = m.group(1)
        # Check if the heading content starts with "N. " (number + dot)
        text_match = re.search(r"(\d+)\.", tag)
        if text_match:
            num = text_match.group(1)
            numbered_id = f"{num}-{existing_id}"
            # Insert an anchor <a> right before the <h2> tag
            return f'<a id="{numbered_id}"></a>{tag}'
        return tag

    html = re.sub(
        r'<h2[^>]*id="([^"]+)"[^>]*>.*?</h2>',
        add_numbered_anchor,
        html,
        flags=re.DOTALL,
    )

    with open(html_path, "w") as f:
        f.write(html)


def html_to_pdf(html_path: str, pdf_path: str) -> None:
    """Render HTML to PDF using Chromium headless via Playwright."""
    from playwright.sync_api import sync_playwright

    # No Chromium headers/footers — both added by pymupdf post-processing
    # to support Cyrillic text and running h2 section names
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_path}", wait_until="networkidle")
        page.wait_for_timeout(3000)
        page.pdf(
            path=pdf_path,
            format="A4",
            margin={"top": "20mm", "bottom": "18mm", "left": "15mm", "right": "15mm"},
            print_background=True,
            display_header_footer=False,
        )
        browser.close()


def add_pdf_headers_and_bookmarks(pdf_path: str, md_path: str) -> None:
    """Add running h2 headers and PDF bookmarks via pymupdf."""
    import fitz

    with open(md_path, "r") as f:
        md = f.read()

    headings = [
        m.group(1).strip()
        for m in re.finditer(r"^## (.+)$", md, re.MULTILINE)
        if m.group(1).strip() != "Содержание"
    ]

    doc = fitz.open(pdf_path)
    num_pages = doc.page_count

    # Step 1: Find which page each h2 heading starts on
    heading_pages = []  # [(page_num_0based, heading_text), ...]
    for heading in headings:
        for page_num in range(num_pages):
            page = doc[page_num]
            results = page.search_for(heading)
            if results:
                if page_num < 2:
                    # Check if it also appears later (skip TOC mentions)
                    for pn2 in range(2, num_pages):
                        if doc[pn2].search_for(heading):
                            heading_pages.append((pn2, heading))
                            break
                    else:
                        heading_pages.append((page_num, heading))
                else:
                    heading_pages.append((page_num, heading))
                break

    # Sort by page number
    heading_pages.sort(key=lambda x: x[0])

    # Step 2: Build page→heading map (each page gets the heading of its section)
    page_heading = {}
    for i, (start_page, heading) in enumerate(heading_pages):
        end_page = heading_pages[i + 1][0] if i + 1 < len(heading_pages) else num_pages
        for p in range(start_page, end_page):
            page_heading[p] = heading

    # Step 3: Add running header text to each page (Cyrillic-capable font)
    # Use Arial.ttf which has Cyrillic glyphs (.ttc files don't load reliably)
    cyrillic_font = None
    for font_path in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]:
        if os.path.exists(font_path):
            cyrillic_font = fitz.Font(fontfile=font_path)
            break
    if cyrillic_font is None:
        print("WARNING: No Cyrillic-capable font found, headers will be missing")
        cyrillic_font = fitz.Font("helv")

    # Chromium PDF pages have an internal content-stream scale (~0.24x).
    # To add correctly-sized text, we create overlay pages with no transform,
    # then merge them onto the original pages.
    section_starts = {p for p, _ in heading_pages}

    # Create an overlay document for headers/footers
    overlay = fitz.open()

    for page_num in range(num_pages):
        page = doc[page_num]
        pw = page.rect.width
        ph = page.rect.height

        # Create a matching blank overlay page
        opage = overlay.new_page(width=pw, height=ph)

        # Running header
        header_text = page_heading.get(page_num, "")
        if header_text and page_num not in section_starts:
            hdr_size = 7.5
            text_length = cyrillic_font.text_length(header_text, fontsize=hdr_size)
            x = (pw - text_length) / 2
            y = 48
            tw = fitz.TextWriter(opage.rect)
            tw.append((x, y), header_text, font=cyrillic_font, fontsize=hdr_size)
            tw.write_text(opage, color=(0.4, 0.4, 0.4))

        # Footer left
        ftr_size = 6.5
        y_footer = ph - 35
        gray = (0.4, 0.4, 0.4)

        tw2 = fitz.TextWriter(opage.rect)
        tw2.append((42, y_footer), FOOTER_LEFT, font=cyrillic_font, fontsize=ftr_size)
        tw2.write_text(opage, color=gray)

        # Footer right
        page_str = f"{page_num + 1} из {num_pages}"
        text_len = cyrillic_font.text_length(page_str, fontsize=ftr_size)
        tw3 = fitz.TextWriter(opage.rect)
        tw3.append((pw - 42 - text_len, y_footer), page_str, font=cyrillic_font, fontsize=ftr_size)
        tw3.write_text(opage, color=gray)

    # Merge overlay onto original pages
    for page_num in range(num_pages):
        page = doc[page_num]
        page.show_pdf_page(page.rect, overlay, page_num)

    overlay.close()

    # Step 4: Set PDF bookmarks/TOC
    toc = [[1, heading, page_num + 1] for page_num, heading in heading_pages]
    doc.set_toc(toc)

    doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    print(f"PDF: {len(toc)} bookmarks, {num_pages} pages, running headers added")
    for t in toc:
        print(f"  p{t[2]:>2}: {t[1]}")


def main() -> None:
    if not os.path.exists(MD_FILE):
        print(f"Error: {MD_FILE} not found")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        html_path = tmp.name

    try:
        print("1. Converting Markdown → HTML...")
        md_to_html(MD_FILE, html_path)

        print("2. Rendering HTML → PDF...")
        html_to_pdf(html_path, PDF_FILE)
        print(f"   {os.path.getsize(PDF_FILE) / 1024 / 1024:.1f} MB")

        print("3. Adding headers and bookmarks...")
        add_pdf_headers_and_bookmarks(PDF_FILE, MD_FILE)

        print(f"\nDone: {PDF_FILE}")
    finally:
        os.unlink(html_path)


if __name__ == "__main__":
    main()
