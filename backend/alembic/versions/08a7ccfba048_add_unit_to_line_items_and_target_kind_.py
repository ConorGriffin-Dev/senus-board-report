"""Add unit to line items and target_kind to targets

Revision ID: 08a7ccfba048
Revises: 6f43dd7d7f9f
Create Date: 2026-07-21 11:20:01.899385

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "08a7ccfba048"
down_revision: Union[str, Sequence[str], None] = "6f43dd7d7f9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "financial_line_item",
        sa.Column("unit", sa.String(length=16), nullable=False, server_default="eur"),
    )
    op.alter_column(
        "financial_line_item", "currency", existing_type=sa.String(length=3), nullable=True
    )
    op.create_check_constraint(
        "ck_line_item_unit",
        "financial_line_item",
        "unit IN ('eur', 'percent', 'count', 'ratio')",
    )
    op.create_check_constraint(
        "ck_currency_matches_unit",
        "financial_line_item",
        "(unit = 'eur' AND currency IS NOT NULL) OR (unit <> 'eur' AND currency IS NULL)",
    )

    op.add_column(
        "target",
        sa.Column("target_kind", sa.String(length=16), nullable=False, server_default="threshold"),
    )
    op.alter_column("target", "target_value", existing_type=sa.Numeric(18, 4), nullable=True)
    op.create_check_constraint(
        "ck_target_kind",
        "target",
        "target_kind IN ('threshold', 'milestone')",
    )
    op.create_check_constraint(
        "ck_target_value_matches_kind",
        "target",
        "(target_kind = 'threshold' AND target_value IS NOT NULL) "
        "OR (target_kind = 'milestone' AND target_value IS NULL)",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_target_value_matches_kind", "target", type_="check")
    op.drop_constraint("ck_target_kind", "target", type_="check")
    op.alter_column("target", "target_value", existing_type=sa.Numeric(18, 4), nullable=False)
    op.drop_column("target", "target_kind")

    op.drop_constraint("ck_currency_matches_unit", "financial_line_item", type_="check")
    op.drop_constraint("ck_line_item_unit", "financial_line_item", type_="check")
    op.alter_column(
        "financial_line_item", "currency", existing_type=sa.String(length=3), nullable=False
    )
    op.drop_column("financial_line_item", "unit")
