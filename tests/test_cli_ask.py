from pathlib import Path

from typer.testing import CliRunner

from finance_report_assistant.cli import app
from finance_report_assistant.retrieval.hybrid import RetrievalHit

runner = CliRunner()


def test_ask_outputs_answer_json(monkeypatch, tmp_path: Path) -> None:
    class _FakeIndex:
        def search(self, query: str, top_k: int = 5):
            return [
                RetrievalHit(
                    rank=1,
                    score=1.0,
                    bm25_score=1.0,
                    embedding_score=1.0,
                    record={
                        "chunk_id": "c1",
                        "citation_url": "https://sec.gov/c1",
                        "section_title": "Risk Factors",
                        "accession_number": "0001",
                        "text": "Supply chain disruptions are a risk factor. Liquidity remains strong.",
                    },
                )
            ]

    monkeypatch.setattr("finance_report_assistant.cli.default_index_dir", lambda **kwargs: tmp_path)
    monkeypatch.setattr("finance_report_assistant.cli.load_retrieval_index", lambda p: _FakeIndex())
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        ["ask", "--ticker", "AAPL", "--form", "10-K", "--question", "What risks are disclosed?"],
    )

    assert result.exit_code == 0
    assert '"answer"' in result.stdout
    assert '"citations"' in result.stdout
