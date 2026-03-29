#!/usr/bin/env python3
"""Generate DOCX from the seminar Markdown article.

Usage:
    uv run python scripts/generate_docx.py
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
DOCX_FILE = os.path.join(OUT_DIR, "Seminar N. Metropolskaya. Aerodynamics of Sail.docx")


def main() -> None:
    if not os.path.exists(MD_FILE):
        print(f"Error: {MD_FILE} not found")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    with open(MD_FILE, "r") as f:
        md = f.read()

    # Pandoc merges consecutive bare links into one paragraph.
    # Append backslash (hard line break) to each TOC link line for compact spacing.
    md = re.sub(r"(\]\([^)]+\))\n(\[)", r"\1\\\n\2", md)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, dir=ARTICLE_DIR,
    ) as tmp:
        tmp.write(md)
        tmp_md = tmp.name

    try:
        print("Converting Markdown → DOCX...")
        subprocess.run(
            [
                "pandoc", tmp_md,
                "-t", "docx",
                "--resource-path", ARTICLE_DIR,
                "--lua-filter", os.path.join(SCRIPTS_DIR, "pagebreak.lua"),
                "-o", DOCX_FILE,
            ],
            check=True,
        )
    finally:
        os.unlink(tmp_md)

    size_mb = os.path.getsize(DOCX_FILE) / 1024 / 1024
    print(f"Done: {DOCX_FILE} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
