from pathlib import Path

from typer.testing import CliRunner

from finance_report_assistant.cli import app

runner = CliRunner()


def test_eval_retrieval_requires_index(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("finance_report_assistant.cli.default_index_dir", lambda **kwargs: tmp_path / "missing")

    result = runner.invoke(
        app,
        ["eval-retrieval", "--ticker", "AAPL", "--form", "10-K"],
    )

    assert result.exit_code == 1
    assert "Run build-retrieval-index first" in result.stdout
