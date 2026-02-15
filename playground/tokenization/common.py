from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Callable

TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?|[^\w\s]")
PUNCT_RE = re.compile(r"\w+|[^\w\s]")
DEFAULT_CHUNKS = Path("data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl")
REPO_ROOT = Path(__file__).resolve().parents[2]

Tokenizer = Callable[[str], list[str]]


def resolve_chunks_path(chunks_path: Path) -> Path:
    if chunks_path.is_absolute():
        return chunks_path
    cwd_candidate = (Path.cwd() / chunks_path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    return (REPO_ROOT / chunks_path).resolve()


def load_chunk_texts(chunks_path: Path) -> list[str]:
    texts: list[str] = []
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        texts.append(payload["text"])
    return texts


def whitespace_tokenize(text: str) -> list[str]:
    return [t for t in text.split() if t]


def regex_tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def simple_subword_tokenize(text: str, split_len: int = 6) -> list[str]:
    # Toy subword tokenizer for learning: split long alnum tokens into prefix + ##suffix chunks.
    out: list[str] = []
    for tok in regex_tokenize(text):
        if tok.isalnum() and len(tok) > split_len:
            out.append(tok[:split_len])
            rest = tok[split_len:]
            while rest:
                out.append(f"##{rest[:split_len]}")
                rest = rest[split_len:]
        else:
            out.append(tok)
    return out


def punct_tokenize(text: str) -> list[str]:
    return PUNCT_RE.findall(text)


def normalized_whitespace_tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text.lower())
    return [t for t in normalized.split() if t]


def char_tokenize(text: str, keep_space: bool = False) -> list[str]:
    if keep_space:
        return list(text)
    return [c for c in text if not c.isspace()]


def char_ngram_tokenize(text: str, n: int = 3) -> list[str]:
    normalized = text.replace(" ", "_")
    if len(normalized) < n:
        return [normalized] if normalized else []
    return [normalized[i : i + n] for i in range(len(normalized) - n + 1)]


def byte_tokenize(text: str) -> list[str]:
    return [f"b{b}" for b in text.encode("utf-8")]


def get_tokenizers() -> dict[str, Tokenizer]:
    return {
        "whitespace": whitespace_tokenize,
        "regex": regex_tokenize,
        "simple_subword": simple_subword_tokenize,
    }


def get_extended_tokenizers() -> dict[str, Tokenizer]:
    return {
        "whitespace": whitespace_tokenize,
        "regex": regex_tokenize,
        "simple_subword": simple_subword_tokenize,
        "punct_aware": punct_tokenize,
        "normalized_whitespace": normalized_whitespace_tokenize,
        "char_no_space": lambda text: char_tokenize(text, keep_space=False),
        "char_keep_space": lambda text: char_tokenize(text, keep_space=True),
        "char_3gram": lambda text: char_ngram_tokenize(text, n=3),
        "byte_level": byte_tokenize,
    }
