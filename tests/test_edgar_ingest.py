from finance_report_assistant.ingestion.edgar_ingest import _iter_recent_filings


def test_iter_recent_filings_filters_and_maps_fields() -> None:
    submissions = {
        "filings": {
            "recent": {
                "form": ["8-K", "10-K"],
                "accessionNumber": ["0001", "0002"],
                "filingDate": ["2024-01-01", "2024-10-31"],
                "reportDate": ["2023-12-31", "2024-09-30"],
                "primaryDocument": ["a.htm", "k10.htm"],
                "primaryDocDescription": ["Current report", "Annual report"],
            }
        }
    }

    rows = list(_iter_recent_filings(submissions, form="10-K"))

    assert len(rows) == 1
    row = rows[0]
    assert row["accession_number"] == "0002"
    assert row["filing_date"] == "2024-10-31"
    assert row["report_date"] == "2024-09-30"
    assert row["primary_document"] == "k10.htm"
    assert row["primary_doc_description"] == "Annual report"
