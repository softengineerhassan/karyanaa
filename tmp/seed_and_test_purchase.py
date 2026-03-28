from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.inventory import (
    Brand,
    Category,
    Product,
    Purchase,
    PurchaseItem,
    PurchasePayment,
    Rider,
    StockBatch,
    StockMovement,
    Supplier,
    Unit,
)
from app.api.v1.schemas.inventory_schema import (
    CategoryCreateRequest,
    ProductCreateRequest,
    PurchaseCreateRequest,
    PurchaseItemCreate,
    RiderCreateRequest,
    SupplierCreateRequest,
    UnitCreateRequest,
)
from app.services.inventory_service import InventoryService


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    for table in [
        Category.__table__,
        Brand.__table__,
        Unit.__table__,
        Supplier.__table__,
        Rider.__table__,
        Product.__table__,
        Purchase.__table__,
        PurchaseItem.__table__,
        PurchasePayment.__table__,
        StockBatch.__table__,
        StockMovement.__table__,
    ]:
        table.create(bind=engine, checkfirst=True)

    session = SessionLocal()
    try:
        service = InventoryService(session)

        category = session.execute(
            select(Category).where(Category.name == "Grocery", Category.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not category:
            category = service.create_category(
                CategoryCreateRequest(
                    name="Grocery",
                    slug="grocery",
                    description="Daily grocery items",
                    parent_id=None,
                    is_active=True,
                )
            )

        unit = session.execute(
            select(Unit).where(Unit.symbol == "kg", Unit.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not unit:
            unit = service.create_unit(
                UnitCreateRequest(
                    name="Kilogram",
                    symbol="kg",
                    description="Weight unit",
                    is_active=True,
                )
            )

        supplier = session.execute(
            select(Supplier).where(Supplier.name == "National Traders", Supplier.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not supplier:
            supplier = service.create_supplier(
                SupplierCreateRequest(
                    name="National Traders",
                    company_name="National Pvt Ltd",
                    phone="+923001112233",
                    alternate_phone=None,
                    email="national@example.com",
                    address="Main bazaar",
                    city="Lahore",
                    opening_balance=Decimal("0"),
                    notes="Primary supplier",
                    is_active=True,
                )
            )

        rider = session.execute(
            select(Rider).where(Rider.name == "Ali Rider", Rider.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not rider:
            rider = service.create_rider(
                RiderCreateRequest(
                    name="Ali Rider",
                    phone="+923331234567",
                    vehicle_number="LEA-1234",
                    supplier_id=supplier.id,
                    notes="Regular delivery",
                    is_active=True,
                )
            )

        sugar = session.execute(
            select(Product).where(Product.sku == "SUG-1KG", Product.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not sugar:
            sugar = service.create_product(
                ProductCreateRequest(
                    name="Sugar 1kg",
                    slug="sugar-1kg",
                    sku="SUG-1KG",
                    barcode="6291000011111",
                    category_id=category.id,
                    brand_id=None,
                    unit_id=unit.id,
                    purchase_unit_id=unit.id,
                    sales_unit_id=unit.id,
                    product_type="stockable",
                    track_inventory=True,
                    has_expiry=True,
                    has_batch=True,
                    minimum_stock_alert=Decimal("5"),
                    default_purchase_price=Decimal("140"),
                    default_selling_price=Decimal("160"),
                    tax_percent=Decimal("0"),
                    description="Fine sugar",
                    image_url=None,
                    is_active=True,
                )
            )

        oil = session.execute(
            select(Product).where(Product.sku == "OIL-5L", Product.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not oil:
            oil = service.create_product(
                ProductCreateRequest(
                    name="Cooking Oil 5L",
                    slug="cooking-oil-5l",
                    sku="OIL-5L",
                    barcode="6291000022222",
                    category_id=category.id,
                    brand_id=None,
                    unit_id=unit.id,
                    purchase_unit_id=unit.id,
                    sales_unit_id=unit.id,
                    product_type="stockable",
                    track_inventory=True,
                    has_expiry=True,
                    has_batch=True,
                    minimum_stock_alert=Decimal("3"),
                    default_purchase_price=Decimal("520"),
                    default_selling_price=Decimal("560"),
                    tax_percent=Decimal("0"),
                    description="Refined oil",
                    image_url=None,
                    is_active=True,
                )
            )

        payload = PurchaseCreateRequest(
            supplier_id=supplier.id,
            rider_id=rider.id,
            invoice_number="INV-2026-0001",
            invoice_date=date(2026, 3, 28),
            purchase_date=date(2026, 3, 28),
            payment_method="cash",
            payment_status="partially_paid",
            other_charges=Decimal("50"),
            notes="Goods received in good condition",
            paid_amount=Decimal("5000"),
            items=[
                PurchaseItemCreate(
                    product_id=sugar.id,
                    unit_id=unit.id,
                    quantity=Decimal("20"),
                    bonus_quantity=Decimal("2"),
                    unit_cost=Decimal("140"),
                    discount_type="flat",
                    discount_value=Decimal("100"),
                    tax_percent=Decimal("0"),
                    batch_number="SUG-001",
                    manufacturing_date=date(2026, 2, 1),
                    expiry_date=date(2026, 9, 1),
                    selling_price=Decimal("160"),
                    notes="Promo stock",
                ),
                PurchaseItemCreate(
                    product_id=oil.id,
                    unit_id=unit.id,
                    quantity=Decimal("30"),
                    bonus_quantity=Decimal("0"),
                    unit_cost=Decimal("520"),
                    discount_type="percent",
                    discount_value=Decimal("2"),
                    tax_percent=Decimal("0"),
                    batch_number="OIL-009",
                    manufacturing_date=date(2026, 1, 15),
                    expiry_date=date(2027, 1, 15),
                    selling_price=Decimal("560"),
                    notes=None,
                ),
            ],
        )

        purchase = service.create_purchase(payload, created_by=None)

        movement_count = session.execute(
            select(func.count(StockMovement.id)).where(StockMovement.purchase_id == purchase.id)
        ).scalar_one()
        batch_count = session.execute(
            select(func.count(StockBatch.id))
            .join(PurchaseItem, StockBatch.purchase_item_id == PurchaseItem.id)
            .where(PurchaseItem.purchase_id == purchase.id)
        ).scalar_one()

        print("PURCHASE_ID", purchase.id)
        print("PURCHASE_NUMBER", purchase.purchase_number)
        print("SUBTOTAL", purchase.subtotal)
        print("DISCOUNT_TOTAL", purchase.discount_total)
        print("TAX_TOTAL", purchase.tax_total)
        print("GRAND_TOTAL", purchase.grand_total)
        print("PAID_AMOUNT", purchase.paid_amount)
        print("REMAINING", purchase.remaining_amount)
        print("PAYMENT_STATUS", purchase.payment_status)
        print("STOCK_BATCHES", batch_count)
        print("STOCK_MOVEMENTS", movement_count)

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
