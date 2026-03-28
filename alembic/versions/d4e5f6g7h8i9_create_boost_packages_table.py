"""create boost packages table

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2024-02-14 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create boost_packages table
    op.create_table(
        'boost_packages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('duration_hours', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('label', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('duration_hours', name='uq_boost_packages_duration_hours')
    )
    
    # Create indexes
    op.create_index('idx_boost_packages_duration_hours', 'boost_packages', ['duration_hours'])
    op.create_index('idx_boost_packages_is_active', 'boost_packages', ['is_active'])
    op.create_index('idx_boost_packages_active_duration', 'boost_packages', ['is_active', 'duration_hours'])
    
    # Add comments
    op.execute("""
        COMMENT ON TABLE boost_packages IS 'Master configuration for Boost campaign pricing packages';
        COMMENT ON COLUMN boost_packages.duration_hours IS 'Duration in hours (24, 48, 72, 168 for 7 days)';
        COMMENT ON COLUMN boost_packages.price IS 'Price for this boost duration';
        COMMENT ON COLUMN boost_packages.label IS 'Display label (e.g., Weekend Boost)';
        COMMENT ON COLUMN boost_packages.description IS 'Optional description for the package';
        COMMENT ON COLUMN boost_packages.is_active IS 'Whether this package is available for selection';
    """)
    
    # Insert default boost packages
    op.execute("""
        INSERT INTO boost_packages (duration_hours, price, label, description, is_active)
        VALUES
            (24, 50.00, '24 Hours Boost', 'Boost your venue for one full day', true),
            (48, 90.00, '48 Hours Boost', 'Weekend boost package', true),
            (72, 120.00, '72 Hours Boost', 'Extended 3-day boost', true),
            (168, 200.00, '7 Days Boost', 'Full week boost campaign', true);
    """)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_boost_packages_active_duration', table_name='boost_packages')
    op.drop_index('idx_boost_packages_is_active', table_name='boost_packages')
    op.drop_index('idx_boost_packages_duration_hours', table_name='boost_packages')
    
    # Drop table
    op.drop_table('boost_packages')
