from typer.testing import CliRunner

from finance_report_assistant.cli import app

runner = CliRunner()


def test_ingest_command_handles_no_results(monkeypatch) -> None:
    def _fake_ingest(*args, **kwargs):
        return []

    monkeypatch.setattr("finance_report_assistant.cli.ingest_filings_for_ticker", _fake_ingest)
    result = runner.invoke(app, ["ingest-10k", "--ticker", "AAPL", "--limit", "1"])

    assert result.exit_code == 1
    assert "No 10-K filings found" in result.stdout


def test_search_command_requires_index(tmp_path, monkeypatch) -> None:
    from finance_report_assistant.core.config import settings

    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    result = runner.invoke(
        app,
        ["search", "--query", "supply chain", "--ticker", "AAPL", "--form", "10-K"],
    )

    assert result.exit_code == 1
    assert "build-retrieval-index first" in result.stdout
