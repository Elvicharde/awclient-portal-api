# AW Client Portal API — Architecture Guide

## Overview

The AW Client Portal API powers the financial reporting portal responsible for:

- client profile management
- monthly financial logs
- financial calculations
- PDF report generation

This backend is intentionally optimized for:

- rapid implementation
- deterministic business logic
- clean modular architecture
- maintainability
- lightweight infrastructure
- demo reliability

The API follows a strict layered MVC-inspired architecture.

---

# Repository Structure

awclient-portal-api/
└── app/
├── main.py
│
├── config/
│ ├── database.py
│ └── settings.py
│
├── models/
│ ├── client_model.py
│ ├── log_model.py
│ └── report_model.py
│
├── schemas/
│ ├── client_schema.py
│ ├── log_schema.py
│ └── report_schema.py
│
├── services/
│ ├── client_service.py
│ ├── log_service.py
│ ├── calculation_service.py
│ └── pdf_service.py
│
├── controllers/
│ ├── client_controller.py
│ ├── log_controller.py
│ └── report_controller.py
│
├── routes/
│ ├── client_routes.py
│ ├── log_routes.py
│ └── report_routes.py
│
├── templates/
│ ├── sacs_report.html
│ └── tcc_report.html
│
└── utils/
├── formatter.py
└── helpers.py

---

# Architecture Philosophy

This backend prioritizes:

- simplicity
- separation of concerns
- deterministic behavior
- stable PDF generation
- maintainable services

This is NOT intended to be:

- heavily abstracted
- microservice-oriented
- event-driven
- enterprise-complex

The application is intentionally lightweight.

---

# Layer Order

Routes → Controllers → Services → Models

This order is STRICT.

---

# Layer Responsibilities

## Routes Layer

Responsibilities:

- define API endpoints
- register routers
- inject dependencies

Rules:

- NO business logic
- NO calculations
- NO database access

---

## Controllers Layer

Responsibilities:

- coordinate request flow
- coordinate response flow
- invoke services
- orchestrate schemas

Rules:

- MUST remain thin
- MUST NOT directly query the database
- MUST NOT contain calculations
- MUST NOT generate PDFs

---

## Services Layer

Responsibilities:

- ALL business logic
- ALL calculations
- ALL database access
- ALL PDF generation
- ALL data transformations

Rules:

- Services are the core application layer
- Services MUST remain modular
- Services MUST NOT return HTTP responses
- Services MUST NOT import FastAPI Request/Response classes

---

## Models Layer

Responsibilities:

- define SQLAlchemy entities
- define relationships
- define table structures

Rules:

- NO business logic
- NO calculations
- NO validation logic

---

## Schemas Layer

Responsibilities:

- request validation
- response serialization
- typed contracts

Rules:

- Use Pydantic only
- Separate Create / Update / Response schemas
- No database logic

---

# Technology Stack

## Backend

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Jinja2
- WeasyPrint

## Deployment

- Railway

---

# Database Philosophy

SQLite is intentionally used for V1.

Reason:

- very small dataset
- low concurrency
- rapid setup
- deployment simplicity

JSON fields are acceptable where flexibility is needed.

Examples:

- accounts_json
- liabilities_json
- accounts_snapshot_json

Avoid over-normalization.

---

# Core Modules

## Clients Module

Handles:

- client profiles
- static financial information
- account structures

---

## Monthly Logs Module

Handles:

- recurring financial entries
- account snapshots
- liabilities snapshots
- monthly balances

---

## Reports Module

Handles:

- SACS PDF generation
- TCC PDF generation
- report persistence
- report history

---

# Calculation Rules

ALL calculations belong ONLY in:

services/calculation_service.py

Never calculate:

- in routes
- in controllers
- in templates

---

# PDF Strategy

Reports are generated using:

HTML Templates → WeasyPrint → PDF

Reason:

- fast iteration
- stable layouts
- easy debugging
- CSS positioning support

Rules:

- Use fixed-position layouts
- Use CSS positioning
- Prioritize visual consistency

Do NOT:

- dynamically calculate SVG layouts
- implement drag/drop rendering systems
- over-engineer template rendering

---

# Coding Standards

- Use type hints everywhere
- Keep controllers thin
- Keep services modular
- Prefer readability over abstraction
- Avoid giant files over 300 lines
- Use snake_case naming
- Use dependency injection where appropriate

---

# API Conventions

Use RESTful conventions.

Examples:

- GET /clients
- POST /clients
- PUT /clients/{id}
- GET /monthly-logs
- POST /reports/sacs/{id}

---

# Out of Scope (V1)

The following are intentionally excluded:

- authentication
- RBAC
- RightCapital integration
- Schwab integration
- Plaid integration
- background workers
- websocket updates
- distributed systems
- advanced analytics

---

# Success Criteria

The API succeeds if:

1. client data entry is fast
2. calculations are reliable
3. reports generate consistently
4. PDF output looks professional
5. the workflow is smooth and stable
