"""add featured_placement_pricing table

Revision ID: 9c4c9022cba9
Revises: j0k1l2m3n4o5
Create Date: 2026-03-04 19:21:39.071626
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c4c9022cba9'
down_revision = 'j0k1l2m3n4o5'
branch_labels = None
depends_on = None


def upgrade():
    # Create the table in the 'omnia' schema
    op.create_table(
        'featured_placement_pricing',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('placement_type', sa.Enum('homepage_featured', 'category_featured', 'spotlight_visibility', name='featured_placement_type_enum'), nullable=False),
        sa.Column('price_per_month', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('monthly_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('booking_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('placement_type'),
        schema='omnia'
    )
    op.create_index(op.f('ix_omnia_featured_placement_pricing_placement_type'), 'featured_placement_pricing', ['placement_type'], unique=True, schema='omnia')

    # Seed initial data
    op.execute(sa.text("""
        INSERT INTO omnia.featured_placement_pricing 
        (id, placement_type, price_per_month, monthly_views, booking_percentage) 
        VALUES 
        (gen_random_uuid(), 'homepage_featured', 500.00, 50000, 245.00),
        (gen_random_uuid(), 'category_featured', 300.00, 25000, 180.00),
        (gen_random_uuid(), 'spotlight_visibility', 150.00, 12000, 125.00)
    """))


def downgrade():
    op.drop_index(op.f('ix_omnia_featured_placement_pricing_placement_type'), table_name='featured_placement_pricing', schema='omnia')
    op.drop_table('featured_placement_pricing', schema='omnia')
    op.execute("DROP TYPE IF EXISTS featured_placement_type_enum")

