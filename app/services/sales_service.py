from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.api.v1.schemas.sales_schema import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    SaleCreateRequest,
    SalePaymentCreateRequest,
)
from app.models.inventory import Product, StockBatch, StockMovement, Unit
from app.models.sales import (
    Customer,
    Sale,
    SaleItem,
    SaleItemBatchAllocation,
    SalePayment,
)
from app.repos.sales_repository import (
    CustomerRepository,
    SaleItemBatchAllocationRepository,
    SaleItemRepository,
    SalePaymentRepository,
    SaleRepository,
)
from app.core.config import settings


class SalesService:
    def __init__(self, session: Session):
        self.session = session
        self.customer_repo = CustomerRepository(Customer, session)
        self.sale_repo = SaleRepository(Sale, session)
        self.sale_item_repo = SaleItemRepository(SaleItem, session)
        self.sale_payment_repo = SalePaymentRepository(SalePayment, session)
        self.sale_item_batch_allocation_repo = SaleItemBatchAllocationRepository(SaleItemBatchAllocation, session)

    @staticmethod
    def _q2(value: Decimal) -> Decimal:
        """Quantize to 2 decimal places for currency."""
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _q3(value: Decimal) -> Decimal:
        """Quantize to 3 decimal places for quantities."""
        return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    def _determine_payment_status(self, paid_amount: Decimal, remaining_amount: Decimal) -> str:
        """Determine payment status based on amounts."""
        if remaining_amount <= Decimal("0"):
            return "paid"
        elif paid_amount > Decimal("0"):
            return "partially_paid"
        else:
            return "unpaid"

    def _assert_customer_exists(self, customer_id: UUID) -> Customer:
        """Validate customer exists."""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        return customer

    def _assert_product_exists(self, product_id: UUID) -> Product:
        """Validate product exists and is active."""
        product = self.session.query(Product).filter(
            Product.id == product_id,
            Product.deleted_at.is_(None),
            Product.is_active.is_(True)
        ).first()
        if not product:
            raise ValueError("Product not found or not active")
        return product

    def _assert_unit_exists(self, unit_id: UUID) -> Unit:
        """Validate unit exists."""
        unit = self.session.query(Unit).filter(
            Unit.id == unit_id,
            Unit.deleted_at.is_(None)
        ).first()
        if not unit:
            raise ValueError("Unit not found")
        return unit

    def _get_available_batches(self, product_id: UUID) -> List[StockBatch]:
        """Get all available stock batches for a product in FIFO order."""
        query = select(StockBatch).where(
            and_(
                StockBatch.product_id == product_id,
                StockBatch.quantity_available > Decimal("0")
            )
        ).order_by(StockBatch.created_at)
        batches = self.session.execute(query).scalars().all()
        return batches

    def _next_sale_number(self) -> str:
        """Generate next sale number."""
        today = date.today()
        date_str = today.strftime("%Y%m%d")
        
        query = select(func.count(Sale.id)).where(
            Sale.sale_number.startswith(f"SAL-{date_str}")
        )
        count = self.session.execute(query).scalar() or 0
        return f"SAL-{date_str}-{count + 1:05d}"

    def _recalculate_customer_balance(self, customer_id: UUID) -> Decimal:
        """
        Recalculate customer current balance.
        Formula: opening_balance + sum(remaining_amount for non-cancelled sales)
        """
        customer = self._assert_customer_exists(customer_id)
        
        query = select(func.sum(Sale.remaining_amount)).where(
            and_(
                Sale.customer_id == customer_id,
                Sale.status != "cancelled",
                Sale.deleted_at.is_(None)
            )
        )
        total_remaining = self.session.execute(query).scalar() or Decimal("0")
        
        current_balance = customer.opening_balance + self._q2(total_remaining)
        
        # Update customer balance
        customer.current_balance = current_balance
        self.session.flush()
        
        return current_balance

    # ========================================================================
    # CUSTOMER OPERATIONS
    # ========================================================================

    def create_customer(self, req: CustomerCreateRequest) -> Customer:
        """Create a new customer."""
        customer = Customer(
            name=req.name,
            phone=req.phone,
            email=req.email,
            address=req.address,
            city=req.city,
            opening_balance=self._q2(Decimal(str(req.opening_balance))),
            current_balance=self._q2(Decimal(str(req.opening_balance))),
            customer_type=req.customer_type,
            notes=req.notes,
            is_active=True,
        )
        return self.customer_repo.create(customer)

    def get_customer_by_id(self, customer_id: UUID) -> Optional[Customer]:
        """Get customer by ID."""
        return self.customer_repo.get_by_id(customer_id)

    def list_customers(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """List all customers."""
        query = select(Customer).where(
            Customer.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        return self.session.execute(query).scalars().all()

    def update_customer(self, customer_id: UUID, req: CustomerUpdateRequest) -> Customer:
        """Update customer."""
        customer = self._assert_customer_exists(customer_id)
        
        if req.name is not None:
            customer.name = req.name
        if req.phone is not None:
            customer.phone = req.phone
        if req.email is not None:
            customer.email = req.email
        if req.address is not None:
            customer.address = req.address
        if req.city is not None:
            customer.city = req.city
        if req.opening_balance is not None:
            customer.opening_balance = self._q2(Decimal(str(req.opening_balance)))
        if req.customer_type is not None:
            customer.customer_type = req.customer_type
        if req.notes is not None:
            customer.notes = req.notes
        
        self.session.flush()
        self.session.refresh(customer)
        return customer

    # ========================================================================
    # SALE OPERATIONS
    # ========================================================================

    def create_sale(self, req: SaleCreateRequest, created_by: Optional[UUID] = None) -> Sale:
        """
        Create a new sale with full FIFO stock allocation and balance updates.
        
        Process:
        1. Validate customer, products, units
        2. Calculate line totals and sale totals (backend only)
        3. Allocate stock using FIFO
        4. Create Sale header, SaleItems, StockMovements, SaleItemBatchAllocations
        5. Create initial payment if paid_amount > 0
        6. Recalculate customer balance
        """
        
        # Validate customer exists
        customer = self._assert_customer_exists(UUID(req.customer_id))
        
        # Validate all items
        if not req.items or len(req.items) == 0:
            raise ValueError("Sale must contain at least one item")
        
        for item in req.items:
            if item.quantity <= 0:
                raise ValueError("Item quantity must be greater than 0")
            if item.unit_price <= 0:
                raise ValueError("Item unit price must be greater than 0")
            product = self._assert_product_exists(UUID(item.product_id))
            self._assert_unit_exists(UUID(item.unit_id))
        
        # Calculate totals
        subtotal = Decimal("0")
        discount_total = Decimal("0")
        tax_total = Decimal("0")
        
        item_calculations = []
        for item in req.items:
            quantity = self._q3(Decimal(str(item.quantity)))
            unit_price = self._q2(Decimal(str(item.unit_price)))
            discount_value = self._q2(Decimal(str(item.discount_value)))
            tax_percent = self._q2(Decimal(str(item.tax_percent)))
            
            # Per item calculation
            base_total = self._q2(quantity * unit_price)
            
            # Discount calculation
            if item.discount_type == "flat":
                discount_amount = discount_value
            elif item.discount_type == "percent":
                discount_amount = self._q2(base_total * (discount_value / Decimal("100")))
            else:
                discount_amount = Decimal("0")
            
            # Tax calculation
            tax_amount = self._q2((base_total - discount_amount) * tax_percent / Decimal("100"))
            
            # Line total
            line_total = self._q2(base_total - discount_amount + tax_amount)
            
            subtotal = self._q2(subtotal + base_total)
            discount_total = self._q2(discount_total + discount_amount)
            tax_total = self._q2(tax_total + tax_amount)
            
            item_calculations.append({
                "item": item,
                "base_total": base_total,
                "discount_amount": discount_amount,
                "tax_amount": tax_amount,
                "line_total": line_total,
                "quantity": quantity,
                "unit_price": unit_price,
            })
        
        # Sale totals
        other_charges = self._q2(Decimal(str(req.other_charges)))
        grand_total = self._q2(subtotal - discount_total + tax_total + other_charges)
        paid_amount = self._q2(Decimal(str(req.paid_amount)))
        remaining_amount = self._q2(grand_total - paid_amount)
        payment_status = self._determine_payment_status(paid_amount, remaining_amount)
        
        # Validate stock availability
        for calc in item_calculations:
            product = self._assert_product_exists(UUID(calc["item"].product_id))
            if product.track_inventory:
                available_batches = self._get_available_batches(product.id)
                total_available = sum(b.quantity_available for b in available_batches)
                if total_available < calc["quantity"]:
                    raise ValueError(
                        f"Insufficient stock for {product.name}. "
                        f"Required: {calc['quantity']}, Available: {total_available}"
                    )
        
        # Create sale header
        sale_number = self._next_sale_number()
        sale = Sale(
            sale_number=sale_number,
            customer_id=customer.id,
            sale_date=req.sale_date,
            invoice_number=req.invoice_number,
            payment_method=req.payment_method,
            payment_status=payment_status,
            subtotal=subtotal,
            discount_total=discount_total,
            tax_total=tax_total,
            other_charges=other_charges,
            grand_total=grand_total,
            paid_amount=paid_amount,
            remaining_amount=remaining_amount,
            notes=req.notes,
            status="posted",
            created_by=created_by,
        )
        self.session.add(sale)
        self.session.flush()
        self.session.refresh(sale)
        
        # Create sale items, allocations, and stock movements
        for calc in item_calculations:
            item_req = calc["item"]
            product = self._assert_product_exists(UUID(item_req.product_id))
            unit = self._assert_unit_exists(UUID(item_req.unit_id))
            
            # Create sale item
            cost_price_snapshot = self._q2(product.default_purchase_price)
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                sku_snapshot=product.sku,
                barcode_snapshot=product.barcode,
                unit_id=unit.id,
                quantity=calc["quantity"],
                unit_price=calc["unit_price"],
                cost_price_snapshot=cost_price_snapshot,
                discount_type=item_req.discount_type,
                discount_value=calc["discount_amount"],
                discount_amount=calc["discount_amount"],
                tax_percent=Decimal(str(item_req.tax_percent)),
                tax_amount=calc["tax_amount"],
                line_total=calc["line_total"],
                notes=item_req.notes,
            )
            self.session.add(sale_item)
            self.session.flush()
            self.session.refresh(sale_item)
            
            # FIFO stock allocation and movement creation
            if product.track_inventory:
                quantity_to_deduct = calc["quantity"]
                available_batches = self._get_available_batches(product.id)
                
                for batch in available_batches:
                    if quantity_to_deduct <= Decimal("0"):
                        break
                    
                    # Allocate quantity
                    allocated_qty = self._q3(min(quantity_to_deduct, batch.quantity_available))
                    
                    # Create batch allocation
                    allocation = SaleItemBatchAllocation(
                        sale_item_id=sale_item.id,
                        stock_batch_id=batch.id,
                        quantity_allocated=allocated_qty,
                        unit_cost=batch.unit_cost,
                    )
                    self.session.add(allocation)
                    self.session.flush()
                    
                    # Create stock movement
                    movement = StockMovement(
                        product_id=product.id,
                        purchase_item_id=None,
                        stock_batch_id=batch.id,
                        movement_type="sale_out",
                        reference_type="sale",
                        reference_id=sale.id,
                        quantity_in=Decimal("0"),
                        quantity_out=allocated_qty,
                        unit_cost=batch.unit_cost,
                        movement_date=datetime.utcnow().date(),
                    )
                    self.session.add(movement)
                    
                    # Reduce batch quantity
                    batch.quantity_available = self._q3(batch.quantity_available - allocated_qty)
                    
                    quantity_to_deduct = self._q3(quantity_to_deduct - allocated_qty)
                    self.session.flush()
        
        # Create initial payment if paid_amount > 0
        if paid_amount > Decimal("0"):
            payment = SalePayment(
                sale_id=sale.id,
                customer_id=customer.id,
                payment_date=req.sale_date,
                amount=paid_amount,
                payment_method=req.payment_method,
            )
            self.session.add(payment)
            self.session.flush()
        
        # Recalculate customer balance
        self._recalculate_customer_balance(customer.id)
        
        self.session.commit()
        
        # Reload sale with relationships
        return self.sale_repo.get_with_relations(sale.id)

    def get_sale_by_id(self, sale_id: UUID) -> Optional[Sale]:
        """Get sale with all relationships."""
        return self.sale_repo.get_with_relations(sale_id)

    def get_printable_invoice_data(self, sale_id: UUID) -> dict:
        """Return sale invoice payload optimized for printing."""
        sale = self.sale_repo.get_with_relations(sale_id)
        if not sale:
            raise ValueError("Sale not found")

        items = []
        for item in sale.items or []:
            items.append(
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name_snapshot,
                    "sku": item.sku_snapshot,
                    "barcode": item.barcode_snapshot,
                    "quantity": self._q3(item.quantity),
                    "unit_price": self._q2(item.unit_price),
                    "discount_amount": self._q2(item.discount_amount),
                    "tax_amount": self._q2(item.tax_amount),
                    "line_total": self._q2(item.line_total),
                }
            )

        payments = []
        for payment in sale.payments or []:
            payments.append(
                {
                    "payment_date": payment.payment_date,
                    "amount": self._q2(payment.amount),
                    "payment_method": payment.payment_method,
                    "reference_number": payment.reference_number,
                }
            )

        return {
            "sale_id": sale.id,
            "sale_number": sale.sale_number,
            "invoice_number": sale.invoice_number,
            "sale_date": sale.sale_date,
            "status": sale.status,
            "payment_status": sale.payment_status,
            "payment_method": sale.payment_method,
            "customer": {
                "id": sale.customer.id,
                "name": sale.customer.name,
                "phone": sale.customer.phone,
                "email": sale.customer.email,
                "address": sale.customer.address,
                "city": sale.customer.city,
                "customer_type": sale.customer.customer_type,
            },
            "items": items,
            "payments": sorted(payments, key=lambda p: p["payment_date"]),
            "subtotal": self._q2(sale.subtotal),
            "discount_total": self._q2(sale.discount_total),
            "tax_total": self._q2(sale.tax_total),
            "other_charges": self._q2(sale.other_charges),
            "grand_total": self._q2(sale.grand_total),
            "paid_amount": self._q2(sale.paid_amount),
            "remaining_amount": self._q2(sale.remaining_amount),
            "notes": sale.notes,
            "company_name": settings.APP_NAME,
            "generated_at": datetime.utcnow(),
        }

    def generate_invoice_pdf(self, sale_id: UUID) -> bytes:
        """Generate PDF bytes for the sale invoice."""
        invoice = self.get_printable_invoice_data(sale_id)

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
        story.append(Paragraph(f"Invoice: {invoice['invoice_number'] or invoice['sale_number']}", styles["Normal"]))
        story.append(Paragraph(f"Sale Number: {invoice['sale_number']}", styles["Normal"]))
        story.append(Paragraph(f"Sale Date: {invoice['sale_date']}", styles["Normal"]))
        story.append(Paragraph(f"Customer: {invoice['customer']['name']}", styles["Normal"]))
        if invoice["customer"].get("phone"):
            story.append(Paragraph(f"Phone: {invoice['customer']['phone']}", styles["Normal"]))
        story.append(Spacer(1, 4 * mm))

        item_rows = [["Item", "Qty", "Unit Price", "Discount", "Tax", "Line Total"]]
        for item in invoice["items"]:
            item_rows.append(
                [
                    item["product_name"],
                    f"{item['quantity']}",
                    f"{item['unit_price']}",
                    f"{item['discount_amount']}",
                    f"{item['tax_amount']}",
                    f"{item['line_total']}",
                ]
            )

        item_table = Table(item_rows, colWidths=[62 * mm, 16 * mm, 24 * mm, 24 * mm, 18 * mm, 24 * mm])
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

        totals_rows = [
            ["Subtotal", f"{invoice['subtotal']}"],
            ["Discount", f"{invoice['discount_total']}"],
            ["Tax", f"{invoice['tax_total']}"],
            ["Other Charges", f"{invoice['other_charges']}"],
            ["Grand Total", f"{invoice['grand_total']}"],
            ["Paid", f"{invoice['paid_amount']}"],
            ["Remaining", f"{invoice['remaining_amount']}"],
        ]
        totals_table = Table(totals_rows, colWidths=[45 * mm, 35 * mm], hAlign="RIGHT")
        totals_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                    ("FONTNAME", (0, 4), (-1, 4), "Helvetica-Bold"),
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

    def list_sales(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[UUID] = None,
        payment_status: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Sale]:
        """List sales with filters."""
        return self.sale_repo.list_with_relations(
            skip=skip,
            limit=limit,
            customer_id=customer_id,
            payment_status=payment_status,
            status=status,
        )

    def add_sale_payment(self, sale_id: UUID, req: SalePaymentCreateRequest) -> Sale:
        """
        Add payment to an existing sale.
        
        Updates:
        - paid_amount
        - remaining_amount
        - payment_status
        - customer current_balance
        """
        sale = self.sale_repo.get_with_relations(sale_id)
        if not sale:
            raise ValueError("Sale not found")
        
        if sale.status == "cancelled":
            raise ValueError("Cannot add payment to cancelled sale")
        
        if req.amount <= Decimal("0"):
            raise ValueError("Payment amount must be greater than 0")
        
        # Create payment record
        payment = SalePayment(
            sale_id=sale.id,
            customer_id=sale.customer_id,
            payment_date=req.payment_date,
            amount=self._q2(Decimal(str(req.amount))),
            payment_method=req.payment_method,
            reference_number=req.reference_number,
            notes=req.notes,
        )
        self.session.add(payment)
        self.session.flush()
        
        # Update sale totals
        sale.paid_amount = self._q2(sale.paid_amount + payment.amount)
        sale.remaining_amount = self._q2(sale.grand_total - sale.paid_amount)
        sale.payment_status = self._determine_payment_status(sale.paid_amount, sale.remaining_amount)
        
        self.session.flush()
        
        # Recalculate customer balance
        self._recalculate_customer_balance(sale.customer_id)
        
        self.session.commit()
        
        # Reload sale with relationships
        return self.sale_repo.get_with_relations(sale_id)

    def cancel_sale(self, sale_id: UUID) -> Sale:
        """
        Cancel a sale and restore stock.
        
        Process:
        1. Get all allocations for the sale
        2. Reverse stock deductions for each batch
        3. Remove stock movements for this sale
        4. Update sale status to cancelled
        5. Recalculate customer balance
        """
        sale = self.sale_repo.get_with_relations(sale_id)
        if not sale:
            raise ValueError("Sale not found")
        
        if sale.status == "cancelled":
            raise ValueError("Sale is already cancelled")
        
        # Restore stock for all allocations
        if sale.items:
            for sale_item in sale.items:
                if sale_item.batch_allocations:
                    for allocation in sale_item.batch_allocations:
                        batch = self.session.query(StockBatch).filter(
                            StockBatch.id == allocation.stock_batch_id
                        ).first()
                        if batch:
                            batch.quantity_available = self._q3(
                                batch.quantity_available + allocation.quantity_allocated
                            )
        
        # Remove stock movements for this sale
        move_query = select(StockMovement).where(
            and_(
                StockMovement.reference_type == "sale",
                StockMovement.reference_id == sale_id,
            )
        )
        movements = self.session.execute(move_query).scalars().all()
        for movement in movements:
            self.session.delete(movement)
        
        # Update sale status
        sale.status = "cancelled"
        self.session.flush()
        
        # Recalculate customer balance
        self._recalculate_customer_balance(sale.customer_id)
        
        self.session.commit()
        
        # Reload sale
        return self.sale_repo.get_with_relations(sale_id)

    # ========================================================================
    # DEFAULT CUSTOMER
    # ========================================================================

    def get_or_create_walk_in_customer(self) -> Customer:
        """Get or create default walk-in customer."""
        existing = self.customer_repo.get_walk_in_customer()
        if existing:
            return existing
        
        req = CustomerCreateRequest(
            name="Walk-in Customer",
            customer_type="walk_in",
            opening_balance=Decimal("0"),
        )
        return self.create_customer(req)
