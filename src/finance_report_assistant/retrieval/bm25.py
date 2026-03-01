from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+")

# Regex tokenization
def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


@dataclass
class BM25Index:
    doc_tokens: list[list[str]]
    idf: dict[str, float]
    avgdl: float
    k1: float = 1.5
    b: float = 0.75

    @classmethod
    def fit(cls, texts: Iterable[str], k1: float = 1.5, b: float = 0.75) -> "BM25Index":
        docs = [tokenize(t) for t in texts]
        n_docs = len(docs)
        avgdl = (sum(len(d) for d in docs) / n_docs) if n_docs else 0.0

        doc_freq: dict[str, int] = {}
        for doc in docs:
            for tok in set(doc):
                doc_freq[tok] = doc_freq.get(tok, 0) + 1

        # Robertson-Sparck Jones-style idf smoothing.
        idf: dict[str, float] = {}
        for tok, df in doc_freq.items():
            idf[tok] = math.log(1 + ((n_docs - df + 0.5) / (df + 0.5)))

        return cls(doc_tokens=docs, idf=idf, avgdl=avgdl, k1=k1, b=b)

    def scores(self, query: str) -> list[float]:
        q_tokens = tokenize(query)
        q_terms = list(dict.fromkeys(q_tokens))
        out = [0.0 for _ in self.doc_tokens]
        if not q_terms:
            return out

        for i, doc in enumerate(self.doc_tokens):
            if not doc:
                continue
            freqs: dict[str, int] = {}
            for tok in doc:
                freqs[tok] = freqs.get(tok, 0) + 1

            dl = len(doc)
            denom_norm = self.k1 * (1 - self.b + self.b * (dl / self.avgdl)) if self.avgdl else self.k1

            score = 0.0
            for term in q_terms:
                tf = freqs.get(term, 0)
                if tf == 0:
                    continue
                idf = self.idf.get(term, 0.0)
                numer = tf * (self.k1 + 1.0)
                denom = tf + denom_norm
                score += idf * (numer / denom)
            out[i] = score
        return out

