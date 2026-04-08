"""add_rider_purchase_items_table

Revision ID: 4d1a3c4d9b11
Revises: 9f3c2bd2e7a1
Create Date: 2026-04-06 13:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d1a3c4d9b11"
down_revision = "9f3c2bd2e7a1"
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to existing rider_purchase_items table
    op.add_column('rider_purchase_items', sa.Column('item_code', sa.String(length=80), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('barcode', sa.String(length=120), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('category', sa.String(length=150), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('brand', sa.String(length=120), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('unit', sa.String(length=50), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('unit_size', sa.Numeric(precision=12, scale=3), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('cost_price', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('expiry_date', sa.Date(), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('batch_number', sa.String(length=100), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('supplier_name', sa.String(length=150), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('supplier_contact', sa.String(length=30), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('status', sa.String(length=30), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('payment_status', sa.String(length=30), nullable=True))
    op.add_column('rider_purchase_items', sa.Column('created_by', sa.UUID(), nullable=True))
    
    # Create indexes for the new columns
    op.create_index(op.f('ix_rider_purchase_items_created_by'), 'rider_purchase_items', ['created_by'], unique=False)
    
    # Note: The other indexes (deleted_at, owner_user_id, rider_profile_id) should already exist from the original table creation


def downgrade():
    # Drop the new columns and their index
    op.drop_index(op.f('ix_rider_purchase_items_created_by'), table_name='rider_purchase_items', if_exists=True)
    op.drop_column('rider_purchase_items', 'status')
    op.drop_column('rider_purchase_items', 'payment_status')
    op.drop_column('rider_purchase_items', 'supplier_contact')
    op.drop_column('rider_purchase_items', 'supplier_name')
    op.drop_column('rider_purchase_items', 'batch_number')
    op.drop_column('rider_purchase_items', 'expiry_date')
    op.drop_column('rider_purchase_items', 'cost_price')
    op.drop_column('rider_purchase_items', 'unit_size')
    op.drop_column('rider_purchase_items', 'unit')
    op.drop_column('rider_purchase_items', 'brand')
    op.drop_column('rider_purchase_items', 'category')
    op.drop_column('rider_purchase_items', 'barcode')
    op.drop_column('rider_purchase_items', 'item_code')
    op.drop_column('rider_purchase_items', 'created_by')
