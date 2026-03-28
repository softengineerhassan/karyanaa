"""
Quick test of sales API without HTTP server.
Tests all the fix points.
"""
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.sales import Customer, Sale, SaleItem, SalePayment, SaleItemBatchAllocation
from app.models.inventory import Product, Unit, Supplier, Category, Brand, Rider, Purchase, PurchaseItem, PurchasePayment, StockBatch, StockMovement
from app.api.v1.schemas.sales_schema import CustomerCreateRequest, CustomerResponse, SaleCreateRequest, SaleItemCreateRequest
from app.services.sales_service import SalesService
from app.services.inventory_service import InventoryService
from app.api.v1.actions.sales_actions import SalesActions

def main():
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
        print("\n=== API LAYER TEST ===\n")
        
        # Test SalesActions layer directly
        actions = SalesActions(session)
        
        # Test 1: Create customer (this was failing before the fix)
        print("Test 1: Creating customer via SalesActions...")
        req = CustomerCreateRequest(
            name="Test Customer",
            phone="+923001234567",
            customer_type="regular",
            opening_balance=Decimal("1000"),
        )
        response = actions.create_customer(req)
        print(f"✓ Customer created: {response.id}")
        print(f"  - Name: {response.name}")
        print(f"  - Balance: {response.current_balance}")
        print(f"  - Type: {type(response).__name__}")
        assert isinstance(response, CustomerResponse), "Response should be CustomerResponse"
        
        # Test 2: Get customer
        print("\nTest 2: Getting customer...")
        customer = actions.get_customer(response.id)
        assert customer is not None, "Customer should be found"
        print(f"✓ Customer retrieved: {customer.name}")
        
        # Test 3: List customers
        print("\nTest 3: Listing customers...")
        customers = actions.list_customers(limit=10)
        print(f"✓ Listed {len(customers)} customer(s)")
        
        # Test 4: Update customer
        print("\nTest 4: Updating customer...")
        from app.api.v1.schemas.sales_schema import CustomerUpdateRequest
        update_req = CustomerUpdateRequest(
            name="Updated Customer Name"
        )
        updated = actions.update_customer(response.id, update_req)
        print(f"✓ Customer updated: {updated.name}")
        
        print("\n=== ALL API TESTS PASSED ===\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
