from logging import getLogger
from typing import Any, Generic, Iterable, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("M", bound=BaseModel)
logger = getLogger(__name__)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        return await db.get(self.model, id)

    async def get_multi(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).offset(offset).limit(limit)
        result = await db.scalars(statement)
        return result.all()

    async def create(
        self, db: AsyncSession, *, obj_in: Union[dict[str, Any], SchemaType]
    ) -> ModelType:
        if isinstance(obj_in, BaseModel):
            obj_in = obj_in.model_dump(mode="json")

        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[dict[str, Any], SchemaType],
    ) -> ModelType:
        if isinstance(obj_in, BaseModel):
            obj_in = obj_in.model_dump(mode="json")

        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        obj = await db.get(self.model, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def get_by_filters(
        self, db: AsyncSession, **filters: Any
    ) -> Optional[ModelType]:
        """
        :param filters - kwarg key is column name, kwarg value is filter value
        """
        statement = select(self.model).filter_by(**filters)
        return await db.scalar(statement)

    async def get_multi_by_filters(
        self, db: AsyncSession, offset: int = 0, limit: int = 100, **filters: Any
    ) -> List[ModelType]:
        """
        :param filters - kwarg key is column name, kwarg value is filter value
        """
        statement = select(self.model).filter_by(**filters).offset(offset).limit(limit)
        result = await db.scalars(statement)
        return result.all()

    async def get_multi_by_ids(
        self,
        db: AsyncSession,
        ids: list[UUID | str],
        offset: int = 0,
        limit: int = 100,
    ):
        statement = (
            select(self.model).where(self.model.id.in_(ids)).offset(offset).limit(limit)
        )
        result = await db.scalars(statement)
        return result.all()

    @staticmethod
    def _apply_filters(model, filters: dict):
        return [getattr(model, k) == v for k, v in filters.items()]

    async def get_by_filters_with_options(
        self, db: AsyncSession, *options: Iterable[Any], **filters: Any
    ):
        """
        :param filters - kwarg key is column name, kwarg value is filter value
        :param options - args with sqlalchemy compatible `.options()` values, such as
        ```
        [
            selectinload(ModelType.m2m_field),
            ...
        ]
        ```
        """
        statement = select(self.model).where(*self._apply_filters(self.model, filters))
        if options:
            statement = statement.options(*options)
        return await db.scalar(statement)

    async def get_multi_by_filters_with_options(
        self,
        db: AsyncSession,
        offset: int = 0,
        limit: int = 100,
        *options: Iterable[Any],
        **filters: Any,
    ) -> List[ModelType]:
        """
        :param filters - kwarg key is column name, kwarg value is filter value
        :param options - args with sqlalchemy compatible `.options()` values, such as
        ```
        [
            selectinload(ModelType.m2m_field),
            ...
        ]
        ```
        """
        statement = (
            select(self.model)
            .where(*self._apply_filters(self.model, filters))
            .offset(offset)
            .limit(limit)
        )
        if options:
            statement = statement.options(*options)

        result = await db.scalars(statement)
        return result.all()

    async def update_by_filters(
        self, db: AsyncSession, values: dict[str, Any], **filters: Any
    ) -> None:
        """
        :param filters - kwarg key is column name, kwarg value is filter value
        """
        statement = (
            update(self.model)
            .where(*(getattr(self.model, k) == v for k, v in filters.items()))
            .values(**values)
        )
        await db.execute(statement)
        await db.commit()
        return

    async def count_with_filters(self, db: AsyncSession, **filters: Any) -> int:
        statement = select(func.count()).select_from(self.model).filter_by(**filters)
        return await db.scalar(statement)

    async def delete_multiple(self, db: AsyncSession, ids: list[str]):
        result = await db.execute(delete(self.model).where(self.model.id.in_(ids)))
        await db.commit()
        await db.flush()
        return result

    async def delete_all_from_table(self, db: AsyncSession):
        result = await db.execute(delete(self.model))
        await db.commit()
        return result
