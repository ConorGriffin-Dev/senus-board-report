# Project Instructions — Senus PLC Board Report (Assiduous Tech Grad Assignment)

Standing reference for all work on this repo. Check back against
`Assiduous_TechGradAssignment.pdf` before making architectural or scope
decisions. If a decision made elsewhere conflicts with this document, the
conflict is resolved here, not silently overridden.

## 0. How this project works

- Feature work (extraction pipeline, API, frontend, diagrams) happens
  incrementally against this scaffold.
- Any change to an architectural decision (stack, schema, extraction
  approach) should be reflected back into this document so later work
  doesn't drift from earlier decisions.
- Diagrams: PlantUML source, rendered images committed alongside.
- Code style: no em dashes, no redundant abstractions, no dead code, no
  unvalidated AI output presented as fact.

## 1. Context (from the PDF)

Senus PLC, Irish Natural Capital management software provider. Founded 2017
(Brendan Allen, Eoghan Finneran, Joe Desbonnet). Admitted to Euronext Access
Dublin 22 December 2025. Products: Measurement, Reporting, Verification,
Planning (MRVP) of natural resource value chains, sold direct and via
intermediaries. FY to 30 June 2025: revenue €836,991, 138 customer accounts.
First public half-year results (period to Dec 2025) reported March 2026.
Strategy "Senus 2030": ≥50% revenue CAGR 2026–2030. Reference source:
https://app.assiduous.tech/investor-relations/senus

## 2. Definition of done (per PDF)

Full-stack, interactive web app, CEO-usable, built around:

- AI-driven extraction of financial data from source documents into a database.
- A Board Report model computed from that database (not hardcoded figures).
- Metrics: Growth & Revenue (YoY, MoM, customers, channels, bookings),
  Profitability (gross/operating/EBITDA margin, cost breakdown), Cash &
  Liquidity (EBITDA-to-FCF bridge, cash runway, working capital), Solvency &
  Leverage (DSCR), Returns (ROCE), plus AI-generated commentary where it adds
  real value.
- Production-quality engineering: architecture, scalability, modern
  frontend, backend APIs, data modelling, AI integration, polished UX.
- README covering architecture, AI-assisted workflow, assumptions,
  validation method.

Submission requires: YouTube demo link, GitHub repo link, one-page write-up
(optional).

## 3. Architecture (standing decision, revisit only with reasoning)

```
[Extraction Pipeline] -> [Database] -> [API Layer] -> [Frontend]
                                            ^
                                      [AI Insight Service]
```

Extraction and insight generation are kept as two separate AI touchpoints.
Extraction turns documents into numbers; insight generation turns numbers
into commentary. Do not conflate them in one prompt or one service.

**Stack:**
- Extraction pipeline: Python (parsing libraries, natural home for LLM extraction calls).
- Backend API: FastAPI (Python) by default, for one language across pipeline
  and API and shared Pydantic validation. Switch to Node/NestJS only if a
  future decision finds shared TypeScript types with the frontend outweighs
  that, and if so, update this section.
- Database: PostgreSQL. Financial data is relational, needs transactional
  integrity, and window functions give YoY/MoM directly in SQL.
- Frontend: React + TypeScript.
- AI: Anthropic API, used separately for extraction and for commentary.

**Rejected and why:** NoSQL (data is relational, referential integrity
between source document, raw figure, and computed metric matters). No-code
dashboard tools (defeats the brief's purpose).

**Data model principle:** raw extracted values are never overwritten by
computed values. Keep `FinancialLineItem` (raw + source ref + confidence)
separate from `ComputedMetric` (derived), with a traceable link between them.

## 4. AI-assisted workflow requirements

Every piece of work that touches extraction or insight generation produces,
as it goes:

- Validation notes: sample of extracted figures checked against source, with error rate.
- Prompts stored as versioned files, not inline strings.
- Assumptions log: anything inferred rather than sourced, stated explicitly.

## 4.1 Source document handling (standing decision)

Source PDFs are not committed to the repository. They are Senus PLC investor
communications and are not republished here. `.gitignore` excludes
`extraction-pipeline/source-docs/`.

Reproducibility is preserved through the fixture files rather than through
the documents themselves. Extraction outputs are committed under `fixtures/`,
every extracted figure carries a document, page and location reference, and
validation notes record what was checked against source and the error rate
found. A reviewer can verify any figure by obtaining the document
independently and checking the stated location.

This trades full end-to-end reproducibility for not redistributing client
material. Revisit only if the documents are confirmed as freely
redistributable.

## 5. Open items

- Confirm backend language choice against real team preference.
- Pull actual Senus investor relations source documents and inventory what
  data genuinely exists before finalizing the metric list.
- Draft ER diagram against real fields once source documents are reviewed.

## 6. Confirmed tech stack

| Layer | Choice |
|---|---|
| Extraction pipeline | Python 3.12, pdfplumber, PyMuPDF, pandas |
| Backend API | FastAPI (Python), async |
| Database | PostgreSQL 16, `numeric` type for all financial figures (never `float`) |
| ORM / migrations | SQLAlchemy 2.0 + Alembic |
| Frontend | React + TypeScript, Vite, TanStack Query, Recharts, Tailwind CSS |
| AI | Anthropic API — extraction service and insight service kept separate |
| Dev environment | Local Postgres via Docker Compose, ruff for Python lint/format, ESLint + Prettier for frontend |
