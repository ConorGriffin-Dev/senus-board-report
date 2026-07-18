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

Extraction and insight generation are two separate AI touchpoints, run
manually via Claude.ai/ChatGPT rather than a live API key (see
[AI-assisted development workflow](#ai-assisted-development-workflow) below):
- **Extraction service** turns source document text into `FinancialLineItem`
  records with a source reference and confidence score.
- **Insight service** is given only computed metrics (never raw document
  text) and generates board commentary. This keeps commentary grounded in
  verified figures rather than half-parsed source text.

Both services read from versioned fixture files at runtime rather than
calling a live API. Each service isolates the model call behind a single
function, so a live key could be substituted later without touching parsing,
validation, or DB-write logic.

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
| AI | Anthropic-style prompting, run manually (no live API key) | Extraction and insight generation done via Claude.ai/ChatGPT, outputs cached as fixtures. See AI-assisted workflow section. |

Full reasoning for each choice is in `docs/PROJECT_INSTRUCTIONS.md`.

## Repository layout

```
extraction-pipeline/   Python: document parsing, cleaning, extraction service, prompts (versioned files)
  prompts/              extraction_v1.md, insight_v1.md
  fixtures/
    extraction/          Cached extraction outputs, one file per source document
    insights/             Cached commentary outputs, one file per reporting period
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
cp ../.env.example ../.env   # DATABASE_URL only, no API key required
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Extraction pipeline
```bash
cd extraction-pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m extraction.seed   # loads cached fixtures from fixtures/extraction/
                             # and fixtures/insights/ into the database
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

## AI-assisted development workflow

**No live Anthropic API key is used in this project.** AI extraction and
insight generation are performed manually through the Claude.ai chat
interface, and the outputs are cached as versioned fixture files that the
pipeline reads and validates exactly as if they had come from a live API
response.

Rationale: cost control, reproducibility (anyone can re-run the pipeline
from the committed fixtures without a key), and no runtime dependency on a
live model call for a CEO-facing report.

### How it works

| Stage | Location |
|---|---|
| Prompts (versioned, never inline in code) | `prompts/extraction_v1.md`, `prompts/insight_v1.md` |
| Extraction outputs | `fixtures/extraction/<document_name>.json` |
| Insight outputs | `fixtures/insight/<period>.json` |
| Swap point for a live API key | single model-call function in `extraction_service.py` and `insight_service.py`, clearly commented |

Fixture outputs still pass through the same Pydantic validation, confidence
scoring, and source-reference attachment that a live API response would.
This is not a shortcut around the data model, only around where the model
call happens. Substituting a live API key later means changing one function
per service, with no change to parsing, validation, or database-write logic.

### Requirements for any work touching extraction or insight generation

- Validation notes recorded when each fixture is created: sample of extracted
  figures checked against source, with error rate. Stored in `docs/validation-notes/`.
- Prompts stored as versioned files in `prompts/`, never as inline strings.
- Assumptions log: anything inferred rather than sourced, stated explicitly.
- Fixture files committed under `fixtures/`, named by document/period, so the
  extraction run is reproducible without re-running anything manually.

## Deliverables (per assignment)

- [ ] YouTube demo link
- [ ] GitHub repo (this one)
- [ ] One-page write-up (optional)
