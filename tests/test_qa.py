from finance_report_assistant.qa.grounded_qa import compose_grounded_answer
from finance_report_assistant.retrieval.hybrid import RetrievalHit


def test_compose_grounded_answer_returns_answer_and_citations() -> None:
    hits = [
        RetrievalHit(
            rank=1,
            score=1.0,
            bm25_score=2.0,
            embedding_score=0.2,
            record={
                "chunk_id": "c1",
                "citation_url": "https://sec.gov/c1",
                "section_title": "Risk Factors",
                "accession_number": "0001",
                "text": "Supply chain disruptions could impact margins. Demand remains strong.",
            },
        )
    ]

    result = compose_grounded_answer("What risks are mentioned?", hits)

    assert result.answer
    assert "Supply chain" in result.answer
    assert len(result.citations) == 1
    assert result.citations[0].chunk_id == "c1"
