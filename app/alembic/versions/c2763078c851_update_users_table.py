"""update users table

Revision ID: c2763078c851
Revises: d40128dd67c8
Create Date: 2026-05-27 11:32:55.531246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2763078c851'
down_revision: Union[str, None] = 'd40128dd67c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE products ALTER COLUMN image DROP DEFAULT"
    )

    op.execute(
        "ALTER TABLE products ALTER COLUMN image SET DEFAULT '[]'::json"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE products ALTER COLUMN image DROP DEFAULT"
    )

    op.execute(
        "ALTER TABLE products ALTER COLUMN image SET DEFAULT '0'"
    )