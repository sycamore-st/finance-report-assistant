from __future__ import annotations

import json
from pathlib import Path

import typer

from src.finance_report_assistant.ingestion.edgar_ingest import ingest_filings_for_ticker
from src.finance_report_assistant.processing.pipeline import build_chunks_for_ticker_form
from src.finance_report_assistant.processing.tokenizer_eval import (
    append_markdown_report,
    evaluate_tokenizer_metrics,
    load_chunk_texts,
)

app = typer.Typer(help="Finance Report Assistant CLI")


@app.callback()
def main() -> None:
    """Finance Report Assistant command group."""


@app.command("ingest-10k")
def ingest_10k(
    ticker: str = typer.Option(..., help="Ticker symbol, e.g., AAPL"),
    limit: int = typer.Option(1, min=1, max=10, help="How many recent matching filings to ingest"),
) -> None:
    """Ingest recent 10-K filing(s) for one ticker."""
    out_dirs = ingest_filings_for_ticker(ticker=ticker, form="10-K", limit=limit)
    if not out_dirs:
        typer.echo(f"No 10-K filings found for {ticker.upper()}")
        raise typer.Exit(code=1)

    typer.echo(f"Ingested {len(out_dirs)} filing(s) for {ticker.upper()}")
    for path in out_dirs:
        typer.echo(f"- {path}")


@app.command("build-chunks")
def build_chunks(
    ticker: str = typer.Option(..., help="Ticker symbol, e.g., AAPL"),
    form: str = typer.Option("10-K", help="SEC form type"),
    limit: int = typer.Option(1, min=1, max=20, help="How many filings to process"),
    max_words: int = typer.Option(220, min=50, max=1000, help="Chunk size in words"),
    overlap_words: int = typer.Option(40, min=0, max=300, help="Chunk overlap in words"),
    min_words: int = typer.Option(20, min=5, max=200, help="Minimum words kept per chunk"),
) -> None:
    """Build cleaned and chunked JSONL outputs from raw SEC filings."""
    out_files = build_chunks_for_ticker_form(
        ticker=ticker,
        form=form,
        max_words=max_words,
        overlap_words=overlap_words,
        min_words=min_words,
        limit=limit,
    )

    if not out_files:
        typer.echo(f"No raw filings found for {ticker.upper()} {form}")
        raise typer.Exit(code=1)

    typer.echo(f"Built chunks for {len(out_files)} filing(s)")
    for path in out_files:
        typer.echo(f"- {path}")


@app.command("eval-tokenizer")
def eval_tokenizer(
    chunks: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
    rare_threshold: int = typer.Option(2, min=1, max=10),
    output_md: Path = typer.Option(Path("docs/evaluation.md")),
) -> None:
    """Run tokenizer/OOV evaluation over chunk file and append Markdown report."""
    texts = load_chunk_texts(chunks)
    metrics = evaluate_tokenizer_metrics(texts, rare_threshold=rare_threshold)
    append_markdown_report(metrics, output_md, chunks)

    typer.echo(json.dumps(metrics, indent=2))
    typer.echo(f"Appended report to {output_md}")


if __name__ == "__main__":
    app()
