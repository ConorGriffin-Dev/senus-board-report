# Senus PLC Board Report

AI-native platform that extracts financial data from Senus PLC's source documents
into a database, computes board-level financial metrics from that data, and
presents them through an interactive Board Report UI — built for the Assiduous
Technology Graduate Assessment.

## Status

Scaffolding stage. Directory structure, tooling, and standing architecture
decisions are in place. Feature work (extraction pipeline, API, frontend,
metric definitions) happens incrementally in follow-up work, tracked against
`docs/PROJECT_INSTRUCTIONS.md`.

## Architecture

```
[Extraction Pipeline] -> [PostgreSQL] -> [FastAPI Backend] -> [React Frontend]
                                              ^
                                     [AI Insight Service]
```

Extraction and insight generation are two separate Anthropic API touchpoints:
- **Extraction service** turns source document text into `FinancialLineItem`
  records with a source reference and confidence score.
- **Insight service** is given only computed metrics (never raw document
  text) and generates board commentary. This keeps commentary grounded in
  verified figures rather than half-parsed source text.

Raw extracted values (`FinancialLineItem`) are never overwritten by derived
values (`ComputedMetric`); a traceable link is kept between them.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Extraction pipeline | Python 3.12, pdfplumber/PyMuPDF, pandas | One language for parsing + LLM calls + validation |
| Backend API | FastAPI | Shared Pydantic models with the extraction pipeline, async, auto OpenAPI docs |
| Database | PostgreSQL 16 | Relational integrity between document → line item → metric; window functions for YoY/MoM |
| ORM / migrations | SQLAlchemy 2.0 + Alembic | Typed models, versioned schema |
| Frontend | React + TypeScript + Vite | TanStack Query for data fetching, Recharts for charts, Tailwind for styling |
| AI | Anthropic API | Used separately for extraction and for commentary |

Full reasoning for each choice is in `docs/PROJECT_INSTRUCTIONS.md`.

## Repository layout

```
extraction-pipeline/   Python: document parsing, cleaning, LLM extraction, prompts (versioned files)
backend/                FastAPI app, SQLAlchemy models, Alembic migrations
frontend/               React + TypeScript + Vite app
docs/                   Diagrams, validation notes, standing project instructions
infra/                  Docker Compose for local Postgres
```

## Local setup

### Prerequisites
- Python 3.12
- Node 22+
- Docker (for local Postgres)

### 1. Database
```bash
cd infra
docker compose up -d
```

### 2. Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env   # fill in ANTHROPIC_API_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Extraction pipeline
```bash
cd extraction-pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

## AI-assisted development workflow

This project is built with AI assistance (Claude). Every chat that touches
extraction or insight generation produces, as it goes:
- Validation notes (sample of extracted figures checked against source, with error rate) in `docs/validation-notes/`
- Prompts as versioned files in `extraction-pipeline/prompts/`, not inline strings
- An assumptions log for anything inferred rather than sourced

## Deliverables (per assignment)

- [ ] YouTube demo link
- [ ] GitHub repo (this one)
- [ ] One-page write-up (optional)
