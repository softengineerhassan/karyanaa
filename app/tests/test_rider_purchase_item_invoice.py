from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock
import uuid

from app.models.rider_profile import RiderProfile
from app.models.rider_purchase_item import RiderPurchaseItem
from app.services.rider_purchase_item_service import RiderPurchaseItemService


def test_generate_invoice_pdf_returns_pdf_bytes() -> None:
    service = RiderPurchaseItemService(MagicMock())

    owner_user_id = uuid.uuid4()
    rider = RiderProfile(
        id=uuid.uuid4(),
        owner_user_id=owner_user_id,
        full_name="Ali Khan",
        phone_number="03001234567",
        email="ali@example.com",
        profile_image=None,
        created_at=datetime(2026, 4, 6, 10, 30, 0),
        updated_at=datetime(2026, 4, 6, 10, 30, 0),
        deleted_at=None,
    )
    item = RiderPurchaseItem(
        id=uuid.uuid4(),
        owner_user_id=owner_user_id,
        rider_profile_id=rider.id,
        item_name="Delivery Bag",
        quantity=Decimal("1.000"),
        unit_price=Decimal("2500.00"),
        total_amount=Decimal("2500.00"),
        purchase_date=date(2026, 4, 6),
        notes="Issued against rider shift",
        created_at=datetime(2026, 4, 6, 10, 30, 0),
        updated_at=datetime(2026, 4, 6, 10, 30, 0),
        deleted_at=None,
    )

    pdf_bytes = service.generate_invoice_pdf(item, rider)

    assert pdf_bytes[:4] == b"%PDF"