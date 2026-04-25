"""URL-verification gate for Phase 05.2 Plan 02 (revised).

Anti-pattern prevention: every external URL listed in the plan must be
verified to resolve (HTTP 200 or documented 4xx-with-explanation) BEFORE
any download task commits the URL as a provenance fact. See
.continue-here.md Critical Anti-Pattern #1 for the originating issue.

Module-level skip mark — this hits the live Ofgem CDN. Run manually
immediately before Task 4 (or use the one-shot inline script in the
plan's Task 1 Step 2).
"""
from __future__ import annotations

import pytest
import requests

pytestmark = pytest.mark.skip(reason="hits live website — run manually before download tasks (Plan 02 Task 1 gate)")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

URL_INVENTORY = [
    ("twelve-year-xlsx",
     "https://www.ofgem.gov.uk/sites/default/files/2025-05/rocs_report_2006_to_2018_20250410081520.xlsx"),
    ("public-reports-landing",
     "https://www.ofgem.gov.uk/renewables-obligation-ro/contacts-guidance-and-resources/public-reports-and-data-ro"),
    ("sy18-2019-20-xlsx",
     "https://www.ofgem.gov.uk/sites/default/files/docs/2021/03/ro_annual_report_data_2019-20.xlsx"),
    ("sy19-2020-21-xlsx",
     "https://www.ofgem.gov.uk/sites/default/files/2022-03/RO Annual Report 2020-21 - Dataset.xlsx"),
    ("sy20-2021-22-xlsx",
     "https://www.ofgem.gov.uk/sites/default/files/2023-03/Renewables Obligation Annual Report Scheme Year 20 Dataset.xlsx"),
    ("sy21-2022-23-xlsx",
     "https://www.ofgem.gov.uk/sites/default/files/2024-03/renewables_obligation_annual_report_sy21_dataset.xlsx"),
    ("sy22-2023-24-xlsx",
     "https://www.ofgem.gov.uk/sites/default/files/2025-03/Renewables-Obligation-(RO)-2023-to-2024-(SY22)-Annual-Report-Dataset.xlsx"),
    ("sy23-2024-25-xlsx",
     "https://www.ofgem.gov.uk/sites/default/files/2026-03/Renewables_Obligation_Annual_Report_Scheme_Year_23_Dataset-20260327121339.xlsx"),
]


@pytest.mark.parametrize("label,url", URL_INVENTORY, ids=[item[0] for item in URL_INVENTORY])
def test_url_resolves_200(label: str, url: str) -> None:
    """HEAD or 1-byte Range GET must report HTTP 200/206. Fail loud on any non-2xx."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=30, headers=HEADERS)
    except requests.exceptions.RequestException as e:
        pytest.fail(f"HEAD failed for {label} ({url}): {e!r}")
    if response.status_code in (405, 403):
        response = requests.get(
            url,
            headers={**HEADERS, "Range": "bytes=0-0"},
            allow_redirects=True,
            timeout=30,
        )
    assert response.status_code in (200, 206), (
        f"{label} returned HTTP {response.status_code} for {url}"
    )
