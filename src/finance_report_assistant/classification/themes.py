from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN_RE = re.compile(r"[a-z0-9]+")

THEME_KEYWORDS: dict[str, set[str]] = {
    "risk": {"risk", "uncertain", "volatility", "exposure", "disruption", "litigation", "adverse"},
    "growth": {"growth", "expand", "increase", "innovation", "ai", "demand", "market"},
    "liquidity": {"cash", "liquidity", "debt", "capital", "financing", "credit", "flow"},
    "guidance": {"guidance", "outlook", "expect", "forecast", "project", "plan", "target"},
}


@dataclass
class ThemeScore:
    theme: str
    score: float
    hits: int


def classify_themes(text: str) -> list[ThemeScore]:
    terms = TOKEN_RE.findall(text.lower())
    if not terms:
        return [ThemeScore(theme=k, score=0.0, hits=0) for k in THEME_KEYWORDS]

    out: list[ThemeScore] = []
    total = len(terms)
    for theme, keywords in THEME_KEYWORDS.items():
        hits = sum(1 for t in terms if t in keywords)
        score = hits / total
        out.append(ThemeScore(theme=theme, score=score, hits=hits))

    return sorted(out, key=lambda x: x.score, reverse=True)
