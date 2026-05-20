AW Client Portal API

## Local Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If WeasyPrint fails to generate PDFs, install the native runtime dependencies required by WeasyPrint for your OS.

## Run Server

Run the API:

```bash
uvicorn app.main:app --reload
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Automated Smoke Test

With the API running locally:

```bash
python scripts/smoke_test.py
```

Against another host:

```bash
python scripts/smoke_test.py --base-url http://127.0.0.1:8000
```

The smoke test covers:

- health check
- demo seed endpoint
- clients list/create/get/update
- single-client validation and report generation
- married-client validation and report generation
- reports list
- generated PDF retrieval
- missing PDF 404 behavior

## Manual Smoke Checks

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Seed demo clients:

```bash
curl -X POST http://127.0.0.1:8000/api/dev/seed
```

Create a single client:

```bash
curl -X POST http://127.0.0.1:8000/api/clients \
  -H "Content-Type: application/json" \
  -d "{\"first_name\":\"Taylor\",\"middle_name\":\"A\",\"last_name\":\"Demo\",\"date_of_birth\":\"1985-04-12\",\"ssn_last_four\":\"1234\",\"email\":\"taylor.demo@example.com\",\"phone\":\"555-0199\",\"marital_status\":\"single\",\"client_1_monthly_salary_after_tax\":15000,\"client_1_monthly_expense_budget\":9000,\"private_reserve_target\":56000,\"insurance_deductible_total\":2000,\"retirement_accounts_json\":{\"IRA\":true,\"401K\":true},\"non_retirement_accounts_json\":{\"Brokerage\":true,\"Checking\":true},\"trust_details_json\":{\"has_trust\":false},\"liabilities_json\":{\"Mortgage\":true}}"
```

Create a married client:

```bash
curl -X POST http://127.0.0.1:8000/api/clients \
  -H "Content-Type: application/json" \
  -d "{\"first_name\":\"Avery\",\"last_name\":\"Demo\",\"date_of_birth\":\"1980-02-20\",\"ssn_last_four\":\"5678\",\"email\":\"avery.demo@example.com\",\"phone\":\"555-0188\",\"marital_status\":\"married\",\"spouse_first_name\":\"Jordan\",\"spouse_last_name\":\"Demo\",\"spouse_date_of_birth\":\"1982-08-18\",\"spouse_ssn_last_four\":\"2468\",\"spouse_email\":\"jordan.demo@example.com\",\"spouse_phone\":\"555-0189\",\"client_1_monthly_salary_after_tax\":15000,\"client_1_monthly_expense_budget\":9000,\"client_2_monthly_salary_after_tax\":8000,\"client_2_monthly_expense_budget\":5000,\"private_reserve_target\":87000,\"insurance_deductible_total\":3000,\"retirement_accounts_json\":{\"client_1\":[\"IRA\",\"401K\"],\"client_2\":[\"Roth IRA\",\"Pension\"]},\"non_retirement_accounts_json\":{\"Joint Brokerage\":true,\"Checking\":true,\"Savings\":true},\"trust_details_json\":{\"has_trust\":true,\"trust_name\":\"Demo Family Trust\"},\"liabilities_json\":{\"Mortgage\":true,\"Auto loan\":true}}"
```

List clients:

```bash
curl "http://127.0.0.1:8000/api/clients?page=1&limit=20"
```

Generate a combined quarterly report:

```bash
curl -X POST http://127.0.0.1:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d "{\"client_id\":1,\"quarter\":\"Q1\",\"is_married\":false,\"sacs\":{\"client_1_quarterly_inflow\":45000,\"client_1_quarterly_expense\":27000,\"insurance_deductible_total\":2000,\"private_reserve_balance\":10000},\"tcc\":{\"client_1_retirement_balances\":{\"IRA\":100000,\"401K\":250000},\"non_retirement_balances\":{\"Brokerage\":80000,\"Checking\":12000},\"trust_value\":500000,\"liability_balances\":{\"Mortgage\":300000}}}"
```

Generated report response:

```json
{
  "id": 1,
  "client_id": 1,
  "quarter": "Q1",
  "report_type": "combined",
  "status": "generated",
  "pdf_url": "/api/reports/1/pdf",
  "generated_at": "2026-05-20T12:00:00"
}
```

Fetch a generated PDF:

```bash
curl -L http://127.0.0.1:8000/api/reports/1/pdf --output combined_report_1.pdf
```

Missing PDF check:

```bash
curl -i http://127.0.0.1:8000/api/reports/999999/pdf
```

Expected result:

```json
{
  "detail": "Report PDF not found"
}
```
