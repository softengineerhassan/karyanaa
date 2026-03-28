from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.inventory_schema import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
    UnitCreateRequest,
    UnitResponse,
    UnitUpdateRequest,
)
from app.core.response import success_response
from app.models.user import User
from app.services.inventory_service import InventoryService


class InventoryActions:
    @staticmethod
    def create_category(payload: CategoryCreateRequest, session: Session, current_user: User):
        service = InventoryService(session)
        try:
            category = service.create_category(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        return success_response(data=CategoryResponse.model_validate(category), message="Category created successfully")

    @staticmethod
    def list_categories(session: Session, current_user: User, is_active: Optional[bool] = None):
        service = InventoryService(session)
        data = [CategoryResponse.model_validate(item) for item in service.list_categories(is_active=is_active)]
        return success_response(data=data, message="Categories fetched successfully")

    @staticmethod
    def get_category(category_id: UUID, session: Session, current_user: User):
        service = InventoryService(session)
        category = service.get_category(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return success_response(data=CategoryResponse.model_validate(category), message="Category fetched successfully")

    @staticmethod
    def update_category(category_id: UUID, payload: CategoryUpdateRequest, session: Session, current_user: User):
        service = InventoryService(session)
        try:
            category = service.update_category(category_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return success_response(data=CategoryResponse.model_validate(category), message="Category updated successfully")

    @staticmethod
    def delete_category(category_id: UUID, session: Session, current_user: User):
        service = InventoryService(session)
        if not service.delete_category(category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return success_response(message="Category deleted successfully")

    @staticmethod
    def create_unit(payload: UnitCreateRequest, session: Session, current_user: User):
        service = InventoryService(session)
        unit = service.create_unit(payload)
        return success_response(data=UnitResponse.model_validate(unit), message="Unit created successfully")

    @staticmethod
    def list_units(session: Session, current_user: User, is_active: Optional[bool] = None):
        service = InventoryService(session)
        data = [UnitResponse.model_validate(item) for item in service.list_units(is_active=is_active)]
        return success_response(data=data, message="Units fetched successfully")

    @staticmethod
    def get_unit(unit_id: UUID, session: Session, current_user: User):
        service = InventoryService(session)
        unit = service.get_unit(unit_id)
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
        return success_response(data=UnitResponse.model_validate(unit), message="Unit fetched successfully")

    @staticmethod
    def update_unit(unit_id: UUID, payload: UnitUpdateRequest, session: Session, current_user: User):
        service = InventoryService(session)
        unit = service.update_unit(unit_id, payload)
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
        return success_response(data=UnitResponse.model_validate(unit), message="Unit updated successfully")

    @staticmethod
    def delete_unit(unit_id: UUID, session: Session, current_user: User):
        service = InventoryService(session)
        if not service.delete_unit(unit_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
        return success_response(message="Unit deleted successfully")

    @staticmethod
    def create_product(payload: ProductCreateRequest, session: Session, current_user: User):
        service = InventoryService(session)
        try:
            product = service.create_product(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        return success_response(data=ProductResponse.model_validate(product), message="Product created successfully")

    @staticmethod
    def list_products(session: Session, current_user: User, is_active: Optional[bool] = None):
        service = InventoryService(session)
        data = [ProductResponse.model_validate(item) for item in service.list_products(is_active=is_active)]
        return success_response(data=data, message="Products fetched successfully")

    @staticmethod
    def get_product(product_id: UUID, session: Session, current_user: User):
        service = InventoryService(session)
        product = service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return success_response(data=ProductResponse.model_validate(product), message="Product fetched successfully")

    @staticmethod
    def update_product(product_id: UUID, payload: ProductUpdateRequest, session: Session, current_user: User):
        service = InventoryService(session)
        try:
            product = service.update_product(product_id, payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return success_response(data=ProductResponse.model_validate(product), message="Product updated successfully")

    @staticmethod
    def delete_product(product_id: UUID, session: Session, current_user: User):
        service = InventoryService(session)
        if not service.delete_product(product_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return success_response(message="Product deleted successfully")

