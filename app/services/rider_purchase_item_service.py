import asyncio
from datetime import datetime
from io import BytesIO
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from sqlalchemy.orm import Session

from app.api.v1.schemas.rider_purchase_item_schema import RiderPurchaseItemCreateRequest, RiderPurchaseItemUpdateRequest
from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.rider_purchase_item import RiderPurchaseItem
from app.models.rider_profile import RiderProfile
from app.repos.rider_profile_repository import RiderProfileRepository
from app.repos.rider_purchase_item_repository import RiderPurchaseItemRepository
from app.services.email_service import EmailService

logger = get_logger(__name__)


class RiderPurchaseItemService:
    def __init__(self, session: Session):
        self.session = session
        self.item_repo = RiderPurchaseItemRepository(session)
        self.rider_repo = RiderProfileRepository(session)

    def _to_total_amount(self, quantity: Decimal, unit_price: Decimal) -> Decimal:
        return (quantity * unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _assert_rider_belongs_to_owner(self, owner_user_id: uuid.UUID, rider_profile_id: uuid.UUID) -> None:
        rider = self.rider_repo.get_by_owner_and_id(owner_user_id, rider_profile_id)
        if not rider:
            raise ValueError("Rider profile not found")

    def _get_rider_profile(self, owner_user_id: uuid.UUID, rider_profile_id: uuid.UUID) -> Optional[RiderProfile]:
        return self.rider_repo.get_by_owner_and_id(owner_user_id, rider_profile_id)

    def _build_invoice_data(self, item: RiderPurchaseItem, rider: RiderProfile) -> dict:
        total_price = Decimal(str(item.total_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "invoice_number": f"RPI-{item.created_at.strftime('%Y%m%d')}-{str(item.id)[:8].upper()}",
            "item_name": item.item_name,
            "item_code": item.item_code,
            "barcode": item.barcode,
            "category": item.category,
            "brand": item.brand,
            "quantity": Decimal(str(item.quantity)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
            "unit": item.unit,
            "unit_size": item.unit_size,
            "unit_price": Decimal(str(item.unit_price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "cost_price": item.cost_price,
            "total_amount": total_price,
            "total_price": total_price,
            "purchase_date": item.purchase_date,
            "expiry_date": item.expiry_date,
            "batch_number": item.batch_number,
            "supplier_name": item.supplier_name,
            "supplier_contact": item.supplier_contact,
            "status": item.status,
            "payment_status": item.payment_status,
            "notes": item.notes,
            "created_by": item.created_by,
            "rider": {
                "name": rider.full_name,
                "phone_number": rider.phone_number,
                "email": rider.email,
            },
            "company_name": settings.APP_NAME,
            "generated_at": datetime.utcnow(),
        }

    def generate_invoice_pdf(self, item: RiderPurchaseItem, rider: RiderProfile) -> bytes:
        invoice = self._build_invoice_data(item, rider)

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except Exception as exc:
            raise RuntimeError("Unable to load PDF renderer. Ensure reportlab is installed.") from exc

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
        )
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"<b>{invoice['company_name']}</b>", styles["Title"]))
        story.append(Paragraph(f"Rider Purchase Invoice: {invoice['invoice_number']}", styles["Normal"]))
        story.append(Paragraph(f"Purchase Date: {invoice['purchase_date']}", styles["Normal"]))
        story.append(Paragraph(f"Rider: {invoice['rider']['name']}", styles["Normal"]))
        if invoice["rider"].get("phone_number"):
            story.append(Paragraph(f"Phone: {invoice['rider']['phone_number']}", styles["Normal"]))
        if invoice["rider"].get("email"):
            story.append(Paragraph(f"Email: {invoice['rider']['email']}", styles["Normal"]))
        story.append(Spacer(1, 4 * mm))

        item_rows = [["Item", "Qty", "Unit Price", "Total"]]
        item_rows.append(
            [
                invoice["item_name"],
                f"{invoice['quantity']}",
                f"{invoice['unit_price']}",
                f"{invoice['total_amount']}",
            ]
        )

        details_rows = [["Field", "Value"]]
        for label, value in [
            ("Item Code", invoice.get("item_code")),
            ("Barcode", invoice.get("barcode")),
            ("Category", invoice.get("category")),
            ("Brand", invoice.get("brand")),
            ("Unit", invoice.get("unit")),
            ("Unit Size", invoice.get("unit_size")),
            ("Cost Price", invoice.get("cost_price")),
            ("Expiry Date", invoice.get("expiry_date")),
            ("Batch Number", invoice.get("batch_number")),
            ("Supplier Name", invoice.get("supplier_name")),
            ("Supplier Contact", invoice.get("supplier_contact")),
            ("Status", invoice.get("status")),
            ("Payment Status", invoice.get("payment_status")),
        ]:
            if value not in (None, ""):
                details_rows.append([label, f"{value}"])

        item_table = Table(item_rows, colWidths=[80 * mm, 25 * mm, 35 * mm, 35 * mm])
        item_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(item_table)
        story.append(Spacer(1, 4 * mm))

        if len(details_rows) > 1:
            details_table = Table(details_rows, colWidths=[40 * mm, 80 * mm])
            details_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            story.append(details_table)
            story.append(Spacer(1, 4 * mm))

        totals_rows = [["Total Amount", f"{invoice['total_amount']}"]]
        totals_table = Table(totals_rows, colWidths=[45 * mm, 35 * mm], hAlign="RIGHT")
        totals_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(totals_table)

        if invoice.get("notes"):
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph("<b>Notes</b>", styles["Heading4"]))
            story.append(Paragraph(str(invoice["notes"]), styles["BodyText"]))

        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(f"Generated At: {invoice['generated_at']}", styles["Normal"]))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def _send_invoice_email(self, owner_user_id: uuid.UUID, item: RiderPurchaseItem) -> None:
        rider = self._get_rider_profile(owner_user_id, item.rider_profile_id)
        if not rider or not rider.email:
            logger.info(
                "Skipping rider invoice email because rider email is missing",
                extra={"item_id": str(item.id), "rider_profile_id": str(item.rider_profile_id)},
            )
            return

        try:
            pdf_bytes = self.generate_invoice_pdf(item, rider)
        except Exception as exc:
            logger.error(
                "Failed to generate rider purchase invoice PDF",
                extra={"item_id": str(item.id), "rider_profile_id": str(item.rider_profile_id), "error": str(exc)},
            )
            return

        filename = f"rider-purchase-invoice-{item.id}.pdf"
        try:
            asyncio.run(
                EmailService.send_rider_purchase_invoice_email(
                    rider.email,
                    rider.full_name,
                    item.item_name,
                    pdf_bytes,
                    filename,
                )
            )
        except Exception as exc:
            logger.error(
                "Failed to send rider purchase invoice email",
                extra={"item_id": str(item.id), "rider_profile_id": str(item.rider_profile_id), "error": str(exc)},
            )

    def create_item(self, owner_user_id: uuid.UUID, payload: RiderPurchaseItemCreateRequest) -> RiderPurchaseItem:
        self._assert_rider_belongs_to_owner(owner_user_id, payload.rider_profile_id)

        total_amount = payload.total_price or self._to_total_amount(payload.quantity, payload.unit_price)
        item = self.item_repo.create(
            {
                "owner_user_id": owner_user_id,
                "rider_profile_id": payload.rider_profile_id,
                "item_name": payload.item_name.strip(),
                "item_code": payload.item_code,
                "barcode": payload.barcode,
                "category": payload.category,
                "brand": payload.brand,
                "quantity": payload.quantity,
                "unit": payload.unit,
                "unit_size": payload.unit_size,
                "unit_price": payload.unit_price,
                "cost_price": payload.cost_price,
                "total_amount": total_amount,
                "purchase_date": payload.purchase_date,
                "expiry_date": payload.expiry_date,
                "batch_number": payload.batch_number,
                "supplier_name": payload.supplier_name,
                "supplier_contact": payload.supplier_contact,
                "status": payload.status,
                "payment_status": payload.payment_status,
                "notes": payload.notes,
                "created_by": payload.created_by or owner_user_id,
            }
        )

        self.session.commit()
        self.session.refresh(item)
        self._send_invoice_email(owner_user_id, item)
        return item

    def list_items(self, owner_user_id: uuid.UUID, rider_profile_id: Optional[uuid.UUID] = None) -> List[RiderPurchaseItem]:
        if rider_profile_id is not None:
            self._assert_rider_belongs_to_owner(owner_user_id, rider_profile_id)
        return self.item_repo.list_by_owner(owner_user_id, rider_profile_id=rider_profile_id)

    def get_item(self, owner_user_id: uuid.UUID, item_id: uuid.UUID) -> Optional[RiderPurchaseItem]:
        return self.item_repo.get_by_owner_and_id(owner_user_id, item_id)

    def update_item(
        self,
        owner_user_id: uuid.UUID,
        item_id: uuid.UUID,
        payload: RiderPurchaseItemUpdateRequest,
    ) -> Optional[RiderPurchaseItem]:
        item = self.item_repo.get_by_owner_and_id(owner_user_id, item_id)
        if not item:
            return None

        data = payload.model_dump(exclude_unset=True)

        if "rider_profile_id" in data and data["rider_profile_id"] is not None:
            self._assert_rider_belongs_to_owner(owner_user_id, data["rider_profile_id"])

        if "item_name" in data and data["item_name"] is not None:
            data["item_name"] = data["item_name"].strip()
        if "item_code" in data and data["item_code"] is not None:
            data["item_code"] = data["item_code"].strip()
        if "barcode" in data and data["barcode"] is not None:
            data["barcode"] = data["barcode"].strip()
        if "category" in data and data["category"] is not None:
            data["category"] = data["category"].strip()
        if "brand" in data and data["brand"] is not None:
            data["brand"] = data["brand"].strip()
        if "unit" in data and data["unit"] is not None:
            data["unit"] = data["unit"].strip()
        if "batch_number" in data and data["batch_number"] is not None:
            data["batch_number"] = data["batch_number"].strip()
        if "supplier_name" in data and data["supplier_name"] is not None:
            data["supplier_name"] = data["supplier_name"].strip()
        if "supplier_contact" in data and data["supplier_contact"] is not None:
            data["supplier_contact"] = data["supplier_contact"].strip()
        if "status" in data and data["status"] is not None:
            data["status"] = data["status"].strip()
        if "payment_status" in data and data["payment_status"] is not None:
            data["payment_status"] = data["payment_status"].strip()

        quantity = data.get("quantity", item.quantity)
        unit_price = data.get("unit_price", item.unit_price)
        data["total_amount"] = data.get("total_price") or self._to_total_amount(quantity, unit_price)
        data.pop("total_price", None)

        return self.item_repo.update(item_id, data)

    def delete_item(self, owner_user_id: uuid.UUID, item_id: uuid.UUID) -> bool:
        item = self.item_repo.get_by_owner_and_id(owner_user_id, item_id)
        if not item:
            return False
        self.item_repo.soft_delete(item_id)
        return True
