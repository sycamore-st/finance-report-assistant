from __future__ import annotations

import typer

from finance_report_assistant.ingestion.edgar_ingest import ingest_filings_for_ticker

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


if __name__ == "__main__":
    app()
