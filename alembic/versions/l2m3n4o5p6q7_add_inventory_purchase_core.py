"""add_inventory_purchase_core

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-03-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "l2m3n4o5p6q7"
down_revision: Union[str, None] = "k1l2m3n4o5p6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.add_column("categories", sa.Column("name", sa.String(length=100), nullable=True))
    op.add_column("categories", sa.Column("slug", sa.String(length=120), nullable=True))
    op.add_column("categories", sa.Column("parent_id", UUID, nullable=True))
    op.add_column("categories", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")))

    op.execute("UPDATE categories SET name = COALESCE(name_en, name_ar, name_fr) WHERE name IS NULL")
    op.execute(
        """
        UPDATE categories
        SET slug = LOWER(REGEXP_REPLACE(COALESCE(name_en, name_ar, name_fr), '[^a-zA-Z0-9]+', '-', 'g'))
        WHERE slug IS NULL
        """
    )

    op.alter_column("categories", "name", nullable=False)
    op.alter_column("categories", "slug", nullable=False)
    op.create_unique_constraint("uq_categories_name", "categories", ["name"])
    op.create_unique_constraint("uq_categories_slug", "categories", ["slug"])
    op.create_foreign_key(
        "fk_categories_parent_id_categories",
        "categories",
        "categories",
        ["parent_id"],
        ["id"],
    )

    op.create_table(
        "brands",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("name", name="uq_brands_name"),
    )

    op.create_table(
        "units",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("name", name="uq_units_name"),
        sa.UniqueConstraint("symbol", name="uq_units_symbol"),
    )

    op.create_table(
        "suppliers",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("company_name", sa.String(length=150), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("alternate_phone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("opening_balance", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("current_balance", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "riders",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("vehicle_number", sa.String(length=50), nullable=True),
        sa.Column("supplier_id", UUID, sa.ForeignKey("suppliers.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "products",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=True),
        sa.Column("barcode", sa.String(length=120), nullable=True),
        sa.Column("category_id", UUID, sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("brand_id", UUID, sa.ForeignKey("brands.id"), nullable=True),
        sa.Column("unit_id", UUID, sa.ForeignKey("units.id"), nullable=False),
        sa.Column("purchase_unit_id", UUID, sa.ForeignKey("units.id"), nullable=True),
        sa.Column("sales_unit_id", UUID, sa.ForeignKey("units.id"), nullable=True),
        sa.Column("product_type", sa.String(length=30), nullable=False, server_default="stockable"),
        sa.Column("track_inventory", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("has_expiry", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("has_batch", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("minimum_stock_alert", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("default_purchase_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("default_selling_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("tax_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("slug", name="uq_products_slug"),
        sa.UniqueConstraint("sku", name="uq_products_sku"),
        sa.UniqueConstraint("barcode", name="uq_products_barcode"),
    )

    op.create_table(
        "purchases",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("purchase_number", sa.String(length=50), nullable=False),
        sa.Column("supplier_id", UUID, sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("rider_id", UUID, sa.ForeignKey("riders.id"), nullable=True),
        sa.Column("invoice_number", sa.String(length=100), nullable=True),
        sa.Column("invoice_date", sa.Date(), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=False, server_default="cash"),
        sa.Column("payment_status", sa.String(length=30), nullable=False, server_default="unpaid"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("discount_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("tax_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("other_charges", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("grand_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("remaining_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="posted"),
        sa.Column("created_by", UUID, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("purchase_number", name="uq_purchases_purchase_number"),
    )

    op.create_table(
        "purchase_items",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("purchase_id", UUID, sa.ForeignKey("purchases.id"), nullable=False),
        sa.Column("product_id", UUID, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("product_name_snapshot", sa.String(length=150), nullable=False),
        sa.Column("sku_snapshot", sa.String(length=80), nullable=True),
        sa.Column("unit_id", UUID, sa.ForeignKey("units.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("bonus_quantity", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_type", sa.String(length=20), nullable=True),
        sa.Column("discount_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("tax_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("batch_number", sa.String(length=100), nullable=True),
        sa.Column("manufacturing_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "purchase_payments",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("purchase_id", UUID, sa.ForeignKey("purchases.id"), nullable=False),
        sa.Column("supplier_id", UUID, sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=False),
        sa.Column("reference_number", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "stock_batches",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("product_id", UUID, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("purchase_item_id", UUID, sa.ForeignKey("purchase_items.id"), nullable=True),
        sa.Column("batch_number", sa.String(length=100), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("quantity_received", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("quantity_available", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "stock_movements",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("product_id", UUID, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("purchase_id", UUID, sa.ForeignKey("purchases.id"), nullable=True),
        sa.Column("purchase_item_id", UUID, sa.ForeignKey("purchase_items.id"), nullable=True),
        sa.Column("stock_batch_id", UUID, sa.ForeignKey("stock_batches.id"), nullable=True),
        sa.Column("movement_type", sa.String(length=30), nullable=False),
        sa.Column("reference_type", sa.String(length=30), nullable=False),
        sa.Column("reference_id", UUID, nullable=True),
        sa.Column("quantity_in", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("quantity_out", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("movement_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("stock_movements")
    op.drop_table("stock_batches")
    op.drop_table("purchase_payments")
    op.drop_table("purchase_items")
    op.drop_table("purchases")
    op.drop_table("products")
    op.drop_table("riders")
    op.drop_table("suppliers")
    op.drop_table("units")
    op.drop_table("brands")
    op.drop_constraint("fk_categories_parent_id_categories", "categories", type_="foreignkey")
    op.drop_constraint("uq_categories_slug", "categories", type_="unique")
    op.drop_constraint("uq_categories_name", "categories", type_="unique")
    op.drop_column("categories", "is_active")
    op.drop_column("categories", "parent_id")
    op.drop_column("categories", "slug")
    op.drop_column("categories", "name")
