# Seminar: Aerodynamics of Sail — N. Mitropolskaya
# Justfile for common tasks

md := "article/Seminar N. Metropolskaya. Aerodynamics of Sail.md"
pdf := "out/Seminar N. Metropolskaya. Aerodynamics of Sail.pdf"

# Run tests
test:
    uv run --with pytest pytest scripts/test_article.py -v

# Generate PDF from Markdown
pdf:
    uv run --with playwright --with pymupdf python scripts/generate_pdf.py

# Install playwright browser (first-time setup)
setup:
    uv run --with playwright python -m playwright install chromium

# Open the PDF
open:
    open "{{pdf}}"

# Open the Markdown in Sublime Text
edit:
    subl "{{md}}"

# Count words in the article
wc:
    wc -w "{{md}}"

# List all images
images:
    ls -la article/images/

# Check for broken image references
check:
    #!/usr/bin/env bash
    set -euo pipefail
    md="{{md}}"
    echo "=== Broken image refs ==="
    grep -o 'images/[^)]*' "$md" | while read f; do test -f "article/$f" || echo "  BROKEN: $f"; done || true
    echo "=== Unused images ==="
    for f in article/images/*; do fname=$(basename "$f"); grep -q "$fname" "$md" || echo "  UNUSED: $fname"; done || true
    echo "=== Stats ==="
    echo "Images: $(ls article/images/ | wc -l | tr -d ' ')"
    echo "Image refs: $(grep -c 'images/' "$md")"
    echo "Lines: $(wc -l < "$md" | tr -d ' ')"
