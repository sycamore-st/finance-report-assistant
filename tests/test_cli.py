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
