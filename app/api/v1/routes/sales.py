from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.api.v1.handlers.sales_handler import SalesHandler
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
from app.api.v1.schemas.common_schema import StandardResponse
from app.core.dependencies import get_db
from app.core.response import success_response
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sales", tags=["Sales"])


def get_sales_handler(db: Session = Depends(get_db)) -> SalesHandler:
    """Get sales handler instance."""
    return SalesHandler(db)


# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================


@router.post("/customers", response_model=StandardResponse[CustomerResponse], status_code=status.HTTP_201_CREATED)
def create_customer(
    req: CustomerCreateRequest,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Create a new customer."""
    try:
        customer = handler.handle_create_customer(req)
        return success_response(data=customer, message="Customer created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customers", response_model=StandardResponse[List[CustomerResponse]], status_code=status.HTTP_200_OK)
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    handler: SalesHandler = Depends(get_sales_handler),
):
    """List all customers."""
    customers = handler.handle_list_customers(skip=skip, limit=limit)
    return success_response(data=customers, message="Customers retrieved successfully")


@router.get("/customers/{customer_id}", response_model=StandardResponse[CustomerResponse], status_code=status.HTTP_200_OK)
def get_customer(
    customer_id: UUID,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Get customer by ID."""
    customer = handler.handle_get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return success_response(data=customer, message="Customer retrieved successfully")


@router.put("/customers/{customer_id}", response_model=StandardResponse[CustomerResponse], status_code=status.HTTP_200_OK)
def update_customer(
    customer_id: UUID,
    req: CustomerUpdateRequest,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Update customer."""
    try:
        customer = handler.handle_update_customer(customer_id, req)
        return success_response(data=customer, message="Customer updated successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# SALE ENDPOINTS
# ============================================================================


@router.post("/sales", response_model=StandardResponse[SaleResponse], status_code=status.HTTP_201_CREATED)
def create_sale(
    req: SaleCreateRequest,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Create a new sale."""
    try:
        sale = handler.handle_create_sale(req)
        return success_response(data=sale, message="Sale created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sales", response_model=StandardResponse[List[SaleListResponse]], status_code=status.HTTP_200_OK)
def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[UUID] = Query(None),
    payment_status: Optional[str] = Query(None),
    sale_status: Optional[str] = Query(None),
    handler: SalesHandler = Depends(get_sales_handler),
):
    """List sales with optional filters."""
    sales = handler.handle_list_sales(
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        payment_status=payment_status,
        status=sale_status,
    )
    return success_response(data=sales, message="Sales retrieved successfully")


@router.get("/sales/{sale_id}", response_model=StandardResponse[SaleResponse], status_code=status.HTTP_200_OK)
def get_sale(
    sale_id: UUID,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Get sale by ID."""
    sale = handler.handle_get_sale(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return success_response(data=sale, message="Sale retrieved successfully")


@router.get("/sales/{sale_id}/invoice", response_model=StandardResponse[PrintableInvoiceResponse], status_code=status.HTTP_200_OK)
def get_sale_invoice(
    sale_id: UUID,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Get printable invoice data for a sale."""
    try:
        invoice = handler.handle_get_printable_invoice(sale_id)
        return success_response(data=invoice, message="Invoice data retrieved successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sales/{sale_id}/invoice/pdf", status_code=status.HTTP_200_OK)
def get_sale_invoice_pdf(
    sale_id: UUID,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Get invoice PDF file for a sale."""
    try:
        pdf_bytes = handler.handle_get_invoice_pdf(sale_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=invoice-{sale_id}.pdf"
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SALE PAYMENT ENDPOINTS
# ============================================================================


@router.post("/sales/{sale_id}/payments", response_model=StandardResponse[SaleResponse], status_code=status.HTTP_201_CREATED)
def add_sale_payment(
    sale_id: UUID,
    req: SalePaymentCreateRequest,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Add payment to sale."""
    try:
        sale = handler.handle_add_sale_payment(sale_id, req)
        return success_response(data=sale, message="Payment recorded successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# SALE CANCELLATION
# ============================================================================


@router.post("/sales/{sale_id}/cancel", response_model=StandardResponse[SaleResponse], status_code=status.HTTP_200_OK)
def cancel_sale(
    sale_id: UUID,
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Cancel a sale and restore stock."""
    try:
        sale = handler.handle_cancel_sale(sale_id)
        return success_response(data=sale, message="Sale cancelled successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# DEFAULT CUSTOMER
# ============================================================================


@router.post("/customers/walk-in/init", response_model=StandardResponse[CustomerResponse], status_code=status.HTTP_200_OK)
def init_walk_in_customer(
    handler: SalesHandler = Depends(get_sales_handler),
):
    """Create or get walk-in customer for walk-in sales."""
    customer = handler.handle_get_or_create_walk_in_customer()
    return success_response(data=customer, message="Walk-in customer initialized successfully")
