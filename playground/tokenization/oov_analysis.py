from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from common import DEFAULT_CHUNKS, get_extended_tokenizers, load_chunk_texts, resolve_chunks_path


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

    tokenizers = get_extended_tokenizers()
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
