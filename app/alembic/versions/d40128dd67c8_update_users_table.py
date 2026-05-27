"""update users table

Revision ID: d40128dd67c8
Revises: e41b0fbcf540
Create Date: 2026-05-27 09:58:25.388625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd40128dd67c8'
down_revision: Union[str, None] = 'e41b0fbcf540'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN referral_by DROP DEFAULT"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN referral_by SET DEFAULT 0"
    )
