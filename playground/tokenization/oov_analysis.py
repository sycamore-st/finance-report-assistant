from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?|[^\w\s]")
DEFAULT_CHUNKS = Path("data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl")
REPO_ROOT = Path(__file__).resolve().parents[2]


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


def oov_ratio(train_tokens: list[str], test_tokens: list[str], min_freq: int) -> tuple[float, int, int]:
    freq = Counter(train_tokens)
    vocab = {tok for tok, c in freq.items() if c >= min_freq}
    if not test_tokens:
        return 0.0, 0, 0

    oov = sum(1 for tok in test_tokens if tok not in vocab)
    return oov / len(test_tokens), oov, len(test_tokens)


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure OOV behavior for multiple tokenizers")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--min-freq", type=int, default=2)
    args = parser.parse_args()

    chunks_path = resolve_chunks_path(args.chunks)
    if not chunks_path.exists():
        raise SystemExit(f"Chunks file not found: {chunks_path}")

    texts = load_chunk_texts(chunks_path)
    if len(texts) < 2:
        raise SystemExit("Need at least 2 chunks for train/test OOV analysis")

    split_idx = max(1, min(len(texts) - 1, int(len(texts) * args.train_ratio)))
    train_texts = texts[:split_idx]
    test_texts = texts[split_idx:]

    tokenizers = {
        "whitespace": whitespace_tokenize,
        "regex": regex_tokenize,
        "simple_subword": simple_subword_tokenize,
    }

    result = {
        "chunks": str(chunks_path),
        "train_chunks": len(train_texts),
        "test_chunks": len(test_texts),
        "train_ratio": args.train_ratio,
        "min_freq": args.min_freq,
        "tokenizers": [],
    }

    for name, fn in tokenizers.items():
        train_tokens = [tok.lower() for t in train_texts for tok in fn(t)]
        test_tokens = [tok.lower() for t in test_texts for tok in fn(t)]
        ratio, oov_count, total = oov_ratio(train_tokens, test_tokens, args.min_freq)

        result["tokenizers"].append(
            {
                "tokenizer": name,
                "train_tokens": len(train_tokens),
                "test_tokens": total,
                "oov_tokens": oov_count,
                "oov_ratio": round(ratio, 4),
            }
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
