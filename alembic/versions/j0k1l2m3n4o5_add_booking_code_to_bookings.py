"""add booking_code to bookings

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-02-17 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'j0k1l2m3n4o5'
down_revision = 'i9j0k1l2m3n4'
branch_labels = None
depends_on = None


def upgrade():
    # Add booking_code column (8-character alphanumeric code)
    op.add_column('bookings', sa.Column('booking_code', sa.String(8), nullable=True))
    op.create_index('idx_booking_code', 'bookings', ['booking_code'], unique=False)
    
    # Add qr_token column (JWT token string)
    op.add_column('bookings', sa.Column('qr_token', sa.String(500), nullable=True))


def downgrade():
    # Drop columns
    op.drop_index('idx_booking_code', table_name='bookings')
    op.drop_column('bookings', 'qr_token')
    op.drop_column('bookings', 'booking_code')
