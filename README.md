# AW Client Portal API

Backend API for the AW Client Portal financial planning workflow application.

Built with:
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- WeasyPrint
- Jinja2

---

# Features

## Client Management
- Client CRUD
- Married/single household support
- Static financial profile persistence
- Account structure persistence
- Trust and liability persistence

## Quarterly Reporting
- Quarterly report persistence
- SACS calculations
- TCC calculations
- Validation workflows
- Combined report generation

## PDF Generation
- Combined SACS + TCC report PDFs
- Jinja2 templating
- WeasyPrint rendering
- File persistence and retrieval

## API Features
- Swagger/OpenAPI documentation
- CORS support
- Validation handling
- Seed/demo data support
- Consistent API responses

---

# Tech Stack

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- WeasyPrint
- Jinja2

---

# Project Structure

```txt
awclient-portal-api/
├── app/
│   ├── controllers/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── schemas/
│   ├── templates/
│   ├── utils/
│   ├── config/
│   └── main.py
├── reports/
├── scripts/
└── requirements.txt
```

---

# Local Development

## 1. Create virtual environment

```bash
python -m venv .venv
```

Activate:

### macOS/Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

---

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Run backend

```bash
uvicorn app.main:app --reload
```

Backend:

```txt
http://127.0.0.1:8000
```

Swagger docs:

```txt
http://127.0.0.1:8000/docs
```

---

# Database

Default database:
- SQLite

Database file is generated locally.

---

# Seed Demo Data

Generate fresh local demo data:

```http
POST /api/dev/reset-seed
```

This:
- clears existing demo data
- creates fresh single + married clients
- creates complete financial/account sample structures

---

# API Overview

## Health

```http
GET /health
```

## Clients

```http
GET    /api/clients
GET    /api/clients/{id}
POST   /api/clients
PUT    /api/clients/{id}
DELETE /api/clients/{id}
```

## Quarterly Reports

```http
GET  /api/reports
GET  /api/reports/{id}
GET  /api/reports/{id}/pdf
POST /api/reports/generate
```

---

# Report Calculation Rules

## SACS

```txt
Excess = Inflow - Outflow
```

```txt
Private Reserve Target =
(6 × monthly expenses) + insurance deductibles
```

---

## TCC

```txt
Client 1 Retirement Total =
sum(Client 1 retirement balances)
```

```txt
Client 2 Retirement Total =
sum(Client 2 retirement balances)
```

```txt
Non-Retirement Total =
sum(non-retirement balances excluding trust)
```

```txt
Grand Total Net Worth =
Client 1 Retirement
+ Client 2 Retirement
+ Non-Retirement
+ Trust Total
```

```txt
Liabilities Total =
sum(liabilities)
```

Important:
- liabilities are displayed separately
- liabilities are NOT subtracted from net worth

---

# PDF Generation

Generated reports:
- persist in the database
- generate combined SACS/TCC PDFs
- can be retrieved through:

```http
GET /api/reports/{id}/pdf
```

---

# Deployment

## Recommended

### Frontend
- Vercel

### Backend
- Railway

---

# Environment Variables

Recommended future variables:

```env
DATABASE_URL=
REPORT_OUTPUT_DIR=
ALLOWED_ORIGINS=
```

---

# Notes

- Backend is the source of truth for all report calculations.
- Frontend preview calculations are UX-only.
- Report validation occurs server-side before persistence/PDF generation.
- Canva editing integration is planned for a future release.

---

# License

Internal / Private Project
