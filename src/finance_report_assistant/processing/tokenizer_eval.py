from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path


def load_chunk_texts(chunks_path: Path) -> list[str]:
    texts: list[str] = []
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        texts.append(row["text"])
    return texts


def whitespace_tokenize(text: str) -> list[str]:
    return [t for t in text.split() if t]


def evaluate_tokenizer_metrics(texts: list[str], rare_threshold: int = 2) -> dict:
    tokenized = [whitespace_tokenize(t) for t in texts]
    lengths = [len(tokens) for tokens in tokenized]
    all_tokens = [tok.lower() for row in tokenized for tok in row]
    freq = Counter(all_tokens)

    rare = sum(1 for tok in all_tokens if freq[tok] <= rare_threshold)
    total = len(all_tokens)

    return {
        "num_chunks": len(texts),
        "total_tokens": total,
        "avg_tokens_per_chunk": round((sum(lengths) / len(lengths)) if lengths else 0, 2),
        "min_tokens_per_chunk": min(lengths) if lengths else 0,
        "max_tokens_per_chunk": max(lengths) if lengths else 0,
        "unique_tokens": len(freq),
        "rare_token_ratio": round((rare / total) if total else 0.0, 4),
        "rare_threshold": rare_threshold,
    }


def append_markdown_report(metrics: dict, output_md: Path, source: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"\n## Tokenizer/OOV Eval - {timestamp}",
        f"- Source: `{source}`",
        f"- Chunks: {metrics['num_chunks']}",
        f"- Total tokens: {metrics['total_tokens']}",
        f"- Avg tokens/chunk: {metrics['avg_tokens_per_chunk']}",
        f"- Min tokens/chunk: {metrics['min_tokens_per_chunk']}",
        f"- Max tokens/chunk: {metrics['max_tokens_per_chunk']}",
        f"- Unique tokens: {metrics['unique_tokens']}",
        f"- Rare-token ratio (freq <= {metrics['rare_threshold']}): {metrics['rare_token_ratio']}",
    ]
    with output_md.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
