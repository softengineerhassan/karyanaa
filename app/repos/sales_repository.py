from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
import uuid

from app.models.sales import (
    Customer,
    Sale,
    SaleItem,
    SalePayment,
    SaleItemBatchAllocation,
)
from app.repos.base import GenericRepository


class CustomerRepository(GenericRepository[Customer]):
    """Repository for Customer model."""

    def get_by_phone(self, phone: str, include_deleted: bool = False) -> Optional[Customer]:
        """Get customer by phone number."""
        query = select(self.model).where(self.model.phone == phone)
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        result = self.session.execute(query).scalar_one_or_none()
        return result

    def get_walk_in_customer(self) -> Optional[Customer]:
        """Get the default walk-in customer."""
        query = select(self.model).where(
            self.model.customer_type == "walk_in"
        ).where(
            self.model.name == "Walk-in Customer"
        ).where(
            self.model.deleted_at.is_(None)
        )
        return self.session.execute(query).scalar_one_or_none()


class SaleRepository(GenericRepository[Sale]):
    """Repository for Sale model."""

    def list_with_relations(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[uuid.UUID] = None,
        payment_status: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Sale]:
        """List sales with eager-loaded relationships."""
        query = select(self.model).where(self.model.deleted_at.is_(None))

        if customer_id:
            query = query.where(self.model.customer_id == customer_id)
        if payment_status:
            query = query.where(self.model.payment_status == payment_status)
        if status:
            query = query.where(self.model.status == status)

        query = (
            query.options(selectinload(self.model.items))
            .options(selectinload(self.model.payments))
            .options(selectinload(self.model.customer))
            .offset(skip)
            .limit(limit)
        )
        results = self.session.execute(query).unique().scalars().all()
        return results

    def get_with_relations(self, id: uuid.UUID) -> Optional[Sale]:
        """Get single sale with eager-loaded relationships."""
        query = (
            select(self.model)
            .where(self.model.id == id)
            .where(self.model.deleted_at.is_(None))
            .options(selectinload(self.model.items))
            .options(selectinload(self.model.payments))
            .options(selectinload(self.model.customer))
        )
        result = self.session.execute(query).scalar_one_or_none()
        return result

    def get_by_sale_number(self, sale_number: str) -> Optional[Sale]:
        """Get sale by sale number."""
        query = select(self.model).where(
            self.model.sale_number == sale_number
        ).where(
            self.model.deleted_at.is_(None)
        )
        return self.session.execute(query).scalar_one_or_none()


class SaleItemRepository(GenericRepository[SaleItem]):
    """Repository for SaleItem model."""

    def get_by_sale_id(self, sale_id: uuid.UUID) -> List[SaleItem]:
        """Get all items for a sale."""
        query = (
            select(self.model)
            .where(self.model.sale_id == sale_id)
            .where(self.model.deleted_at.is_(None))
            .options(selectinload(self.model.batch_allocations))
        )
        return self.session.execute(query).scalars().all()


class SalePaymentRepository(GenericRepository[SalePayment]):
    """Repository for SalePayment model."""

    def get_by_sale_id(self, sale_id: uuid.UUID) -> List[SalePayment]:
        """Get all payments for a sale."""
        query = select(self.model).where(
            self.model.sale_id == sale_id
        ).where(
            self.model.deleted_at.is_(None)
        )
        return self.session.execute(query).scalars().all()


class SaleItemBatchAllocationRepository(GenericRepository[SaleItemBatchAllocation]):
    """Repository for SaleItemBatchAllocation model."""

    def get_by_sale_item_id(self, sale_item_id: uuid.UUID) -> List[SaleItemBatchAllocation]:
        """Get all batch allocations for a sale item."""
        query = select(self.model).where(
            self.model.sale_item_id == sale_item_id
        )
        return self.session.execute(query).scalars().all()
