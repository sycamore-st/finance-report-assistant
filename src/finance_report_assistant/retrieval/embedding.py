from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+")


def _feature_stream(text: str) -> list[str]:
    tokens = TOKEN_RE.findall(text.lower())
    if not tokens:
        return []

    features: list[str] = []
    for tok in tokens:
        features.append(f"w:{tok}")
        if len(tok) >= 4:
            for i in range(len(tok) - 2):
                features.append(f"c3:{tok[i:i+3]}")

    for i in range(len(tokens) - 1):
        features.append(f"bg:{tokens[i]}_{tokens[i + 1]}")
    return features


def _hash_feature(feature: str, dim: int) -> tuple[int, float]:
    h = hashlib.sha1(feature.encode("utf-8")).digest()
    idx = int.from_bytes(h[:4], "big") % dim
    sign = 1.0 if (h[4] & 1) else -1.0
    return idx, sign


def _normalize(vec: dict[int, float]) -> dict[int, float]:
    norm = math.sqrt(sum(v * v for v in vec.values()))
    if norm == 0:
        return {}
    return {k: v / norm for k, v in vec.items()}


def _encode_sparse(text: str, dim: int) -> dict[int, float]:
    vec: dict[int, float] = {}
    for feature in _feature_stream(text):
        idx, sign = _hash_feature(feature, dim=dim)
        vec[idx] = vec.get(idx, 0.0) + sign
    return _normalize(vec)


def _sparse_dot(a: dict[int, float], b: dict[int, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(val * b.get(idx, 0.0) for idx, val in a.items())


@dataclass
class HashEmbeddingIndex:
    dim: int
    doc_vectors: list[dict[int, float]]

    @classmethod
    def fit(cls, texts: Iterable[str], dim: int = 384) -> "HashEmbeddingIndex":
        vectors = [_encode_sparse(text, dim=dim) for text in texts]
        return cls(dim=dim, doc_vectors=vectors)

    def scores(self, query: str) -> list[float]:
        q = _encode_sparse(query, dim=self.dim)
        if not q:
            return [0.0 for _ in self.doc_vectors]
        return [_sparse_dot(q, dv) for dv in self.doc_vectors]

