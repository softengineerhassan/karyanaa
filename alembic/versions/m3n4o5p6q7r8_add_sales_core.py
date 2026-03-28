"""Add sales module with customer, sale, sale_item, sale_payment, and batch allocation tables.

Revision ID: m3n4o5p6q7r8
Revises: l2m3n4o5p6q7
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers, used by Alembic.
revision = 'm3n4o5p6q7r8'
down_revision = 'l2m3n4o5p6q7'
branch_labels = None
depends_on = None


def upgrade():
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('phone', sa.String(30), nullable=True),
        sa.Column('email', sa.String(120), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('opening_balance', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('current_balance', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('customer_type', sa.String(30), nullable=False, server_default='walk_in'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone'),
        schema='omnia'
    )
    op.create_index(op.f('ix_omnia_customers_deleted_at'), 'customers', ['deleted_at'], schema='omnia')

    # Create sales table
    op.create_table(
        'sales',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_number', sa.String(50), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_date', sa.Date(), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('payment_method', sa.String(30), nullable=False, server_default='cash'),
        sa.Column('payment_status', sa.String(30), nullable=False, server_default='unpaid'),
        sa.Column('subtotal', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('discount_total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('tax_total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('other_charges', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('grand_total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('paid_amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('remaining_amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='posted'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['omnia.customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sale_number'),
        schema='omnia'
    )
    op.create_index(op.f('ix_omnia_sales_deleted_at'), 'sales', ['deleted_at'], schema='omnia')

    # Create sale_items table
    op.create_table(
        'sale_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_name_snapshot', sa.String(150), nullable=False),
        sa.Column('sku_snapshot', sa.String(80), nullable=True),
        sa.Column('barcode_snapshot', sa.String(120), nullable=True),
        sa.Column('unit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(12, 3), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('cost_price_snapshot', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('discount_type', sa.String(20), nullable=True),
        sa.Column('discount_value', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('tax_percent', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('line_total', sa.Numeric(12, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['omnia.products.id'], ),
        sa.ForeignKeyConstraint(['sale_id'], ['omnia.sales.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['omnia.units.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='omnia'
    )
    op.create_index(op.f('ix_omnia_sale_items_deleted_at'), 'sale_items', ['deleted_at'], schema='omnia')

    # Create sale_payments table
    op.create_table(
        'sale_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_method', sa.String(30), nullable=False),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['omnia.customers.id'], ),
        sa.ForeignKeyConstraint(['sale_id'], ['omnia.sales.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='omnia'
    )
    op.create_index(op.f('ix_omnia_sale_payments_deleted_at'), 'sale_payments', ['deleted_at'], schema='omnia')

    # Create sale_item_batch_allocations table
    op.create_table(
        'sale_item_batch_allocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sale_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stock_batch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity_allocated', sa.Numeric(12, 3), nullable=False),
        sa.Column('unit_cost', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['sale_item_id'], ['omnia.sale_items.id'], ),
        sa.ForeignKeyConstraint(['stock_batch_id'], ['omnia.stock_batches.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='omnia'
    )


def downgrade():
    op.drop_table('sale_item_batch_allocations', schema='omnia')
    op.drop_table('sale_payments', schema='omnia')
    op.drop_table('sale_items', schema='omnia')
    op.drop_table('sales', schema='omnia')
    op.drop_table('customers', schema='omnia')
