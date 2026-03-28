"""add venue favorites table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2024-02-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create venue_favorites table
    op.create_table(
        'venue_favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('venue_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'venue_id', name='unique_user_venue_favorite')
    )
    
    # Create indexes
    op.create_index(
        'idx_venue_favorites_user_id',
        'venue_favorites',
        ['user_id'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    op.create_index(
        'idx_venue_favorites_venue_id',
        'venue_favorites',
        ['venue_id'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )
    op.create_index(
        'idx_venue_favorites_user_venue',
        'venue_favorites',
        ['user_id', 'venue_id'],
        postgresql_where=sa.text('deleted_at IS NULL')
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_venue_favorites_user_venue', table_name='venue_favorites')
    op.drop_index('idx_venue_favorites_venue_id', table_name='venue_favorites')
    op.drop_index('idx_venue_favorites_user_id', table_name='venue_favorites')
    
    # Drop table
    op.drop_table('venue_favorites')
