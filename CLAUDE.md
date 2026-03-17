# Project: Mitropolskaya Aerodynamics Seminar

Transcription and illustrated article based on Natalia Mitropolskaya's seminar on sail aerodynamics for the Equipage yacht club (16.03.2026).

## Structure

- `src/` — source materials (not generated)
  - `slides.pdf` — original presentation slides
  - `subtitles.vtt` — video subtitles (Russian)
  - `transcript.txt` — cleaned transcript
- `article/` — the article and its images
  - `Seminar N. Metropolskaya. Aerodynamics of Sail.md` — main article (Russian)
  - `images/` — slide images, prefixed with section numbers (e.g. `01_`, `06_`)
- `out/` — generated output (gitignored)
  - `Seminar N. Metropolskaya. Aerodynamics of Sail.pdf` — generated PDF
- `scripts/` — code
  - `generate_pdf.py` — builds PDF from Markdown (pandoc + playwright + pymupdf)
  - `test_article.py` — 30 integrity tests (images, links, structure, dictionary, math)
- `justfile` — common tasks (`just pdf`, `just test`, `just check`, etc.)

## Sources

- Video: youtu.be/MXJhzNGrsMo
- Slides PDF: Google Drive (2026-03-16 Mitropolskaya Aerodynamics.pdf)
- Lecture notes: Obsidian vault (3Segeln/2 Physics/)

## PDF generation

All PDF changes must be made in `scripts/generate_pdf.py` for reproducibility. Never use ad-hoc commands.

Requires: pandoc, uv, Chromium (via playwright).

```
just setup  # first time: install Chromium
just pdf    # generate PDF
just test   # run integrity tests
just check  # check broken/unused image refs
```

PDF features:
- Running h2 section headers on each page (via pymupdf overlay, not Chromium headers)
- Footer with document title + page numbers (X из Y)
- No header/footer on section start pages (where h2 heading appears)
- PDF bookmarks (TOC) for all sections
- KaTeX math rendering
- Numbered anchor IDs injected for TOC internal links

## Conventions

- Article language: Russian
- Dictionary terms: Russian primary, English in parentheses, bold, with Wikipedia links
- Image naming: `NN_descriptive-english-name.jpeg` where NN = h2 section number
- Misleading diagrams marked with warning markers and explanation text
- Image alt-text: short filename-based; detailed descriptions as italic text below images
- Each h2 starts on a new page (CSS `page-break-before: always`)
- Each h2 has a `[up Содержание](#содержание)` back-link
- TOC in markdown uses bare links (not bullet list) — rendered with `<br>` in PDF
- Lists in markdown need blank line before first `- ` item (pandoc requirement)
