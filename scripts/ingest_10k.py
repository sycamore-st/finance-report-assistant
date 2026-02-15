from src.finance_report_assistant.ingestion.edgar_ingest import ingest_filings_for_ticker


if __name__ == "__main__":
    paths = ingest_filings_for_ticker(ticker="AAPL", form="10-K", limit=1)
    for p in paths:
        print(p)
