from typing import Optional
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.actions.inventory_actions import InventoryActions
from app.api.v1.schemas.inventory_schema import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    ProductCreateRequest,
    ProductUpdateRequest,
    UnitCreateRequest,
    UnitUpdateRequest,
)
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User


class InventoryHandler:
    @staticmethod
    def create_category(
        payload: CategoryCreateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.create_category(payload, session, current_user)

    @staticmethod
    def list_categories(
        is_active: Optional[bool] = Query(None),
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.list_categories(session, current_user, is_active=is_active)

    @staticmethod
    def get_category(
        category_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.get_category(category_id, session, current_user)

    @staticmethod
    def update_category(
        category_id: UUID,
        payload: CategoryUpdateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.update_category(category_id, payload, session, current_user)

    @staticmethod
    def delete_category(
        category_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.delete_category(category_id, session, current_user)

    @staticmethod
    def create_unit(
        payload: UnitCreateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.create_unit(payload, session, current_user)

    @staticmethod
    def list_units(
        is_active: Optional[bool] = Query(None),
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.list_units(session, current_user, is_active=is_active)

    @staticmethod
    def get_unit(
        unit_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.get_unit(unit_id, session, current_user)

    @staticmethod
    def update_unit(
        unit_id: UUID,
        payload: UnitUpdateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.update_unit(unit_id, payload, session, current_user)

    @staticmethod
    def delete_unit(
        unit_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.delete_unit(unit_id, session, current_user)

    @staticmethod
    def create_product(
        payload: ProductCreateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.create_product(payload, session, current_user)

    @staticmethod
    def list_products(
        is_active: Optional[bool] = Query(None),
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.list_products(session, current_user, is_active=is_active)

    @staticmethod
    def get_product(
        product_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.get_product(product_id, session, current_user)

    @staticmethod
    def update_product(
        product_id: UUID,
        payload: ProductUpdateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.update_product(product_id, payload, session, current_user)

    @staticmethod
    def delete_product(
        product_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return InventoryActions.delete_product(product_id, session, current_user)

