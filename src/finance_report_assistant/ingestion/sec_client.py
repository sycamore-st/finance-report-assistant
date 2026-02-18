from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from finance_report_assistant.core.config import settings

SEC_DATA_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"


class SecEdgarClient:
    def __init__(self, user_agent: str | None = None, timeout_s: float = 30.0) -> None:
        self.user_agent = user_agent or settings.sec_user_agent
        self._client = httpx.Client(
            timeout=timeout_s,
            headers={
                "User-Agent": self.user_agent,
                "Accept-Encoding": "gzip, deflate",
                "Host": "data.sec.gov",
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SecEdgarClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    @retry(wait=wait_exponential(min=1, max=16), stop=stop_after_attempt(3), reraise=True)
    def get_submissions(self, cik: str) -> dict[str, Any]:
        url = SEC_DATA_SUBMISSIONS_URL.format(cik=cik.zfill(10))
        resp = self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(min=1, max=16), stop=stop_after_attempt(3), reraise=True)
    def get_archive_document(self, cik: str, accession_number: str, primary_document: str) -> str:
        cik_int = str(int(cik))
        accession_no_dashes = accession_number.replace("-", "")
        url = f"{SEC_ARCHIVES_BASE}/{cik_int}/{accession_no_dashes}/{primary_document}"

        # SEC archive host should be requested from sec.gov
        with httpx.Client(
            timeout=30.0,
            headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"},
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
