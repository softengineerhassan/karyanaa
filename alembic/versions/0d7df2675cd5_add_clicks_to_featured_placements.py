"""add_clicks_to_featured_placements

Revision ID: 0d7df2675cd5
Revises: 3e455169e798
Create Date: 2026-03-10 15:42:49.792107
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d7df2675cd5'
down_revision = '3e455169e798'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('venue_featured_placements', sa.Column('clicks', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('venue_featured_placements', 'clicks')
