from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import DEFAULT_CHUNKS, get_extended_tokenizers, load_chunk_texts, resolve_chunks_path


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

    tokenizers = get_extended_tokenizers()
    report = {"chunks": str(chunks_path), "budget": args.budget, "tokenizers": []}

    for name, fn in tokenizers.items():
        lengths = [len(fn(t)) for t in texts]
        stats = summarize_lengths(lengths, args.budget)
        stats["tokenizer"] = name
        report["tokenizers"].append(stats)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
