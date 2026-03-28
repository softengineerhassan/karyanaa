"""rename is_available_for_booking to is_featured

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-02-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'g7h8i9j0k1l2'
down_revision = 'f6g7h8i9j0k1'
branch_labels = None
depends_on = None


def upgrade():
    """Rename is_available_for_booking to is_featured in resources table"""
    # Check if column already renamed (skip if already done)
    from sqlalchemy import inspect
    from sqlalchemy.engine import reflection
    
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('resources', schema='omnia')]
    
    # Only rename if old column exists
    if 'is_available_for_booking' in columns:
        op.alter_column(
            'resources',
            'is_available_for_booking',
            new_column_name='is_featured',
            schema='omnia'
        )
    
    # Update default value from True to False (if column exists)
    if 'is_featured' in columns or 'is_available_for_booking' in columns:
        op.alter_column(
            'resources',
            'is_featured',
            server_default='false',
            schema='omnia'
        )


def downgrade():
    """Revert is_featured back to is_available_for_booking"""
    # Rename back
    op.alter_column(
        'resources',
        'is_featured',
        new_column_name='is_available_for_booking',
        schema='omnia'
    )
    
    # Restore original default value
    op.alter_column(
        'resources',
        'is_available_for_booking',
        server_default='true',
        schema='omnia'
    )
