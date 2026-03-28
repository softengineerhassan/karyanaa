"""add_boost_snapshot_to_perks

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-02-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add boost package snapshot fields to perks table"""
    
    # Add boost_package_id foreign key
    op.add_column('perks', sa.Column('boost_package_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Add duration_hours_snapshot
    op.add_column('perks', sa.Column('duration_hours_snapshot', sa.Integer(), nullable=True))
    
    # Add price_snapshot
    op.add_column('perks', sa.Column('price_snapshot', sa.Numeric(precision=10, scale=2), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_perks_boost_package_id',
        'perks',
        'boost_packages',
        ['boost_package_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index on boost_package_id for faster lookups
    op.create_index('ix_perks_boost_package_id', 'perks', ['boost_package_id'])


def downgrade() -> None:
    """Remove boost package snapshot fields from perks table"""
    
    # Drop index
    op.drop_index('ix_perks_boost_package_id', table_name='perks')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_perks_boost_package_id', 'perks', type_='foreignkey')
    
    # Drop columns
    op.drop_column('perks', 'price_snapshot')
    op.drop_column('perks', 'duration_hours_snapshot')
    op.drop_column('perks', 'boost_package_id')
