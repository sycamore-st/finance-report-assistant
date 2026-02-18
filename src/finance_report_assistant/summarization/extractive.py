from __future__ import annotations

import re
from collections import Counter

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
TOKEN_RE = re.compile(r"[a-z0-9]+")


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]


def summarize_text(text: str, max_sentences: int = 3) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return ""
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    words = TOKEN_RE.findall(text.lower())
    freqs = Counter(words)

    scored: list[tuple[float, int, str]] = []
    for idx, sentence in enumerate(sentences):
        tokens = TOKEN_RE.findall(sentence.lower())
        if not tokens:
            continue
        score = sum(freqs[t] for t in tokens) / len(tokens)
        # small position bias for earlier sentences
        score += max(0.0, 0.2 - (idx * 0.01))
        scored.append((score, idx, sentence))

    top = sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences]
    ordered = [s for _, _, s in sorted(top, key=lambda x: x[1])]
    return " ".join(ordered)


def summarize_chunks(records: list[dict], max_sentences: int = 5) -> str:
    merged = " ".join(r.get("text", "") for r in records if r.get("text"))
    return summarize_text(merged, max_sentences=max_sentences)
