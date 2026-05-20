AW Client Portal API

## Local Smoke Checks

Run the API:

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Seed demo clients:

```bash
curl -X POST http://127.0.0.1:8000/api/dev/seed
```

Create a client:

```bash
curl -X POST http://127.0.0.1:8000/api/clients \
  -H "Content-Type: application/json" \
  -d "{\"first_name\":\"Taylor\",\"last_name\":\"Demo\",\"email\":\"taylor.demo@example.com\",\"phone\":\"555-0199\"}"
```

List clients:

```bash
curl "http://127.0.0.1:8000/api/clients?page=1&limit=20"
```

Generate a combined quarterly report:

```bash
curl -X POST http://127.0.0.1:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d "{\"client_id\":1,\"quarter\":\"Q1\",\"is_married\":false,\"sacs\":{\"client_1_quarterly_inflow\":45000,\"client_1_quarterly_outflow\":27000,\"insurance_deductible_total\":2000,\"private_reserve_balance\":10000},\"tcc\":{\"client_1_retirement_balances\":{\"IRA\":100000,\"401K\":250000},\"non_retirement_balances\":{\"Brokerage\":80000,\"Checking\":12000},\"trust_property_value\":500000,\"liabilities\":{\"Mortgage\":300000}}}"
```

Fetch a generated PDF:

```bash
curl -L http://127.0.0.1:8000/api/reports/1/pdf --output combined_report_1.pdf
```
