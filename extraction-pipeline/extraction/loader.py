"""Load validated extraction fixtures into PostgreSQL.

One transaction per document. Load order matters: the authoritative document
must be loaded first so it claims the unique constraints on targets and
segments before a corroborating document is offered.

Every deviation between fixture and database is logged as it happens, so the
run output is a complete account of what was changed and what was skipped.
"""

import argparse
import asyncio
from datetime import UTC, datetime

from app.db.session import AsyncSessionLocal
from app.models.financial import FinancialLineItem, Segment
from app.models.metrics import Target
from app.models.source import ExtractionRun, ReportingPeriod, SourceDocument
from extraction import load_rules
from extraction.extraction_service import (
    MODEL_NAME,
    PROMPT_VERSION,
    extract,
    fixture_path_for,
)
from extraction.schemas import ExtractionResult
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# DOC-01 before DOC-03 so the listing document claims the shared targets and
# segments. See assumption A-14.
LOAD_ORDER = ["DOC-01", "DOC-02", "DOC-03"]

# Source URLs and retrieval dates, from docs/source-inventory.md. Held here
# rather than in the fixtures because they describe how the document was
# obtained, not what it contains.
DOCUMENT_PROVENANCE = {
    "DOC-01": {
        "source_url": (
            "https://live.euronext.com/sites/default/files/2025-12/"
            "SENUS%20PLC%20-%20Information%20Document.pdf"
        ),
        "retrieved_at": datetime(2026, 7, 18, tzinfo=UTC),
    },
    "DOC-02": {
        "source_url": "https://app.assiduous.tech/investor-relations/senus",
        "retrieved_at": datetime(2026, 7, 18, tzinfo=UTC),
    },
    "DOC-03": {
        "source_url": "https://app.assiduous.tech/investor-relations/senus",
        "retrieved_at": datetime(2026, 7, 18, tzinfo=UTC),
    },
}


class LoadReport:
    """Accumulates what happened during a load, for printing at the end."""

    def __init__(self) -> None:
        self.loaded: dict[str, int] = {}
        self.skipped: list[str] = []
        self.reattributed: list[str] = []

    def record(self, key: str, count: int) -> None:
        self.loaded[key] = self.loaded.get(key, 0) + count

    def skip(self, reason: str) -> None:
        self.skipped.append(reason)

    def reattribute(self, detail: str) -> None:
        self.reattributed.append(detail)

    def print(self) -> None:
        print("\nLoaded:")
        for key, count in sorted(self.loaded.items()):
            print(f"  {key}: {count}")

        if self.reattributed:
            print(f"\nReattributed ({len(self.reattributed)}), per assumption A-13:")
            for detail in self.reattributed:
                print(f"  {detail}")

        if self.skipped:
            print(f"\nSkipped ({len(self.skipped)}):")
            for reason in self.skipped:
                print(f"  {reason}")


async def _period_lookup(session: AsyncSession) -> dict[str, ReportingPeriod]:
    result = await session.execute(select(ReportingPeriod))
    return {p.label: p for p in result.scalars().all()}


async def _upsert_document(
    session: AsyncSession, result: ExtractionResult
) -> SourceDocument:
    meta = result.document
    existing = await session.execute(
        select(SourceDocument).where(SourceDocument.doc_ref == meta.doc_ref)
    )
    document = existing.scalar_one_or_none()
    if document is not None:
        return document

    provenance = DOCUMENT_PROVENANCE[meta.doc_ref]
    document = SourceDocument(
        doc_ref=meta.doc_ref,
        filename=meta.filename,
        document_type=meta.document_type,
        publication_date=meta.publication_date,
        source_url=provenance["source_url"],
        retrieved_at=provenance["retrieved_at"],
        page_count=meta.page_count,
        reporting_entity=meta.reporting_entity,
        reporting_basis=meta.reporting_basis,
    )
    session.add(document)
    await session.flush()
    return document


async def _load_line_items(
    session: AsyncSession,
    result: ExtractionResult,
    document: SourceDocument,
    run: ExtractionRun,
    periods: dict[str, ReportingPeriod],
    report: LoadReport,
) -> None:
    doc_ref = result.document.doc_ref

    for item in result.line_items:
        period_label = item.period_label
        note = item.validation_note

        if period_label == "unmapped":
            report.skip(f"{doc_ref} line item '{item.label}': unmapped period (A-16)")
            continue

        corrected = load_rules.reattributed_period(doc_ref, item.label, period_label)
        if corrected is not None:
            note = load_rules.append_note(
                note,
                load_rules.REATTRIBUTION_NOTE.format(
                    original=period_label, reattributed=corrected
                ),
            )
            report.reattribute(
                f"{doc_ref} '{item.label}': {period_label} to {corrected}"
            )
            period_label = corrected

        session.add(
            FinancialLineItem(
                source_document_id=document.id,
                reporting_period_id=periods[period_label].id,
                extraction_run_id=run.id,
                label=item.label,
                value=item.value,
                unit=item.unit,
                currency=item.currency,
                statement=item.statement,
                sign_convention=item.sign_convention,
                page_number=item.page_number,
                source_location=item.source_location,
                data_class=item.data_class,
                confidence=item.confidence,
                validation_status=item.validation_status,
                validation_note=note,
                extracted_at=run.executed_at,
            )
        )
        report.record("line items", 1)


