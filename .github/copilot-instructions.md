# GitHub Copilot Instructions — AW Client Portal API

This repository contains the backend API for the AW Client Portal system.

The backend follows a STRICT layered MVC-inspired architecture.

---

# Repository

awclient-portal-api/

---

# Architecture Rules

Layer order:

Routes → Controllers → Services → Models

This structure is STRICT and MUST NOT be bypassed.

---

# Routes Layer

Location:
app/routes/

Responsibilities:

- register API endpoints
- map HTTP methods
- inject dependencies

Rules:

- NO business logic
- NO calculations
- NO database queries
- NO PDF generation

---

# Controllers Layer

Location:
app/controllers/

Responsibilities:

- orchestrate request flow
- orchestrate response flow
- invoke services
- coordinate schemas

Rules:

- Controllers MUST remain thin
- Controllers MUST NOT query the database
- Controllers MUST NOT contain calculations
- Controllers MUST NOT generate PDFs
- Controllers MUST NOT contain SQLAlchemy logic

---

# Services Layer

Location:
app/services/

Responsibilities:

- ALL business logic
- ALL calculations
- ALL database interaction
- ALL PDF generation
- ALL data transformation

Rules:

- Services are the ONLY layer allowed to access models/database
- Services MUST NOT import FastAPI Request or Response
- Services MUST NOT return HTTP responses
- Services MUST remain reusable and modular

---

# Models Layer

Location:
app/models/

Responsibilities:

- SQLAlchemy ORM definitions only

Rules:

- NO business logic
- NO calculations
- NO validation logic

---

# Schemas Layer

Location:
app/schemas/

Responsibilities:

- request validation
- response serialization
- typed contracts

Rules:

- Use Pydantic only
- Separate Create / Update / Response schemas
- No database access

---

# Technology Stack

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Jinja2
- WeasyPrint

---

# Database Rules

- Use SQLAlchemy ORM only
- No raw SQL queries
- SQLite is the primary database
- JSON fields are acceptable where flexibility is needed

Examples:

- accounts_json
- liabilities_json
- accounts_snapshot_json

Avoid over-normalization.

---

# Calculation Rules

ALL financial calculations belong ONLY in:

app/services/calculation_service.py

Never calculate:

- in routes
- in controllers
- in templates

---

# PDF Rules

PDF generation belongs ONLY in:

app/services/pdf_service.py

Use:

- Jinja2 templates
- WeasyPrint

Do NOT:

- dynamically calculate SVG layouts
- use canvas rendering systems
- over-engineer PDF rendering

Use:

- CSS positioning
- fixed layouts
- stable visual rendering

---

# Current Modules

1. Clients
2. Monthly Logs
3. Reports

---

# API Design Rules

Use RESTful conventions.

Examples:

- GET /clients
- POST /clients
- PUT /clients/{id}
- GET /monthly-logs
- POST /reports/sacs/{id}

---

# Code Style Rules

- Use type hints everywhere
- Prefer small reusable functions
- Keep files modular
- Avoid files larger than 300 lines
- Prefer composition over inheritance
- Keep naming consistent
- Use dependency injection where appropriate

---

# Naming Rules

Use snake_case for:

- files
- variables
- functions

Use PascalCase for:

- classes

---

# Generation Constraints

When generating code:

- prioritize simplicity
- prioritize readability
- prioritize maintainability
- prioritize deterministic behavior

Avoid:

- unnecessary abstraction
- unnecessary utility layers
- premature optimization
- unnecessary generics

This is a lightweight deterministic financial reporting system.

---

# Preferred Backend Flow

Routes
→ Controllers
→ Services
→ Models
→ Database

Never bypass layers.

---

# Project Goal

The backend must support:

- client management
- monthly financial logs
- reliable calculations
- polished PDF generation

The API should optimize for:

- speed of implementation
- clean architecture
- visual report stability
- demo reliability
