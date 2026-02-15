from __future__ import annotations

import argparse
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Callable

from common import (
    DEFAULT_CHUNKS,
    get_extended_tokenizers,
    load_chunk_texts,
    regex_tokenize,
    resolve_chunks_path,
)

Tokenizer = Callable[[str], list[str]]

NOTES = {
    "whitespace": ("Fast baseline", "Poor punctuation handling"),
    "regex": ("Stronger word boundary handling", "Language-specific heuristics"),
    "simple_subword": ("Lower OOV than word-level", "Toy method, not production-grade"),
    "punct_aware": ("Clean punctuation splitting", "Still brittle for multilingual text"),
    "normalized_whitespace": ("Unicode/case normalization", "Can lose case-sensitive signals"),
    "char_no_space": ("No OOV", "Very long sequences"),
    "char_keep_space": ("Preserves whitespace cues", "Longest sequences"),
    "char_3gram": ("Captures morphology/robustness", "Large token counts"),
    "byte_level": ("No OOV across languages", "Very long sequences, less interpretable"),
    "vocab_unk": ("Explicit OOV/UNK behavior", "Information loss on unknown terms"),
    "hf_bpe": ("Real subword segmentation", "Needs extra dependency and training step"),
}


def split_train_test(texts: list[str], train_ratio: float) -> tuple[list[str], list[str]]:
    split_idx = max(1, min(len(texts) - 1, int(len(texts) * train_ratio)))
    return texts[:split_idx], texts[split_idx:]


def oov_ratio(train_tokens: list[str], test_tokens: list[str], min_freq: int) -> tuple[float, int, int, int]:
    freq = Counter(train_tokens)
    vocab = {tok for tok, c in freq.items() if c >= min_freq}
    total = len(test_tokens)
    if total == 0:
        return 0.0, 0, 0, len(vocab)
    oov = sum(1 for tok in test_tokens if tok not in vocab)
    return oov / total, oov, total, len(vocab)


def build_vocab_unk_tokenizer(train_texts: list[str], min_freq: int) -> tuple[Tokenizer, set[str]]:
    train_tokens = [tok.lower() for text in train_texts for tok in regex_tokenize(text)]
    freq = Counter(train_tokens)
    vocab = {tok for tok, count in freq.items() if count >= min_freq}

    def _tokenizer(text: str) -> list[str]:
        tokens = [tok.lower() for tok in regex_tokenize(text)]
        return [tok if tok in vocab else "<unk>" for tok in tokens]

    return _tokenizer, vocab


def maybe_build_hf_bpe_tokenizer(train_texts: list[str], vocab_size: int) -> Tokenizer | None:
    try:
        from tokenizers import Tokenizer as HfTokenizer
        from tokenizers.models import BPE
        from tokenizers.pre_tokenizers import Whitespace
        from tokenizers.trainers import BpeTrainer
    except ImportError:
        return None

    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".txt") as handle:
        for text in train_texts:
            handle.write(text + "\n")
        train_file = handle.name

    tokenizer = HfTokenizer(BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = Whitespace()
    trainer = BpeTrainer(vocab_size=vocab_size, special_tokens=["<unk>"])
    tokenizer.train([train_file], trainer)

    def _tokenizer(text: str) -> list[str]:
        return tokenizer.encode(text).tokens

    return _tokenizer


def evaluate_tokenizer(
    name: str,
    tokenizer: Tokenizer,
    train_texts: list[str],
    test_texts: list[str],
    min_freq: int,
) -> dict:
    all_texts = train_texts + test_texts
    all_lengths = [len(tokenizer(t)) for t in all_texts]

    train_tokens = [tok.lower() for t in train_texts for tok in tokenizer(t)]
    test_tokens = [tok.lower() for t in test_texts for tok in tokenizer(t)]

    oov, oov_count, test_total, vocab_size = oov_ratio(train_tokens, test_tokens, min_freq=min_freq)
    strength, weakness = NOTES[name]

    return {
        "tokenizer": name,
        "oov_ratio": round(oov, 4),
        "avg_seq_len": round(sum(all_lengths) / len(all_lengths), 2) if all_lengths else 0.0,
        "vocab_size": vocab_size,
        "strength": strength,
        "weakness": weakness,
        "oov_tokens": oov_count,
        "test_tokens": test_total,
    }


def render_markdown_table(rows: list[dict]) -> str:
    lines = [
        "| Tokenizer | OOV | Avg Seq Len | Vocab Size | Strength | Weakness |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['tokenizer']} | {row['oov_ratio']:.4f} | {row['avg_seq_len']:.2f} | "
            f"{row['vocab_size']} | {row['strength']} | {row['weakness']} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare all tokenizer strategies on SEC chunks")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--min-freq", type=int, default=2)
    parser.add_argument("--bpe-vocab-size", type=int, default=5000)
    parser.add_argument("--output-md", type=Path, default=None)
    args = parser.parse_args()

    chunks_path = resolve_chunks_path(args.chunks)
    if not chunks_path.exists():
        raise SystemExit(f"Chunks file not found: {chunks_path}")

    texts = load_chunk_texts(chunks_path)
    if len(texts) < 2:
        raise SystemExit("Need at least 2 chunks for comparison")

    train_texts, test_texts = split_train_test(texts, args.train_ratio)

    tokenizers = get_extended_tokenizers()
    vocab_unk_tokenizer, _ = build_vocab_unk_tokenizer(train_texts, min_freq=args.min_freq)
    tokenizers["vocab_unk"] = vocab_unk_tokenizer

    hf_bpe = maybe_build_hf_bpe_tokenizer(train_texts, vocab_size=args.bpe_vocab_size)
    if hf_bpe is not None:
        tokenizers["hf_bpe"] = hf_bpe

    rows: list[dict] = []
    for name, tokenizer in tokenizers.items():
        rows.append(
            evaluate_tokenizer(
                name=name,
                tokenizer=tokenizer,
                train_texts=train_texts,
                test_texts=test_texts,
                min_freq=args.min_freq,
            )
        )

    table = render_markdown_table(rows)
    payload = {
        "chunks": str(chunks_path),
        "train_chunks": len(train_texts),
        "test_chunks": len(test_texts),
        "min_freq": args.min_freq,
        "hf_bpe_enabled": hf_bpe is not None,
        "matrix": rows,
        "markdown_table": table,
    }
    print(json.dumps(payload, indent=2))

    if args.output_md is not None:
        out_path = args.output_md
        if not out_path.is_absolute():
            out_path = (Path.cwd() / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(table + "\n", encoding="utf-8")
        print(f"\nWrote markdown table: {out_path}")


if __name__ == "__main__":
    main()