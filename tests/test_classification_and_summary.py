from finance_report_assistant.classification.themes import classify_themes
from finance_report_assistant.summarization.extractive import summarize_text


def test_classify_themes_detects_liquidity_and_growth_terms() -> None:
    text = "Cash flow and liquidity improved while growth in market demand increased."
    themes = classify_themes(text)

    by_theme = {t.theme: t for t in themes}
    assert by_theme["liquidity"].hits > 0
    assert by_theme["growth"].hits > 0


def test_summarize_text_returns_nonempty_extract() -> None:
    text = (
        "Revenue increased due to services growth. "
        "Cash flow remained strong across regions. "
        "Risk factors include supply constraints and litigation exposure."
    )
    summary = summarize_text(text, max_sentences=2)

    assert summary
    assert "." in summary
