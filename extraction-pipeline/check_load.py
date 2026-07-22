"""Post-load checks against the database.

Verifies that what the loader reported actually landed, and spot-checks the
two things most likely to have been silently altered on the way in: the
share price precision and the reattributed period assignments.
"""

import asyncio

from app.db.session import AsyncSessionLocal
from app.models.financial import FinancialLineItem, Segment
from app.models.metrics import Target
from app.models.source import ExtractionRun, ReportingPeriod, SourceDocument
from sqlalchemy import func, select


async def main() -> None:
    async with AsyncSessionLocal() as session:
        print("Row counts")
        for model, name in (
            (SourceDocument, "documents"),
            (ExtractionRun, "extraction runs"),
            (FinancialLineItem, "line items"),
            (Segment, "segments"),
            (Target, "targets"),
        ):
            count = await session.scalar(select(func.count()).select_from(model))
            print(f"  {name}: {count}")

        print("\nLine items by period")
        rows = await session.execute(
            select(ReportingPeriod.label, func.count(FinancialLineItem.id))
            .outerjoin(
                FinancialLineItem,
                FinancialLineItem.reporting_period_id == ReportingPeriod.id,
            )
            .group_by(ReportingPeriod.label)
            .order_by(ReportingPeriod.label)
        )
        for label, count in rows:
            print(f"  {label}: {count}")

        flagged = await session.scalar(
            select(func.count())
            .select_from(FinancialLineItem)
            .where(FinancialLineItem.validation_status == "flagged")
        )
        print(f"\nFlagged line items: {flagged}")

        print("\nNon-euro units, checking currency is null")
        rows = await session.execute(
            select(
                FinancialLineItem.label,
                FinancialLineItem.unit,
                FinancialLineItem.currency,
            )
            .where(FinancialLineItem.unit != "eur")
            .order_by(FinancialLineItem.label)
        )
        for label, unit, currency in rows:
            print(f"  {label}: {unit}, currency={currency}")

        print("\nPrecision check")
        price = await session.scalar(
            select(FinancialLineItem.value).where(
                FinancialLineItem.label == "Implied share price on admission"
            )
        )
        print(f"  Implied share price stored as {price}, source states 5.126")

        print("\nReattributed items, expect HY2026")
        rows = await session.execute(
            select(FinancialLineItem.label, ReportingPeriod.label)
            .join(
                ReportingPeriod,
                FinancialLineItem.reporting_period_id == ReportingPeriod.id,
            )
            .where(
                FinancialLineItem.label.in_(
                    [
                        "Private placement gross proceeds",
                        "Post money enterprise valuation",
                        "Implied share price on admission",
                        "Issued share capital",
                        "Employee headcount",
                    ]
                )
            )
            .order_by(FinancialLineItem.label)
        )
        for label, period in rows:
            print(f"  {label}: {period}")


if __name__ == "__main__":
    asyncio.run(main())
