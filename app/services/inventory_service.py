import re
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.schemas.inventory_schema import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    ProductCreateRequest,
    ProductUpdateRequest,
    UnitCreateRequest,
    UnitUpdateRequest,
)
from app.models.inventory import (
    Category,
    Product,
    Unit,
)
from app.repos.inventory_repository import (
    CategoryRepository,
    ProductRepository,
    UnitRepository,
)


def _slugify(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "-", value)


class InventoryService:
    def __init__(self, session: Session):
        self.session = session
        self.category_repo = CategoryRepository(session)
        self.unit_repo = UnitRepository(session)
        self.product_repo = ProductRepository(session)

    def _unique_slug(self, model, name: str, slug: Optional[str] = None, excluded_id: Optional[UUID] = None) -> str:
        base = _slugify(slug or name)
        candidate = base
        counter = 1
        while True:
            query = select(model).where(model.slug == candidate, model.deleted_at.is_(None))
            if excluded_id:
                query = query.where(model.id != excluded_id)
            existing = self.session.execute(query).scalar_one_or_none()
            if not existing:
                return candidate
            counter += 1
            candidate = f"{base}-{counter}"

    def _assert_category_exists(self, category_id: UUID) -> None:
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")

    def _assert_unit_exists(self, unit_id: UUID) -> None:
        unit = self.unit_repo.get_by_id(unit_id)
        if not unit:
            raise ValueError("Unit not found")

    def create_category(self, payload: CategoryCreateRequest) -> Category:
        slug = self._unique_slug(Category, payload.name, payload.slug)
        if payload.parent_id:
            self._assert_category_exists(payload.parent_id)
        return self.category_repo.create(
            {
                "name_en": payload.name.strip(),
                "name_ar": payload.name.strip(),
                "name_fr": payload.name.strip(),
                "name": payload.name.strip(),
                "slug": slug,
                "description": payload.description,
                "parent_id": payload.parent_id,
                "is_active": payload.is_active,
            }
        )

    def list_categories(self, is_active: Optional[bool] = None) -> List[Category]:
        filters = {} if is_active is None else {"is_active": is_active}
        return self.category_repo.get_all(filters=filters, order_by="name")

    def get_category(self, category_id: UUID) -> Optional[Category]:
        return self.category_repo.get_by_id(category_id)

    def update_category(self, category_id: UUID, payload: CategoryUpdateRequest) -> Optional[Category]:
        category = self.category_repo.get_by_id(category_id)
        if not category:
            return None

        data = payload.model_dump(exclude_unset=True)
        if "name" in data and "slug" not in data:
            data["slug"] = self._unique_slug(Category, data["name"], excluded_id=category_id)
            data["name_en"] = data["name"]
            data["name_ar"] = data["name"]
            data["name_fr"] = data["name"]
        elif "slug" in data and data["slug"]:
            data["slug"] = self._unique_slug(Category, category.name, data["slug"], excluded_id=category_id)

        if "parent_id" in data and data["parent_id"]:
            self._assert_category_exists(data["parent_id"])

        return self.category_repo.update(category_id, data)

    def delete_category(self, category_id: UUID) -> bool:
        category = self.category_repo.get_by_id(category_id)
        if not category:
            return False
        self.category_repo.soft_delete(category_id)
        return True

    def create_unit(self, payload: UnitCreateRequest) -> Unit:
        return self.unit_repo.create(payload.model_dump())

    def list_units(self, is_active: Optional[bool] = None) -> List[Unit]:
        filters = {} if is_active is None else {"is_active": is_active}
        return self.unit_repo.get_all(filters=filters, order_by="name")

    def get_unit(self, unit_id: UUID) -> Optional[Unit]:
        return self.unit_repo.get_by_id(unit_id)

    def update_unit(self, unit_id: UUID, payload: UnitUpdateRequest) -> Optional[Unit]:
        return self.unit_repo.update(unit_id, payload.model_dump(exclude_unset=True))

    def delete_unit(self, unit_id: UUID) -> bool:
        unit = self.unit_repo.get_by_id(unit_id)
        if not unit:
            return False
        self.unit_repo.soft_delete(unit_id)
        return True

    def create_product(self, payload: ProductCreateRequest) -> Product:
        self._assert_category_exists(payload.category_id)
        self._assert_unit_exists(payload.unit_id)
        if payload.purchase_unit_id:
            self._assert_unit_exists(payload.purchase_unit_id)
        if payload.sales_unit_id:
            self._assert_unit_exists(payload.sales_unit_id)

        slug = self._unique_slug(Product, payload.name, payload.slug)
        return self.product_repo.create(
            {
                **payload.model_dump(exclude={"slug"}),
                "slug": slug,
            }
        )

    def list_products(self, is_active: Optional[bool] = None) -> List[Product]:
        filters = {} if is_active is None else {"is_active": is_active}
        return self.product_repo.get_all(filters=filters, order_by="name")

    def get_product(self, product_id: UUID) -> Optional[Product]:
        return self.product_repo.get_by_id(product_id)

    def update_product(self, product_id: UUID, payload: ProductUpdateRequest) -> Optional[Product]:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return None

        data = payload.model_dump(exclude_unset=True)
        if "category_id" in data and data["category_id"]:
            self._assert_category_exists(data["category_id"])
        if "unit_id" in data and data["unit_id"]:
            self._assert_unit_exists(data["unit_id"])
        if "purchase_unit_id" in data and data["purchase_unit_id"]:
            self._assert_unit_exists(data["purchase_unit_id"])
        if "sales_unit_id" in data and data["sales_unit_id"]:
            self._assert_unit_exists(data["sales_unit_id"])

        if "name" in data and "slug" not in data:
            data["slug"] = self._unique_slug(Product, data["name"], excluded_id=product_id)
        elif "slug" in data and data["slug"]:
            data["slug"] = self._unique_slug(Product, product.name, data["slug"], excluded_id=product_id)

        return self.product_repo.update(product_id, data)

    def delete_product(self, product_id: UUID) -> bool:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False
        self.product_repo.soft_delete(product_id)
        return True
