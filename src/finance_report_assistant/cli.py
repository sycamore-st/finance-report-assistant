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
from src.finance_report_assistant.retrieval.index import (
    build_retrieval_index,
    default_index_dir,
    load_retrieval_index,
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


@app.command("build-retrieval-index")
def build_retrieval(
    ticker: str = typer.Option(..., help="Ticker symbol, e.g., AAPL"),
    form: str = typer.Option("10-K", help="SEC form type"),
    limit: int = typer.Option(1, min=1, max=20, help="How many filings to include"),
    embedding_dim: int = typer.Option(384, min=64, max=2048, help="Dense hashing vector size"),
) -> None:
    """Build local retrieval index (BM25 + dense hash embeddings)."""
    out_dir, manifest = build_retrieval_index(
        ticker=ticker,
        form=form,
        limit=limit,
        embedding_dim=embedding_dim,
    )
    typer.echo(f"Built retrieval index: {out_dir}")
    typer.echo(json.dumps(manifest, indent=2))


@app.command("search")
def search(
    query: str = typer.Option(..., help="Natural-language question/query"),
    ticker: str = typer.Option(..., help="Ticker symbol, e.g., AAPL"),
    form: str = typer.Option("10-K", help="SEC form type"),
    top_k: int = typer.Option(5, min=1, max=20),
    bm25_weight: float = typer.Option(0.55, min=0.0, max=1.0),
    embedding_weight: float = typer.Option(0.45, min=0.0, max=1.0),
) -> None:
    """Run hybrid retrieval against local index and print citation-ready hits."""
    index_dir = default_index_dir(ticker=ticker, form=form)
    if not index_dir.exists():
        typer.echo(
            f"Index does not exist at {index_dir}. Run build-retrieval-index first."
        )
        raise typer.Exit(code=1)

    index = load_retrieval_index(index_dir)
    hits = index.search(
        query=query,
        top_k=top_k,
        bm25_weight=bm25_weight,
        embedding_weight=embedding_weight,
    )
    if not hits:
        typer.echo("No retrieval hits found.")
        raise typer.Exit(code=1)

    for hit in hits:
        row = {
            "rank": hit.rank,
            "score": round(hit.score, 6),
            "bm25_score": round(hit.bm25_score, 6),
            "embedding_score": round(hit.embedding_score, 6),
            "chunk_id": hit.record.get("chunk_id"),
            "ticker": hit.record.get("ticker"),
            "form": hit.record.get("form"),
            "accession_number": hit.record.get("accession_number"),
            "section_title": hit.record.get("section_title"),
            "citation_url": hit.record.get("citation_url"),
            "text": hit.record.get("text"),
        }
        typer.echo(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    app()
