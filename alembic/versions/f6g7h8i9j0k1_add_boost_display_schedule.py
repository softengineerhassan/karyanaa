"""add_boost_display_schedule

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-02-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f6g7h8i9j0k1'
down_revision: Union[str, None] = 'e5f6g7h8i9j0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add display value and schedule fields to perks table for boost perks"""
    
    # Add display_value
    op.add_column('perks', sa.Column('display_value', sa.String(length=100), nullable=True))
    
    # Add boost schedule fields
    op.add_column('perks', sa.Column('boost_start_date', sa.Date(), nullable=True))
    op.add_column('perks', sa.Column('boost_start_time', sa.Time(), nullable=True))
    op.add_column('perks', sa.Column('boost_end_date', sa.Date(), nullable=True))
    op.add_column('perks', sa.Column('boost_end_time', sa.Time(), nullable=True))


def downgrade() -> None:
    """Remove display value and schedule fields from perks table"""
    
    # Drop columns
    op.drop_column('perks', 'boost_end_time')
    op.drop_column('perks', 'boost_end_date')
    op.drop_column('perks', 'boost_start_time')
    op.drop_column('perks', 'boost_start_date')
    op.drop_column('perks', 'display_value')
