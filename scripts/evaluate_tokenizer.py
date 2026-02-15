from __future__ import annotations

import argparse
import json
from pathlib import Path

from finance_report_assistant.processing.tokenizer_eval import (
    append_markdown_report,
    evaluate_tokenizer_metrics,
    load_chunk_texts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate tokenizer/OOV stats for chunk files")
    parser.add_argument("--chunks", type=Path, required=True, help="Path to chunks.jsonl")
    parser.add_argument("--rare-threshold", type=int, default=2)
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("docs/evaluation.md"),
        help="Markdown file to append report",
    )
    args = parser.parse_args()

    texts = load_chunk_texts(args.chunks)
    metrics = evaluate_tokenizer_metrics(texts, rare_threshold=args.rare_threshold)
    append_markdown_report(metrics, args.output_md, args.chunks)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
