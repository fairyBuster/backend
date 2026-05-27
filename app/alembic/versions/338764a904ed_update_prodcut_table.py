"""update prodcut table

Revision ID: 338764a904ed
Revises: c2763078c851
Create Date: 2026-05-27 12:03:14.585954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '338764a904ed'
down_revision: Union[str, None] = 'c2763078c851'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'products',
        'image',
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=sa.String(length=255),
        existing_nullable=False,
        existing_server_default=None,
    )

def downgrade() -> None:
    op.alter_column(
        'products',
        'image',
        existing_type=sa.String(length=255),
        type_=postgresql.JSON(astext_type=sa.Text()),
        existing_nullable=False,
        existing_server_default=sa.text("'[]'::json"),
    )
