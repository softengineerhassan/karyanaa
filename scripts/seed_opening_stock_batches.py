from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import and_, func, select

from app.database.session import SessionLocal
from app.models.inventory import Product, StockBatch, StockMovement


def main() -> None:
    session = SessionLocal()
    try:
        products = session.execute(
            select(Product)
            .where(
                Product.deleted_at.is_(None),
                Product.is_active.is_(True),
                Product.track_inventory.is_(True),
            )
            .order_by(Product.name.asc())
        ).scalars().all()

        created_batches = 0
        for product in products:
            available_qty = session.execute(
                select(func.coalesce(func.sum(StockBatch.quantity_available), 0)).where(
                    and_(
                        StockBatch.product_id == product.id,
                        StockBatch.deleted_at.is_(None),
                        StockBatch.quantity_available > 0,
                    )
                )
            ).scalar()

            if Decimal(str(available_qty or 0)) > Decimal("0"):
                continue

            opening_qty = Decimal("100")
            batch = StockBatch(
                product_id=product.id,
                purchase_item_id=None,
                batch_number=f"OPEN-{datetime.utcnow().strftime('%Y%m%d')}-{str(product.id)[:8]}",
                expiry_date=None,
                unit_cost=Decimal(str(product.default_purchase_price or 0)),
                selling_price=Decimal(str(product.default_selling_price or 0)),
                quantity_received=opening_qty,
                quantity_available=opening_qty,
            )
            session.add(batch)
            session.flush()

            movement = StockMovement(
                product_id=product.id,
                purchase_id=None,
                purchase_item_id=None,
                stock_batch_id=batch.id,
                movement_type="opening_in",
                reference_type="opening_balance",
                reference_id=None,
                quantity_in=opening_qty,
                quantity_out=Decimal("0"),
                unit_cost=Decimal(str(product.default_purchase_price or 0)),
                notes="Auto opening stock seed",
                movement_date=datetime.utcnow(),
            )
            session.add(movement)
            created_batches += 1

        session.commit()

        print("Opening stock seeding completed.")
        print(f"Track-inventory products checked: {len(products)}")
        print(f"Batches created: {created_batches}")
    except Exception as exc:
        session.rollback()
        print(f"Opening stock seeding failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
