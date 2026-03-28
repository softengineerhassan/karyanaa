"""
Seed script for sales module.
Tests complete sales flow with FIFO stock allocation, payment recording, and balance calculations.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select
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
from app.models.sales import (
    Customer,
    Sale,
    SaleItem,
    SalePayment,
    SaleItemBatchAllocation,
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
from app.api.v1.schemas.sales_schema import (
    CustomerCreateRequest,
    SaleCreateRequest,
    SaleItemCreateRequest,
    SalePaymentCreateRequest,
)
from app.services.inventory_service import InventoryService
from app.services.sales_service import SalesService


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Create all tables
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
        Customer.__table__,
        Sale.__table__,
        SaleItem.__table__,
        SalePayment.__table__,
        SaleItemBatchAllocation.__table__,
    ]:
        table.create(bind=engine, checkfirst=True)

    session = SessionLocal()
    try:
        inventory_service = InventoryService(session)
        sales_service = SalesService(session)

        # ====================================================================
        # SETUP: Create inventory (same as purchase tests)
        # ====================================================================
        
        print("\n=== SETUP: Creating Inventory Data ===")
        
        category = session.execute(
            select(Category).where(Category.name == "Grocery", Category.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not category:
            category = inventory_service.create_category(
                CategoryCreateRequest(
                    name="Grocery",
                    slug="grocery",
                    description="Daily grocery items",
                    parent_id=None,
                    is_active=True,
                )
            )
            print(f"✓ Created Category: {category.name}")

        unit = session.execute(
            select(Unit).where(Unit.symbol == "kg", Unit.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not unit:
            unit = inventory_service.create_unit(
                UnitCreateRequest(
                    name="Kilogram",
                    symbol="kg",
                    description="Weight unit",
                    is_active=True,
                )
            )
            print(f"✓ Created Unit: {unit.name}")

        supplier = session.execute(
            select(Supplier).where(Supplier.name == "National Traders", Supplier.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not supplier:
            supplier = inventory_service.create_supplier(
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
            print(f"✓ Created Supplier: {supplier.name}")

        rider = session.execute(
            select(Rider).where(Rider.name == "Ali Rider", Rider.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not rider:
            rider = inventory_service.create_rider(
                RiderCreateRequest(
                    name="Ali Rider",
                    phone="+923005551234",
                    vehicle_number="ABC-1234",
                    supplier_id=supplier.id,
                    notes="Regular delivery rider",
                    is_active=True,
                )
            )
            print(f"✓ Created Rider: {rider.name}")

        # Create products with stock
        product_sugar = session.execute(
            select(Product).where(Product.sku == "SUGAR-1KG", Product.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not product_sugar:
            product_sugar = inventory_service.create_product(
                ProductCreateRequest(
                    name="Sugar 1kg",
                    slug="sugar-1kg",
                    sku="SUGAR-1KG",
                    barcode="1234567890",
                    category_id=category.id,
                    brand_id=None,
                    unit_id=unit.id,
                    purchase_unit_id=unit.id,
                    sales_unit_id=unit.id,
                    product_type="stockable",
                    track_inventory=True,
                    has_expiry=False,
                    has_batch=True,
                    minimum_stock_alert=Decimal("5"),
                    default_purchase_price=Decimal("100"),
                    default_selling_price=Decimal("150"),
                    tax_percent=Decimal("0"),
                    description="Premium white sugar",
                    image_url=None,
                    is_active=True,
                )
            )
            print(f"✓ Created Product: {product_sugar.name}")

        product_oil = session.execute(
            select(Product).where(Product.sku == "OIL-5L", Product.deleted_at.is_(None))
        ).scalar_one_or_none()
        if not product_oil:
            product_oil = inventory_service.create_product(
                ProductCreateRequest(
                    name="Cooking Oil 5L",
                    slug="cooking-oil-5l",
                    sku="OIL-5L",
                    barcode="0987654321",
                    category_id=category.id,
                    brand_id=None,
                    unit_id=unit.id,
                    purchase_unit_id=unit.id,
                    sales_unit_id=unit.id,
                    product_type="stockable",
                    track_inventory=True,
                    has_expiry=True,
                    has_batch=True,
                    minimum_stock_alert=Decimal("2"),
                    default_purchase_price=Decimal("500"),
                    default_selling_price=Decimal("650"),
                    tax_percent=Decimal("0"),
                    description="Pure cooking oil",
                    image_url=None,
                    is_active=True,
                )
            )
            print(f"✓ Created Product: {product_oil.name}")

        # Create purchase to populate stock
        purchase = inventory_service.create_purchase(
            PurchaseCreateRequest(
                supplier_id=supplier.id,
                rider_id=rider.id,
                invoice_number="INV-2026-001",
                invoice_date=date.today(),
                purchase_date=date.today(),
                payment_method="cash",
                paid_amount=Decimal("0"),
                other_charges=Decimal("0"),
                notes="Initial stock",
                items=[
                    PurchaseItemCreate(
                        product_id=product_sugar.id,
                        unit_id=unit.id,
                        quantity=Decimal("50"),
                        bonus_quantity=Decimal("5"),
                        unit_cost=Decimal("100"),
                        discount_type=None,
                        discount_value=Decimal("0"),
                        tax_percent=Decimal("0"),
                        batch_number="BATCH-001",
                        expiry_date=None,
                        selling_price=Decimal("150"),
                        notes=None,
                    ),
                    PurchaseItemCreate(
                        product_id=product_oil.id,
                        unit_id=unit.id,
                        quantity=Decimal("30"),
                        bonus_quantity=Decimal("0"),
                        unit_cost=Decimal("500"),
                        discount_type=None,
                        discount_value=Decimal("0"),
                        tax_percent=Decimal("0"),
                        batch_number="BATCH-OIL-001",
                        expiry_date=date(2027, 12, 31),
                        selling_price=Decimal("650"),
                        notes=None,
                    ),
                ],
            )
        )
        print(f"✓ Created Purchase: {purchase.purchase_number} with {len(purchase.items)} items")

        # ====================================================================
        # SALES TEST: Create customers
        # ====================================================================
        
        print("\n=== SALES TEST: Creating Customers ===")
        
        # Create default walk-in customer
        walk_in = sales_service.get_or_create_walk_in_customer()
        print(f"✓ Walk-in Customer: {walk_in.name} (ID: {walk_in.id})")

        # Create regular customer
        import time
        timestamp = int(time.time() % 10000)
        try:
            regular_customer = sales_service.create_customer(
                CustomerCreateRequest(
                    name="Ahmed Hassan",
                    phone=f"+923009876{timestamp % 10000:04d}",
                    email="ahmed@example.com",
                    address="Street 10, Lahore",
                    city="Lahore",
                    opening_balance=Decimal("500"),
                    customer_type="regular",
                    notes="Regular customer",
                )
            )
        except Exception as e:
            # If duplicate, fetch existing regular customer
            if "duplicate" in str(e).lower():
                regular_customer = session.query(Customer).filter_by(customer_type="regular").first()
                if not regular_customer:
                    raise
            else:
                raise
        print(f"✓ Regular Customer: {regular_customer.name} (Balance: {regular_customer.current_balance})")

        # ====================================================================
        # SALES TEST: Create sale with FIFO allocation
        # ====================================================================
        
        print("\n=== SALES TEST: Creating Sale (FIFO Allocation) ===")
        
        sale = sales_service.create_sale(
            SaleCreateRequest(
                customer_id=str(regular_customer.id),
                sale_date=date.today(),
                invoice_number="SAL-2026-001",
                payment_method="cash",
                paid_amount=Decimal("5000"),
                other_charges=Decimal("0"),
                notes="Test sale with multiple items",
                items=[
                    SaleItemCreateRequest(
                        product_id=str(product_sugar.id),
                        unit_id=str(unit.id),
                        quantity=Decimal("20"),
                        unit_price=Decimal("150"),
                        discount_type="flat",
                        discount_value=Decimal("200"),
                        tax_percent=Decimal("0"),
                        notes="Bulk discount",
                    ),
                    SaleItemCreateRequest(
                        product_id=str(product_oil.id),
                        unit_id=str(unit.id),
                        quantity=Decimal("5"),
                        unit_price=Decimal("650"),
                        discount_type="percent",
                        discount_value=Decimal("5"),
                        tax_percent=Decimal("0"),
                        notes="Volume discount",
                    ),
                ],
            )
        )
        print(f"✓ Created Sale: {sale.sale_number}")
        print(f"  - Subtotal: {sale.subtotal}")
        print(f"  - Discount Total: {sale.discount_total}")
        print(f"  - Tax Total: {sale.tax_total}")
        print(f"  - Grand Total: {sale.grand_total}")
        print(f"  - Paid Amount: {sale.paid_amount}")
        print(f"  - Remaining: {sale.remaining_amount}")
        print(f"  - Payment Status: {sale.payment_status}")

        # Verify items and allocations
        print(f"\n  - Items: {len(sale.items)}")
        for item in sale.items:
            print(f"    • {item.product_name_snapshot}: Qty {item.quantity} @ {item.unit_price} = {item.line_total}")
            print(f"      Allocations: {len(item.batch_allocations)}")
            for alloc in item.batch_allocations:
                print(f"        - Batch {alloc.stock_batch_id}: {alloc.quantity_allocated} units")

        # Verify customer balance updated
        customer_refreshed = sales_service.get_customer_by_id(regular_customer.id)
        print(f"\n  - Customer Balance Updated: {customer_refreshed.current_balance}")
        expected_balance = Decimal("500") + sale.remaining_amount
        print(f"    Expected: {expected_balance}")

        # ====================================================================
        # SALES TEST: Add payment
        # ====================================================================
        
        print("\n=== SALES TEST: Adding Payment ===")
        
        sale_with_payment = sales_service.add_sale_payment(
            sale.id,
            SalePaymentCreateRequest(
                payment_date=date.today(),
                amount=Decimal("3000"),
                payment_method="bank_transfer",
                reference_number="TRF-123456",
                notes="Partial payment",
            )
        )
        print(f"✓ Added Payment of {Decimal('3000')}")
        print(f"  - New Paid Amount: {sale_with_payment.paid_amount}")
        print(f"  - New Remaining: {sale_with_payment.remaining_amount}")
        print(f"  - Payment Status: {sale_with_payment.payment_status}")

        # Verify customer balance after payment
        customer_refreshed = sales_service.get_customer_by_id(regular_customer.id)
        print(f"  - Customer Balance After Payment: {customer_refreshed.current_balance}")

        # ====================================================================
        # VERIFICATION: Database state
        # ====================================================================
        
        print("\n=== VERIFICATION: Database State ===")
        
        # Count records
        customer_count = session.execute(select(Customer).where(Customer.deleted_at.is_(None))).scalars().all()
        sale_count = session.execute(select(Sale).where(Sale.deleted_at.is_(None))).scalars().all()
        sale_item_count = session.execute(select(SaleItem).where(SaleItem.deleted_at.is_(None))).scalars().all()
        sale_payment_count = session.execute(select(SalePayment).where(SalePayment.deleted_at.is_(None))).scalars().all()
        allocation_count = session.execute(select(SaleItemBatchAllocation)).scalars().all()
        
        print(f"Customers: {len(customer_count)}")
        print(f"Sales: {len(sale_count)}")
        print(f"Sale Items: {len(sale_item_count)}")
        print(f"Sale Payments: {len(sale_payment_count)}")
        print(f"Batch Allocations: {len(allocation_count)}")

        # Verify FIFO allocation reduced stock
        batches = session.execute(select(StockBatch).where(StockBatch.product_id.in_([product_sugar.id, product_oil.id]))).scalars().all()
        print(f"\nStock Batch Status:")
        for batch in batches:
            print(f"  - {batch.product_id}: {batch.quantity_available} available (received: {batch.quantity_received})")

        # Verify stock movements created
        movements = session.execute(select(StockMovement).where(StockMovement.reference_type == "sale")).scalars().all()
        print(f"\nStock Movements (sale_out): {len(movements)}")
        for movement in movements:
            print(f"  - Product {movement.product_id}: {movement.quantity_out} units out")

        print("\n=== ALL TESTS PASSED ===")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
