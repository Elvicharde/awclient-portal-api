import argparse
import json
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JsonValue = dict[str, Any] | list[Any] | str | int | float | bool | None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AW Client Portal API smoke checks.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL")
    args = parser.parse_args()

    runner = SmokeRunner(args.base_url.rstrip("/"))

    try:
        runner.run()
    except SmokeFailure as exc:
        print(f"FAIL: {exc}")
        return 1
    except URLError as exc:
        print(f"FAIL: Unable to reach API: {exc.reason}")
        return 1

    print("PASS: smoke checks completed")
    return 0


class SmokeFailure(Exception):
    pass


class SmokeRunner:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.created_single_client_id: int | None = None
        self.created_married_client_id: int | None = None
        self.generated_report_id: int | None = None

    def run(self) -> None:
        self._check_health()
        self._seed_demo_data()
        self._list_clients()
        self._validate_married_client_failure()
        self._create_single_client()
        self._get_single_client()
        self._update_single_client()
        self._generate_single_report()
        self._create_married_client()
        self._generate_married_report()
        self._list_reports()
        self._fetch_pdf()
        self._verify_missing_pdf_returns_404()

    def _check_health(self) -> None:
        response = self._request("GET", "/health")
        self._assert(response == {"status": "ok"}, "Health check did not return status ok")

    def _seed_demo_data(self) -> None:
        self._request("POST", "/api/dev/seed")

    def _list_clients(self) -> None:
        response = self._request("GET", "/api/clients?page=1&limit=20")
        self._assert("items" in response and "total" in response, "Client list response shape is invalid")

    def _validate_married_client_failure(self) -> None:
        payload = {
            "first_name": "Invalid",
            "last_name": "Married",
            "date_of_birth": "1980-01-01",
            "ssn_last_four": "1111",
            "email": f"invalid.married.{_timestamp()}@example.com",
            "marital_status": "married",
            "client_1_monthly_salary_after_tax": 10000,
            "client_1_monthly_expense_budget": 7000,
        }
        self._request_expect_status("POST", "/api/clients", 400, payload)

    def _create_single_client(self) -> None:
        payload = {
            "first_name": "Smoke",
            "middle_name": "Single",
            "last_name": "Client",
            "date_of_birth": "1985-04-12",
            "ssn_last_four": "1234",
            "email": f"smoke.single.{_timestamp()}@example.com",
            "phone": "555-1001",
            "marital_status": "single",
            "client_1_monthly_salary_after_tax": 15000,
            "client_1_monthly_expense_budget": 9000,
            "private_reserve_target": 56000,
            "insurance_deductible_total": 2000,
            "retirement_accounts_json": {"IRA": True, "401K": True},
            "non_retirement_accounts_json": {"Brokerage": True, "Checking": True},
            "trust_details_json": {"has_trust": False},
            "liabilities_json": {"Mortgage": True},
        }
        response = self._request("POST", "/api/clients", payload)
        self.created_single_client_id = _require_int(response, "id")
        self._assert(response.get("marital_status") == "single", "Single client marital status was not preserved")
        self._assert(response.get("client_2_monthly_salary_after_tax") is None, "Single client retained Client 2 salary")

    def _get_single_client(self) -> None:
        client_id = self._require_single_client_id()
        response = self._request("GET", f"/api/clients/{client_id}")
        self._assert(response.get("id") == client_id, "GET client returned the wrong client")

    def _update_single_client(self) -> None:
        client_id = self._require_single_client_id()
        response = self._request("PUT", f"/api/clients/{client_id}", {"phone": "555-1999"})
        self._assert(response.get("phone") == "555-1999", "PUT client did not update phone")

    def _generate_single_report(self) -> None:
        client_id = self._require_single_client_id()
        payload = {
            "client_id": client_id,
            "quarter": "Q1",
            "is_married": False,
            "sacs": {
                "client_1_quarterly_inflow": 45000,
                "client_1_quarterly_expense": 27000,
                "insurance_deductible_total": 2000,
                "private_reserve_balance": 10000,
            },
            "tcc": {
                "client_1_retirement_balances": {"IRA": 100000, "401K": 250000},
                "non_retirement_balances": {"Brokerage": 80000, "Checking": 12000},
                "trust_value": 500000,
                "liability_balances": {"Mortgage": 300000},
            },
        }
        response = self._request("POST", "/api/reports/generate", payload)
        self.generated_report_id = _require_int(response, "id")
        self._assert(response.get("status") == "generated", "Single report was not generated")
        self._assert(response.get("pdf_url") == f"/api/reports/{self.generated_report_id}/pdf", "Single report pdf_url is invalid")
        totals = response.get("calculated_totals_json", {})
        tcc_totals = totals.get("tcc", {}) if isinstance(totals, dict) else {}
        self._assert(tcc_totals.get("client_2_retirement_total") == 0, "Single report Client 2 retirement total was not zero")

    def _create_married_client(self) -> None:
        payload = {
            "first_name": "Smoke",
            "last_name": "Married",
            "date_of_birth": "1980-02-20",
            "ssn_last_four": "5678",
            "email": f"smoke.married.{_timestamp()}@example.com",
            "phone": "555-2001",
            "marital_status": "married",
            "spouse_first_name": "Jordan",
            "spouse_last_name": "Married",
            "spouse_date_of_birth": "1982-08-18",
            "spouse_ssn_last_four": "2468",
            "spouse_email": f"smoke.spouse.{_timestamp()}@example.com",
            "spouse_phone": "555-2002",
            "client_1_monthly_salary_after_tax": 15000,
            "client_1_monthly_expense_budget": 9000,
            "client_2_monthly_salary_after_tax": 8000,
            "client_2_monthly_expense_budget": 5000,
            "private_reserve_target": 87000,
            "insurance_deductible_total": 3000,
        }
        response = self._request("POST", "/api/clients", payload)
        self.created_married_client_id = _require_int(response, "id")
        self._assert(response.get("marital_status") == "married", "Married client marital status was not preserved")

    def _generate_married_report(self) -> None:
        client_id = self._require_married_client_id()
        payload = {
            "client_id": client_id,
            "quarter": "Q2",
            "is_married": True,
            "spouse_name": "Jordan Married",
            "sacs": {
                "client_1_quarterly_inflow": 45000,
                "client_1_quarterly_expense": 27000,
                "client_2_quarterly_inflow": 24000,
                "client_2_quarterly_expense": 15000,
                "insurance_deductible_total": 3000,
                "private_reserve_balance": 20000,
            },
            "tcc": {
                "client_1_retirement_balances": {"IRA": 100000, "401K": 250000},
                "client_2_retirement_balances": {"Roth IRA": 75000, "Pension": 125000},
                "non_retirement_balances": {"Joint Brokerage": 120000, "Checking": 18000},
                "trust_value": 600000,
                "liability_balances": {"Mortgage": 350000, "Auto loan": 22000},
            },
        }
        response = self._request("POST", "/api/reports/generate", payload)
        totals = response.get("calculated_totals_json", {})
        sacs_totals = totals.get("sacs", {}) if isinstance(totals, dict) else {}
        tcc_totals = totals.get("tcc", {}) if isinstance(totals, dict) else {}
        self._assert(sacs_totals.get("total_inflow") == 69000, "Married SACS inflow total is incorrect")
        self._assert(sacs_totals.get("total_outflow") == 42000, "Married SACS outflow total is incorrect")
        self._assert(tcc_totals.get("client_1_retirement_total") == 350000, "Client 1 retirement total is incorrect")
        self._assert(tcc_totals.get("client_2_retirement_total") == 200000, "Client 2 retirement total is incorrect")
        self._assert(tcc_totals.get("grand_total_net_worth") == 1288000, "Grand total net worth is incorrect")

    def _list_reports(self) -> None:
        response = self._request("GET", "/api/reports")
        self._assert("items" in response and "total" in response, "Report list response shape is invalid")

    def _fetch_pdf(self) -> None:
        report_id = self._require_generated_report_id()
        body, headers, status = self._raw_request("GET", f"/api/reports/{report_id}/pdf")
        content_type = headers.get("Content-Type", "")
        self._assert(status == 200, "PDF endpoint did not return 200")
        self._assert("application/pdf" in content_type, "PDF endpoint did not return application/pdf")
        self._assert(body.startswith(b"%PDF"), "PDF response does not look like a PDF")

    def _verify_missing_pdf_returns_404(self) -> None:
        self._request_expect_status("GET", "/api/reports/999999/pdf", 404)

    def _request(self, method: str, path: str, payload: JsonValue = None) -> JsonValue:
        body, _, status = self._raw_request(method, path, payload)
        self._assert(200 <= status < 300, f"{method} {path} returned {status}")

        if not body:
            return None

        return json.loads(body.decode("utf-8"))

    def _request_expect_status(
        self,
        method: str,
        path: str,
        expected_status: int,
        payload: JsonValue = None,
    ) -> JsonValue:
        body, _, status = self._raw_request(method, path, payload, allow_error=True)
        self._assert(status == expected_status, f"{method} {path} returned {status}, expected {expected_status}")

        if not body:
            return None

        return json.loads(body.decode("utf-8"))

    def _raw_request(
        self,
        method: str,
        path: str,
        payload: JsonValue = None,
        allow_error: bool = False,
    ) -> tuple[bytes, dict[str, str], int]:
        data = None
        headers = {"Accept": "application/json"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)

        try:
            with urlopen(request, timeout=30) as response:
                return response.read(), dict(response.headers.items()), response.status
        except HTTPError as exc:
            if allow_error:
                return exc.read(), dict(exc.headers.items()), exc.code
            detail = exc.read().decode("utf-8", errors="replace")
            raise SmokeFailure(f"{method} {path} returned {exc.code}: {detail}") from exc

    def _require_single_client_id(self) -> int:
        self._assert(self.created_single_client_id is not None, "Single client was not created")
        return self.created_single_client_id

    def _require_married_client_id(self) -> int:
        self._assert(self.created_married_client_id is not None, "Married client was not created")
        return self.created_married_client_id

    def _require_generated_report_id(self) -> int:
        self._assert(self.generated_report_id is not None, "Report was not generated")
        return self.generated_report_id

    def _assert(self, condition: bool, message: str) -> None:
        if not condition:
            raise SmokeFailure(message)


def _timestamp() -> int:
    return int(time.time() * 1000)


def _require_int(data: JsonValue, key: str) -> int:
    if not isinstance(data, dict) or not isinstance(data.get(key), int):
        raise SmokeFailure(f"Response is missing integer field: {key}")
    return data[key]


if __name__ == "__main__":
    sys.exit(main())
