# Seminar: Aerodynamics of Sail — N. Mitropolskaya
# Justfile for common tasks

md := "Seminar N. Metropolskaya. Aerodynamics of Sail.md"
pdf := "Seminar N. Metropolskaya. Aerodynamics of Sail.pdf"

# Run tests
test:
    uv run --with pytest pytest test_article.py -v

# Generate PDF from Markdown
pdf:
    uv run --with playwright --with pymupdf python generate_pdf.py

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
    ls -la images/

# Check for broken image references
check:
    #!/usr/bin/env bash
    set -euo pipefail
    md="{{md}}"
    echo "=== Broken image refs ==="
    grep -o 'images/[^)]*' "$md" | while read f; do test -f "$f" || echo "  BROKEN: $f"; done || true
    echo "=== Unused images ==="
    for f in images/*; do fname=$(basename "$f"); grep -q "$fname" "$md" || echo "  UNUSED: $fname"; done || true
    echo "=== Stats ==="
    echo "Images: $(ls images/ | wc -l | tr -d ' ')"
    echo "Image refs: $(grep -c 'images/' "$md")"
    echo "Lines: $(wc -l < "$md" | tr -d ' ')"
