from finance_report_assistant.processing.chunker import build_chunk_candidates
from finance_report_assistant.processing.html_cleaner import extract_sections_from_html


def test_extract_sections_from_html_reads_headings_and_text() -> None:
    html = """
    <html><body>
      <h1>Item 1. Business</h1>
      <p>Apple designs, manufactures and markets smartphones.</p>
      <h2>Products</h2>
      <p>iPhone, Mac, iPad and services.</p>
    </body></html>
    """

    sections = extract_sections_from_html(html)

    assert len(sections) >= 2
    assert sections[0].title == "Item 1. Business"
    assert "Apple designs" in sections[0].text
    assert any(s.title == "Products" for s in sections)


def test_extract_sections_detects_item_heading_in_div() -> None:
    html = """
    <html><body>
      <div>Item 1A. Risk Factors</div>
      <div>Our business could be harmed by supply constraints.</div>
    </body></html>
    """
    sections = extract_sections_from_html(html)

    assert sections
    assert sections[0].title.lower().startswith("item 1a")
    assert "supply constraints" in sections[0].text.lower()


def test_build_chunk_candidates_with_overlap() -> None:
    html = "<html><body><h1>Overview</h1><p>" + " ".join([f"w{i}" for i in range(30)]) + "</p></body></html>"
    sections = extract_sections_from_html(html)

    chunks = build_chunk_candidates(sections, max_words=10, overlap_words=2, min_words=1)

    assert len(chunks) >= 3
    assert chunks[0].text.split()[-2:] == chunks[1].text.split()[:2]


def test_extract_sections_splits_document_on_item_pattern() -> None:
    html = """
    <html><body>
      <p>Intro text. Item 1. Business We build products. Item 1A. Risk Factors Supply chain risks.</p>
    </body></html>
    """
    sections = extract_sections_from_html(html)
    titles = [s.title for s in sections]

    assert any(t.lower().startswith("item 1.") for t in titles)
    assert any(t.lower().startswith("item 1a.") for t in titles)
