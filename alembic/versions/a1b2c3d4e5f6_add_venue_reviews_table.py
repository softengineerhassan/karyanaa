"""add_venue_reviews_table

Revision ID: a1b2c3d4e5f6
Revises: f9fb38292809
Create Date: 2026-02-14 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f9fb38292809'
branch_labels = None
depends_on = None


def upgrade():
    # Create venue_reviews table
    op.create_table(
        'venue_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('venue_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('booking_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        
        # Constraints
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        sa.UniqueConstraint('booking_id', name='uq_venue_reviews_booking_id'),
    )
    
    # Create indexes
    op.create_index('ix_venue_reviews_venue_id', 'venue_reviews', ['venue_id'])
    op.create_index('ix_venue_reviews_user_id', 'venue_reviews', ['user_id'])
    op.create_index('ix_venue_reviews_venue_rating', 'venue_reviews', ['venue_id', 'rating'])
    op.create_index('ix_venue_reviews_user_venue', 'venue_reviews', ['user_id', 'venue_id'])
    op.create_index('ix_venue_reviews_deleted_at', 'venue_reviews', ['deleted_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_venue_reviews_deleted_at', table_name='venue_reviews')
    op.drop_index('ix_venue_reviews_user_venue', table_name='venue_reviews')
    op.drop_index('ix_venue_reviews_venue_rating', table_name='venue_reviews')
    op.drop_index('ix_venue_reviews_user_id', table_name='venue_reviews')
    op.drop_index('ix_venue_reviews_venue_id', table_name='venue_reviews')
    
    # Drop table
    op.drop_table('venue_reviews')
