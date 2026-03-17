# YouTube Video to Rich PDF: A Complete Pipeline Example

A working example of converting a YouTube lecture into a professionally typeset PDF article with illustrations, math formulas, and structured navigation.

This pipeline was used to produce an illustrated article from [a sail aerodynamics seminar](https://youtu.be/MXJhzNGrsMo) by Natalia Mitropolskaya (Equipage yacht club, March 2026).

## The Pipeline

```
YouTube Video          Lecture Notes
     |                      |
     v                      |
 Subtitles (.vtt)           |
     |                      |
     v                      v
 Transcript (.txt)  +  Obsidian Notes
     |                      |
     +----------+-----------+
                |
                v
     Markdown Article (.md)
      + slide images
                |
                v
     pandoc (Markdown -> HTML)
      + KaTeX (math rendering)
                |
                v
     Playwright + Chromium (HTML -> PDF)
                |
                v
     PyMuPDF post-processing
      + running section headers
      + footer with page numbers
      + PDF bookmarks (TOC)
                |
                v
         Rich PDF Output
```

## What makes the PDF "rich"

- Table of contents with clickable PDF bookmarks
- Running section headers on each page (current h2 title)
- Footer with document title and page numbering (X of Y)
- KaTeX-rendered math formulas
- 50+ illustrations extracted from presentation slides
- Each section starts on a new page
- No header/footer on section start pages (clean section breaks)

## Project Structure

```
src/                    # Source materials (not generated)
  subtitles.vtt         #   YouTube subtitles (Russian)
  transcript.txt        #   Cleaned transcript
  slides.pdf            #   Original presentation slides
article/                # The article
  *.md                  #   Markdown article (Russian)
  images/               #   Slide images, prefixed by section number
scripts/                # Pipeline code
  generate_pdf.py       #   Markdown -> HTML -> PDF with post-processing
  test_article.py       #   30 integrity tests (images, links, structure)
out/                    # Generated output (gitignored)
  *.pdf                 #   Final PDF
justfile                # Task runner (just pdf, just test, etc.)
```

## Quick Start

Prerequisites: [pandoc](https://pandoc.org/), [uv](https://docs.astral.sh/uv/), [just](https://github.com/casey/just)

```bash
just setup  # install Chromium via Playwright (once)
just pdf    # generate PDF from Markdown
just test   # run 30 integrity tests
just check  # verify image references
just open   # open the generated PDF
```

## How Each Step Works

### 1. YouTube Video -> Transcript

YouTube subtitles were downloaded as `.vtt` and cleaned into a plain text transcript. The transcript captures the speaker's explanations, analogies, and asides that don't appear in slides.

### 2. Transcript + Notes -> Markdown Article

The transcript was cross-referenced with lecture notes (Obsidian) to produce a structured Markdown article. The notes provided technical precision (formulas, terminology, references); the transcript provided narrative flow and the speaker's original reasoning.

### 3. Slides -> Images

Key diagrams were extracted from the presentation PDF and named by section number for easy reference (e.g., `06_gentry-fig17-developed-circulation.png`).

### 4. Markdown -> Rich PDF

The PDF generation pipeline ([`scripts/generate_pdf.py`](scripts/generate_pdf.py)) runs in three stages:

1. **pandoc** converts Markdown to standalone HTML5 with KaTeX math rendering
2. **Playwright** (headless Chromium) renders HTML to a paginated PDF
3. **PyMuPDF** adds post-processing that Chromium can't do natively:
   - Running h2 section headers (requires text search across pages)
   - Cyrillic-capable footer with page numbers
   - PDF bookmarks/TOC from Markdown headings
   - Suppresses header/footer on pages where a new section starts

### 5. Quality Assurance

30 pytest tests ([`scripts/test_article.py`](scripts/test_article.py)) verify:
- All image references resolve to existing files
- No unused images in the images directory
- Markdown structure follows conventions (headings, TOC links, blank lines before lists)
- Dictionary terms follow the bilingual format
- Math expressions render correctly

## Dependencies

- [pandoc](https://pandoc.org/) -- Markdown to HTML conversion
- [uv](https://docs.astral.sh/uv/) -- Python dependency management (no virtualenv setup needed)
- [playwright](https://playwright.dev/python/) + Chromium -- HTML to PDF rendering
- [pymupdf](https://pymupdf.readthedocs.io/) -- PDF post-processing (headers, footers, bookmarks)
- [pytest](https://pytest.org/) -- article integrity tests
- [just](https://github.com/casey/just) -- task runner

## License

Code is licensed under [MIT](LICENSE). Article content and images are copyright of their respective authors.
