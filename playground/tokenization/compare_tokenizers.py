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
    rows = chunks_path.read_text(encoding="utf-8").splitlines()
    texts: list[str] = []
    for row in rows:
        if not row.strip():
            continue
        payload = json.loads(row)
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
                piece = rest[:split_len]
                out.append(f"##{piece}")
                rest = rest[split_len:]
        else:
            out.append(tok)
    return out


def summarize(name: str, tokenized: list[list[str]]) -> dict:
    all_tokens = [t.lower() for row in tokenized for t in row]
    lengths = [len(row) for row in tokenized]
    counts = Counter(all_tokens)
    return {
        "tokenizer": name,
        "num_chunks": len(tokenized),
        "total_tokens": len(all_tokens),
        "avg_tokens_per_chunk": round(sum(lengths) / len(lengths), 2) if lengths else 0.0,
        "unique_tokens": len(counts),
        "top_10_tokens": counts.most_common(10),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare tokenizer behaviors on chunked SEC text")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--sample-index", type=int, default=0)
    args = parser.parse_args()

    chunks_path = resolve_chunks_path(args.chunks)
    if not chunks_path.exists():
        raise SystemExit(f"Chunks file not found: {chunks_path}")

    texts = load_chunk_texts(chunks_path)
    if not texts:
        raise SystemExit("No chunk texts found")

    tokenizers = {
        "whitespace": whitespace_tokenize,
        "regex": regex_tokenize,
        "simple_subword": simple_subword_tokenize,
    }

    sample_idx = max(0, min(args.sample_index, len(texts) - 1))
    sample_text = texts[sample_idx]

    report = {"sample_index": sample_idx, "chunks": str(chunks_path), "tokenizers": []}
    for name, fn in tokenizers.items():
        tokenized = [fn(t) for t in texts]
        sample_tokens = fn(sample_text)[:40]
        stats = summarize(name, tokenized)
        stats["sample_tokens"] = sample_tokens
        report["tokenizers"].append(stats)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