async def _load_segments(
    session: AsyncSession,
    result: ExtractionResult,
    document: SourceDocument,
    periods: dict[str, ReportingPeriod],
    report: LoadReport,
) -> None:
    doc_ref = result.document.doc_ref

    for segment in result.segments:
        if segment.period_label == "unmapped":
            report.skip(
                f"{doc_ref} segment '{segment.segment_name}': unmapped period (A-16)"
            )
            continue

        period = periods[segment.period_label]
        clash = await session.execute(
            select(Segment).where(
                Segment.reporting_period_id == period.id,
                Segment.segment_type == segment.segment_type,
                Segment.segment_name == segment.segment_name,
            )
        )
        if clash.scalar_one_or_none() is not None:
            report.skip(
                f"{doc_ref} segment '{segment.segment_type}/{segment.segment_name}' "
                f"{segment.period_label}: already loaded from "
                f"{load_rules.AUTHORITATIVE_FOR_SEGMENTS} (A-14)"
            )
            continue

        session.add(
            Segment(
                source_document_id=document.id,
                reporting_period_id=period.id,
                segment_type=segment.segment_type,
                segment_name=segment.segment_name,
                revenue_share_pct=segment.revenue_share_pct,
                revenue_value=segment.revenue_value,
                customer_count=segment.customer_count,
                avg_contract_value=segment.avg_contract_value,
                confidence=segment.confidence,
            )
        )
        report.record("segments", 1)


async def _load_targets(
    session: AsyncSession,
    result: ExtractionResult,
    document: SourceDocument,
    periods: dict[str, ReportingPeriod],
    report: LoadReport,
) -> None:
    doc_ref = result.document.doc_ref

    for target in result.targets:
        clash = await session.execute(
            select(Target).where(
                Target.target_type == target.target_type,
                Target.target_period_label == target.target_period_label,
            )
        )
        if clash.scalar_one_or_none() is not None:
            report.skip(
                f"{doc_ref} target '{target.target_type}' {target.target_period_label}: "
                f"already loaded from {load_rules.AUTHORITATIVE_FOR_TARGETS} (A-14)"
            )
            continue

        baseline = periods.get(target.baseline_period_label or "")
        session.add(
            Target(
                source_document_id=document.id,
                target_type=target.target_type,
                target_kind=target.target_kind,
                target_value=target.target_value,
                unit=target.unit,
                target_period_label=target.target_period_label,
                baseline_period_id=baseline.id if baseline else None,
                baseline_value=target.baseline_value,
            )
        )
        report.record("targets", 1)


async def load_document(
    session: AsyncSession,
    doc_ref: str,
    periods: dict[str, ReportingPeriod],
    report: LoadReport,
) -> None:
    """Load one document. Validation failures raise before anything is written."""
    result = extract(doc_ref)
    document = await _upsert_document(session, result)

    run = ExtractionRun(
        source_document_id=document.id,
        fixture_path=fixture_path_for(doc_ref),
        prompt_version=PROMPT_VERSION,
        model_name=MODEL_NAME,
        executed_at=datetime.now(UTC),
        notes="; ".join(result.extraction_notes) if result.extraction_notes else None,
    )
    session.add(run)
    await session.flush()

    await _load_line_items(session, result, document, run, periods, report)
    await _load_segments(session, result, document, periods, report)
    await _load_targets(session, result, document, periods, report)


async def purge(session: AsyncSession) -> None:
    """Clear extracted data so a load can be repeated.

    Reporting periods survive: they are reference data seeded separately, and
    line items reference them.
    """
    for model in (FinancialLineItem, Segment, Target, ExtractionRun, SourceDocument):
        await session.execute(delete(model))
    await session.commit()
    print("Purged existing extraction data.")


async def main(reset: bool) -> None:
    async with AsyncSessionLocal() as session:
        if reset:
            await purge(session)

        periods = await _period_lookup(session)
        if not periods:
            raise RuntimeError(
                "No reporting periods found. Run app.db.seed_periods first."
            )

        report = LoadReport()
        for doc_ref in LOAD_ORDER:
            print(f"Loading {doc_ref}...")
            await load_document(session, doc_ref, periods, report)

        await session.commit()
        report.print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load extraction fixtures into PostgreSQL."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing extracted data before loading.",
    )
    args = parser.parse_args()
    asyncio.run(main(args.reset))
