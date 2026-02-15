from __future__ import annotations

import argparse
import json
import re
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


def percentile(sorted_vals: list[int], p: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = (len(sorted_vals) - 1) * p
    low = int(idx)
    high = min(low + 1, len(sorted_vals) - 1)
    frac = idx - low
    return sorted_vals[low] * (1 - frac) + sorted_vals[high] * frac


def summarize_lengths(lengths: list[int], budget: int) -> dict:
    vals = sorted(lengths)
    over = sum(1 for x in vals if x > budget)
    return {
        "chunks": len(vals),
        "avg": round(sum(vals) / len(vals), 2) if vals else 0,
        "min": vals[0] if vals else 0,
        "p50": round(percentile(vals, 0.50), 2),
        "p90": round(percentile(vals, 0.90), 2),
        "max": vals[-1] if vals else 0,
        "over_budget_count": over,
        "over_budget_ratio": round(over / len(vals), 4) if vals else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Show how tokenizer choice changes chunk token lengths")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--budget", type=int, default=220)
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

    report = {"chunks": str(chunks_path), "budget": args.budget, "tokenizers": []}
    for name, fn in tokenizers.items():
        lengths = [len(fn(t)) for t in texts]
        stats = summarize_lengths(lengths, args.budget)
        stats["tokenizer"] = name
        report["tokenizers"].append(stats)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
