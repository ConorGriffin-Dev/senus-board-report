"""Add sign_convention to financial_line_item

Revision ID: 6f43dd7d7f9f
Revises: ce2eee455f8c
Create Date: 2026-07-21 10:54:30.069210

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6f43dd7d7f9f"
down_revision: Union[str, Sequence[str], None] = "ce2eee455f8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "financial_line_item",
        sa.Column(
            "sign_convention",
            sa.String(length=16),
            nullable=False,
            server_default="as_printed",
        ),
    )
    # Autogenerate does not emit CHECK constraints, so this is added by hand.
    op.create_check_constraint(
        "ck_sign_convention",
        "financial_line_item",
        "sign_convention IN ('as_printed', 'negated_label')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_sign_convention", "financial_line_item", type_="check")
    op.drop_column("financial_line_item", "sign_convention")
