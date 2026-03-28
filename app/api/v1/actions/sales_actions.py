from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

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
from app.services.sales_service import SalesService


class SalesActions:
    """Actions for sales module."""

    def __init__(self, db: Session):
        self.sales_service = SalesService(db)

    # ====================================================================
    # CUSTOMER ACTIONS
    # ====================================================================

    def create_customer(self, req: CustomerCreateRequest) -> CustomerResponse:
        """Create a new customer."""
        customer = self.sales_service.create_customer(req)
        return CustomerResponse.model_validate(customer)

    def get_customer(self, customer_id: UUID) -> Optional[CustomerResponse]:
        """Get customer by ID."""
        customer = self.sales_service.get_customer_by_id(customer_id)
        if not customer:
            return None
        return CustomerResponse.model_validate(customer)

    def list_customers(self, skip: int = 0, limit: int = 100) -> List[CustomerResponse]:
        """List all customers."""
        customers = self.sales_service.list_customers(skip=skip, limit=limit)
        return [CustomerResponse.model_validate(c) for c in customers]

    def update_customer(self, customer_id: UUID, req: CustomerUpdateRequest) -> CustomerResponse:
        """Update a customer."""
        customer = self.sales_service.update_customer(customer_id, req)
        return CustomerResponse.model_validate(customer)

    # ====================================================================
    # SALE ACTIONS
    # ====================================================================

    def create_sale(
        self,
        req: SaleCreateRequest,
        created_by: Optional[UUID] = None,
    ) -> SaleResponse:
        """Create a new sale."""
        sale = self.sales_service.create_sale(req, created_by=created_by)
        return SaleResponse.model_validate(sale)

    def get_sale(self, sale_id: UUID) -> Optional[SaleResponse]:
        """Get sale by ID."""
        sale = self.sales_service.get_sale_by_id(sale_id)
        if not sale:
            return None
        return SaleResponse.model_validate(sale)

    def list_sales(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[UUID] = None,
        payment_status: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[SaleListResponse]:
        """List sales."""
        sales = self.sales_service.list_sales(
            skip=skip,
            limit=limit,
            customer_id=customer_id,
            payment_status=payment_status,
            status=status,
        )
        return [SaleListResponse.model_validate(s) for s in sales]

    def add_sale_payment(
        self,
        sale_id: UUID,
        req: SalePaymentCreateRequest,
    ) -> SaleResponse:
        """Add payment to sale."""
        sale = self.sales_service.add_sale_payment(sale_id, req)
        return SaleResponse.model_validate(sale)

    def cancel_sale(self, sale_id: UUID) -> SaleResponse:
        """Cancel a sale."""
        sale = self.sales_service.cancel_sale(sale_id)
        return SaleResponse.model_validate(sale)

    def get_printable_invoice(self, sale_id: UUID) -> PrintableInvoiceResponse:
        """Get printable invoice payload for a sale."""
        invoice = self.sales_service.get_printable_invoice_data(sale_id)
        return PrintableInvoiceResponse.model_validate(invoice)

    def get_invoice_pdf(self, sale_id: UUID) -> bytes:
        """Get invoice PDF bytes for a sale."""
        return self.sales_service.generate_invoice_pdf(sale_id)

    # ====================================================================
    # DEFAULTS
    # ====================================================================

    def get_or_create_walk_in_customer(self) -> CustomerResponse:
        """Get or create walk-in customer."""
        customer = self.sales_service.get_or_create_walk_in_customer()
        return CustomerResponse.model_validate(customer)
