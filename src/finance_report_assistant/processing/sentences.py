from __future__ import annotations

import re

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences_with_spans(text: str) -> list[dict[str, int | str]]:
    """Split text into sentence-like units with char spans relative to the input text."""
    out: list[dict[str, int | str]] = []
    if not text.strip():
        return out

    start = 0
    for match in SENTENCE_RE.finditer(text):
        end = match.start()
        raw = text[start:end]
        sentence = raw.strip()
        if sentence:
            lead_ws = len(raw) - len(raw.lstrip())
            sent_start = start + lead_ws
            sent_end = sent_start + len(sentence)
            out.append(
                {
                    "text": sentence,
                    "char_start": sent_start,
                    "char_end": sent_end,
                }
            )
        start = match.end()

    tail = text[start:]
    tail_sentence = tail.strip()
    if tail_sentence:
        lead_ws = len(tail) - len(tail.lstrip())
        sent_start = start + lead_ws
        sent_end = sent_start + len(tail_sentence)
        out.append(
            {
                "text": tail_sentence,
                "char_start": sent_start,
                "char_end": sent_end,
            }
        )

    return out
