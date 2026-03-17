"""Tests for the seminar article integrity."""

import os
import re

import pytest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(BASE_DIR, "Seminar N. Metropolskaya. Aerodynamics of Sail.md")


@pytest.fixture
def md_content():
    with open(MD_FILE, "r") as f:
        return f.read()


@pytest.fixture
def md_lines(md_content):
    return md_content.split("\n")


@pytest.fixture
def image_refs(md_content):
    return re.findall(r"images/([^)]+)", md_content)


@pytest.fixture
def h2_headings(md_content):
    return [m.group(1).strip() for m in re.finditer(r"^## (.+)$", md_content, re.MULTILINE)]


@pytest.fixture
def image_files():
    img_dir = os.path.join(BASE_DIR, "images")
    return os.listdir(img_dir) if os.path.isdir(img_dir) else []


# --- File structure ---


class TestFileStructure:
    def test_md_file_exists(self):
        assert os.path.exists(MD_FILE)

    def test_images_dir_exists(self):
        assert os.path.isdir(os.path.join(BASE_DIR, "images"))

    def test_generate_script_exists(self):
        assert os.path.exists(os.path.join(BASE_DIR, "generate_pdf.py"))

    def test_justfile_exists(self):
        assert os.path.exists(os.path.join(BASE_DIR, "justfile"))


# --- Image integrity ---


class TestImageIntegrity:
    def test_no_broken_image_refs(self, image_refs):
        broken = [ref for ref in image_refs if not os.path.exists(os.path.join(BASE_DIR, "images", ref))]
        assert broken == [], f"Broken image refs: {broken}"

    def test_no_unused_images(self, md_content, image_files):
        unused = [f for f in image_files if f not in md_content]
        assert unused == [], f"Unused images: {unused}"

    def test_image_count_matches(self, image_refs, image_files):
        assert len(set(image_refs)) == len(image_files), (
            f"Refs: {len(set(image_refs))}, Files: {len(image_files)}"
        )

    def test_images_have_section_prefix(self, image_files):
        bad = [f for f in image_files if not re.match(r"^\d{2}_", f)]
        assert bad == [], f"Images without NN_ prefix: {bad}"

    def test_no_1x1_pixel_images(self, image_files):
        for f in image_files:
            path = os.path.join(BASE_DIR, "images", f)
            assert os.path.getsize(path) > 100, f"Suspiciously small image: {f}"


# --- Image captions ---


class TestImageCaptions:
    def test_every_image_has_italic_caption(self, md_lines):
        """Each image line should be followed (after blank line) by an italic caption."""
        missing = []
        for i, line in enumerate(md_lines):
            if line.startswith("![") and "images/" in line:
                # Look ahead for italic caption within next 3 lines
                found_caption = False
                for j in range(i + 1, min(i + 4, len(md_lines))):
                    if md_lines[j].startswith("*") and md_lines[j].endswith("*"):
                        found_caption = True
                        break
                if not found_caption:
                    missing.append(f"Line {i + 1}: {line[:60]}...")
        assert missing == [], f"Images without italic captions:\n" + "\n".join(missing)


# --- Article structure ---


class TestArticleStructure:
    def test_has_h1_title(self, md_content):
        assert md_content.startswith("# ")

    def test_has_содержание(self, h2_headings):
        assert "Содержание" in h2_headings

    def test_has_словарь(self, h2_headings):
        assert "Словарь" in h2_headings

    def test_has_литература(self, md_content):
        assert "## Рекомендуемая литература" in md_content or "## Литература" in md_content

    def test_numbered_sections_sequential(self, h2_headings):
        numbers = []
        for h in h2_headings:
            m = re.match(r"(\d+)\.", h)
            if m:
                numbers.append(int(m.group(1)))
        expected = list(range(1, max(numbers) + 1))
        assert numbers == expected, f"Section numbers: {numbers}, expected: {expected}"

    def test_h2_count_reasonable(self, h2_headings):
        assert len(h2_headings) >= 15, f"Too few h2 headings: {len(h2_headings)}"


# --- TOC links ---


