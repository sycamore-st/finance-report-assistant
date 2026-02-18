from finance_report_assistant.processing.sentences import split_sentences_with_spans


def test_split_sentences_with_spans_returns_units_and_offsets() -> None:
    text = "Alpha risk is rising. Liquidity remains strong!"
    spans = split_sentences_with_spans(text)

    assert len(spans) == 2
    assert spans[0]["text"] == "Alpha risk is rising."
    assert spans[1]["text"] == "Liquidity remains strong!"
    assert spans[0]["char_start"] == 0
    assert spans[1]["char_start"] > spans[0]["char_end"]
