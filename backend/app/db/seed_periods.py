"""Seed the five reporting periods.

Extraction fixtures reference periods by label, so these rows must exist
before any fixture can be loaded. Idempotent: safe to run repeatedly.

H2 FY2025 is included as a derived period per assumption A-03. It carries no
extracted line items, only computed metrics.
"""

import asyncio
from datetime import date

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.source import ReportingPeriod

PERIODS = [
    {
        "label": "FY2024",
        "period_type": "annual",
        "start_date": date(2023, 7, 1),
        "end_date": date(2024, 6, 30),
        "is_audited": True,
        "reporting_entity": "ADF Farm Solutions Limited",
        "reporting_basis": "company",
        "is_derived": False,
    },
    {
        "label": "FY2025",
        "period_type": "annual",
        "start_date": date(2024, 7, 1),
        "end_date": date(2025, 6, 30),
        "is_audited": True,
        "reporting_entity": "ADF Farm Solutions Limited",
        "reporting_basis": "company",
        "is_derived": False,
    },
    {
        "label": "HY2025",
        "period_type": "half_year",
        "start_date": date(2024, 7, 1),
        "end_date": date(2024, 12, 31),
        "is_audited": False,
        "reporting_entity": "Senus PLC",
        "reporting_basis": "group",
        "is_derived": False,
    },
    {
        "label": "HY2026",
        "period_type": "half_year",
        "start_date": date(2025, 7, 1),
        "end_date": date(2025, 12, 31),
        "is_audited": False,
        "reporting_entity": "Senus PLC",
        "reporting_basis": "group",
        "is_derived": False,
    },
    {
        # Derived by subtracting HY2025 from FY2025. Basis is mixed because
        # the two inputs are on different bases. See assumptions A-02, A-03.
        "label": "H2FY2025",
        "period_type": "half_year",
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 6, 30),
        "is_audited": False,
        "reporting_entity": "ADF Farm Solutions Limited",
        "reporting_basis": "mixed",
        "is_derived": True,
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        existing = set((await session.execute(select(ReportingPeriod.label))).scalars().all())
        added = 0
        for spec in PERIODS:
            if spec["label"] in existing:
                continue
            session.add(ReportingPeriod(**spec))
            added += 1
        await session.commit()
        print(f"Seeded {added} periods. {len(existing)} already present.")


if __name__ == "__main__":
    asyncio.run(seed())
