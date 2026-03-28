"""add_booking_created_by_id

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-14 16:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add created_by_id column to bookings table
    op.add_column('bookings', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_bookings_created_by_user',
        'bookings',
        'users',
        ['created_by_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index for performance
    op.create_index('idx_booking_created_by_id', 'bookings', ['created_by_id'])


def downgrade():
    # Drop index
    op.drop_index('idx_booking_created_by_id', table_name='bookings')
    
    # Drop foreign key
    op.drop_constraint('fk_bookings_created_by_user', 'bookings', type_='foreignkey')
    
    # Drop column
    op.drop_column('bookings', 'created_by_id')
