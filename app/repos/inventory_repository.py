from sqlalchemy.orm import Session

from app.models.inventory import Category, Product, Unit
from app.repos.base import GenericRepository


class CategoryRepository(GenericRepository[Category]):
    def __init__(self, session: Session):
        super().__init__(Category, session)


class UnitRepository(GenericRepository[Unit]):
    def __init__(self, session: Session):
        super().__init__(Unit, session)


class ProductRepository(GenericRepository[Product]):
    def __init__(self, session: Session):
        super().__init__(Product, session)
