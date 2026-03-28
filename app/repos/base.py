import uuid
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session, selectinload
from app.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class GenericRepository(Generic[T]):

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def create(self, obj_in: Union[Dict[str, Any], T]) -> T:
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        elif isinstance(obj_in, self.model):
            db_obj = obj_in
        else:
            raise TypeError(
                f"create() expects dict or {self.model.__name__}, "
                f"got {type(obj_in)}"
            )

        self.session.add(db_obj)
        self.session.flush()
        self.session.refresh(db_obj)
        return db_obj

    def get_by_id(
        self,
        id: uuid.UUID,
        *,
        include_deleted: bool = False,
        load_relations: Optional[List[str]] = None
    ) -> Optional[T]:
        query = select(self.model).where(self.model.id == id)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        if load_relations:
            for relation in load_relations:
                if hasattr(self.model, relation):
                    query = query.options(
                        selectinload(getattr(self.model, relation))
                    )

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_by_field(
        self,
        field_name: str,
        field_value: Any,
        *,
        include_deleted: bool = False
    ) -> Optional[T]:
        if not hasattr(self.model, field_name):
            raise ValueError(
                f"Model {self.model.__name__} has no field '{field_name}'"
            )

        field = getattr(self.model, field_name)
        query = select(self.model).where(field == field_value)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        search_filters: Optional[Dict[str, Any]] = None,
        load_relations: Optional[List[str]] = None
    ) -> List[T]:
        query = select(self.model)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    query = query.where(
                        getattr(self.model, field_name) == field_value
                    )

        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if order_desc:
                order_field = order_field.desc()
            query = query.order_by(order_field)
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        if load_relations:
            for relation in load_relations:
                if hasattr(self.model, relation):
                    query = query.options(
                        selectinload(getattr(self.model, relation))
                    )

        query = query.offset(skip).limit(limit)
        result = self.session.execute(query)
        return list(result.scalars().all())

    def count(
        self,
        *,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        search_filters: Optional[Dict[str, Any]] = None
    ) -> int:
        query = select(func.count(self.model.id))

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name):
                    query = query.where(
                        getattr(self.model, field_name) == field_value
                    )

        result = self.session.execute(query)
        return result.scalar() or 0

    def update(self, id: uuid.UUID, obj_in: Dict[str, Any]) -> Optional[T]:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None

        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.flush()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: uuid.UUID) -> bool:
        db_obj = self.get_by_id(id, include_deleted=True)
        if not db_obj:
            return False

        self.session.delete(db_obj)
        self.session.commit()
        return True


    def soft_delete(self, id: uuid.UUID) -> Optional[T]:
        if not hasattr(self.model, "deleted_at"):
            raise ValueError(
                f"{self.model.__name__} does not support soft delete"
            )

        db_obj = self.get_by_id(id)
        if not db_obj:
            return None

        db_obj.deleted_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj


    def restore(self, id: uuid.UUID) -> Optional[T]:
        db_obj = self.get_by_id(id, include_deleted=True)
        if not db_obj:
            return None

        db_obj.deleted_at = None
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj


    def exists(self, id: uuid.UUID, *, include_deleted: bool = False) -> bool:
        query = select(func.count(self.model.id)).where(self.model.id == id)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        result = self.session.execute(query)
        return (result.scalar() or 0) > 0

    def bulk_create(
        self, objects: List[Union[Dict[str, Any], T]]
    ) -> List[T]:
        db_objects: List[T] = []

        for obj in objects:
            if isinstance(obj, dict):
                db_objects.append(self.model(**obj))
            elif isinstance(obj, self.model):
                db_objects.append(obj)
            else:
                raise TypeError(
                    f"bulk_create expects dict or {self.model.__name__}"
                )

        self.session.add_all(db_objects)
        self.session.flush()

        for obj in db_objects:
            self.session.refresh(obj)

        return db_objects

    def bulk_update(self, filters: Dict[str, Any], values: Dict[str, Any]) -> int:
        query = update(self.model)

        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name):
                query = query.where(
                    getattr(self.model, field_name) == field_value
                )

        result = self.session.execute(query.values(**values))
        return result.rowcount

    def bulk_delete(self, ids: List[uuid.UUID]) -> int:
        result = self.session.execute(
            delete(self.model).where(self.model.id.in_(ids))
        )
        return result.rowcount