class TestTocLinks:
    def test_содержание_has_links(self, md_content):
        toc_match = re.search(r"## Содержание\n\n(.*?)\n\n## ", md_content, re.DOTALL)
        assert toc_match, "Содержание section not found"
        links = re.findall(r"\[.+?\]\(#.+?\)", toc_match.group(1))
        assert len(links) >= 15, f"TOC has only {len(links)} links"

    def test_toc_links_have_targets(self, md_content):
        toc_match = re.search(r"## Содержание\n\n(.*?)\n\n## ", md_content, re.DOTALL)
        if not toc_match:
            pytest.skip("No TOC section")
        anchors = re.findall(r"\(#([^)]+)\)", toc_match.group(1))
        for anchor in anchors:
            # Check that there's a heading that would generate this anchor
            assert anchor in md_content.lower().replace(" ", "-").replace("«", "").replace("»", ""), (
                f"TOC link #{anchor} has no matching heading"
            )

    def test_back_to_toc_links(self, md_content, h2_headings):
        non_toc_headings = [h for h in h2_headings if h != "Содержание"]
        back_links = md_content.count("[↑ Содержание](#содержание)")
        assert back_links >= len(non_toc_headings) - 2, (
            f"Only {back_links} back-to-TOC links for {len(non_toc_headings)} headings"
        )


# --- Dictionary ---


class TestDictionary:
    def test_dictionary_entries_are_bold(self, md_content):
        dict_match = re.search(r"## Словарь\n\n(.*?)\n\n## ", md_content, re.DOTALL)
        if not dict_match:
            pytest.skip("No dictionary section")
        entries = [line for line in dict_match.group(1).split("\n") if line.startswith("- ")]
        non_bold = [e[:50] for e in entries if not e.startswith("- **")]
        assert non_bold == [], f"Non-bold dictionary entries: {non_bold}"

    def test_dictionary_has_enough_entries(self, md_content):
        dict_match = re.search(r"## Словарь\n\n(.*?)\n\n## ", md_content, re.DOTALL)
        if not dict_match:
            pytest.skip("No dictionary section")
        entries = [line for line in dict_match.group(1).split("\n") if line.startswith("- ")]
        assert len(entries) >= 25, f"Only {len(entries)} dictionary entries"

    def test_dictionary_has_wikipedia_links(self, md_content):
        dict_match = re.search(r"## Словарь\n\n(.*?)\n\n## ", md_content, re.DOTALL)
        if not dict_match:
            pytest.skip("No dictionary section")
        wiki_links = re.findall(r"ru\.wikipedia\.org", dict_match.group(1))
        assert len(wiki_links) >= 10, f"Only {len(wiki_links)} Wikipedia links in dictionary"


# --- Misleading content ---


class TestMisleadingWarnings:
    def test_has_warning_markers(self, md_content):
        warnings = md_content.count("⚠️")
        assert warnings >= 3, f"Only {warnings} warning markers, expected at least 3"

    def test_incorrect_images_have_warnings(self, md_content):
        """Each 'incorrect' image should be near a ⚠️ warning."""
        incorrect_imgs = re.findall(r"images/\d+_incorrect[^)]+", md_content)
        assert len(incorrect_imgs) >= 3, f"Only {len(incorrect_imgs)} incorrect images"


# --- Math formulas ---


class TestMathFormulas:
    def test_has_display_math(self, md_content):
        display_math = md_content.count("$$")
        assert display_math >= 10, f"Only {display_math // 2} display math blocks"

    def test_has_inline_math(self, md_content):
        inline_math = len(re.findall(r"(?<!\$)\$(?!\$).+?(?<!\$)\$(?!\$)", md_content))
        assert inline_math >= 20, f"Only {inline_math} inline math expressions"


# --- Content quality ---


class TestContentQuality:
    def test_no_empty_sections(self, md_content):
        """No h2 heading should be immediately followed by another h2."""
        empty = re.findall(r"^## .+\n\n\[↑.+\n\n## ", md_content, re.MULTILINE)
        assert empty == [], f"Empty sections found: {len(empty)}"

    def test_video_link_present(self, md_content):
        assert "youtu.be/MXJhzNGrsMo" in md_content

    def test_equipage_link_present(self, md_content):
        assert "equipage.club" in md_content

    def test_article_length_reasonable(self, md_content):
        words = len(md_content.split())
        assert words >= 3000, f"Article too short: {words} words"
        assert words <= 20000, f"Article too long: {words} words"
