from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.api.v1.actions.sales_actions import SalesActions
from app.api.v1.schemas.sales_schema import (
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    SaleCreateRequest,
    SaleListResponse,
    SalePaymentCreateRequest,
    SalePaymentResponse,
    SaleResponse,
    PrintableInvoiceResponse,
)


class SalesHandler:
    """Handler for sales module request/response orchestration."""

    def __init__(self, db: Session):
        self.actions = SalesActions(db)

    # ====================================================================
    # CUSTOMER HANDLERS
    # ====================================================================

    def handle_create_customer(self, req: CustomerCreateRequest) -> CustomerResponse:
        """Handle customer creation."""
        return self.actions.create_customer(req)

    def handle_get_customer(self, customer_id: UUID) -> Optional[CustomerResponse]:
        """Handle get customer."""
        return self.actions.get_customer(customer_id)

    def handle_list_customers(self, skip: int = 0, limit: int = 100) -> List[CustomerResponse]:
        """Handle list customers."""
        return self.actions.list_customers(skip=skip, limit=limit)

    def handle_update_customer(self, customer_id: UUID, req: CustomerUpdateRequest) -> CustomerResponse:
        """Handle update customer."""
        return self.actions.update_customer(customer_id, req)

    # ====================================================================
    # SALE HANDLERS
    # ====================================================================

    def handle_create_sale(
        self,
        req: SaleCreateRequest,
        created_by: Optional[UUID] = None,
    ) -> SaleResponse:
        """Handle sale creation."""
        return self.actions.create_sale(req, created_by=created_by)

    def handle_get_sale(self, sale_id: UUID) -> Optional[SaleResponse]:
        """Handle get sale."""
        return self.actions.get_sale(sale_id)

    def handle_get_printable_invoice(self, sale_id: UUID) -> PrintableInvoiceResponse:
        """Handle get printable invoice."""
        return self.actions.get_printable_invoice(sale_id)

    def handle_get_invoice_pdf(self, sale_id: UUID) -> bytes:
        """Handle get invoice PDF bytes."""
        return self.actions.get_invoice_pdf(sale_id)

    def handle_list_sales(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[UUID] = None,
        payment_status: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[SaleListResponse]:
        """Handle list sales."""
        return self.actions.list_sales(
            skip=skip,
            limit=limit,
            customer_id=customer_id,
            payment_status=payment_status,
            status=status,
        )

    def handle_add_sale_payment(
        self,
        sale_id: UUID,
        req: SalePaymentCreateRequest,
    ) -> SaleResponse:
        """Handle adding payment to sale."""
        return self.actions.add_sale_payment(sale_id, req)

    def handle_cancel_sale(self, sale_id: UUID) -> SaleResponse:
        """Handle sale cancellation."""
        return self.actions.cancel_sale(sale_id)

    # ====================================================================
    # DEFAULT HANDLERS
    # ====================================================================

    def handle_get_or_create_walk_in_customer(self) -> CustomerResponse:
        """Handle get or create walk-in customer."""
        return self.actions.get_or_create_walk_in_customer()
