import typing

from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.middleware.pagination import request_object

M = typing.TypeVar("M", bound=BaseModel)


class BasePaginator:
    def __init__(
        self,
        page: int,
        per_page: int,
    ):
        self.page = page
        self.per_page = per_page
        self.limit = per_page * page
        self.offset = (page - 1) * per_page
        self.request = request_object.get()
        # computed later
        self.number_of_pages = 0
        self.next_page = ""
        self.previous_page = ""

    def _get_next_page(self) -> typing.Optional[str]:
        if self.page >= self.number_of_pages:
            return
        url = self.request.url.include_query_params(page=self.page + 1)
        return str(url)

    def _get_previous_page(self) -> typing.Optional[str]:
        if self.page == 1 or self.page > self.number_of_pages + 1:
            return
        url = self.request.url.include_query_params(page=self.page - 1)
        return str(url)

    def _get_number_of_pages(self, count: int) -> int:
        rest = count % self.per_page
        quotient = count // self.per_page
        return quotient if not rest else quotient + 1


class Paginator(BasePaginator):
    """
    Paginator class designed for usage with pydantic models and orm queries
    """

    def __init__(
        self,
        session: AsyncSession,
        query: Select,
        page: int,
        per_page: int,
    ):
        super().__init__(page=page, per_page=per_page)
        self.session = session
        self.query = query

    async def get_response(
        self, cast_to: typing.Optional[typing.Type[M]] = None
    ) -> dict:
        q = await self.session.scalars(self.query.limit(self.limit).offset(self.offset))
        if cast_to:
            items = [cast_to(**item.__dict__) for item in q]
        else:
            items = [{**item.__dict__} for item in q]
        return {
            "total_count": await self._get_total_count(),
            "next_page": self._get_next_page(),
            "previous_page": self._get_previous_page(),
            "items": items,
        }

    async def _get_total_count(self) -> int:
        count = await self.session.scalar(
            select(func.count()).select_from(self.query.subquery())
        )
        self.number_of_pages = self._get_number_of_pages(count)
        return count


class RawPaginator(BasePaginator):
    """
    Paginator class designed to be used with raw text sql queries with dict outputs
    """

    def __init__(self, page: int, per_page: int):
        super().__init__(page, per_page)

    def paginate_raw_sql_query(
        self, total_count: int, items: list | dict
    ) -> dict[
        typing.Literal["total_count"]
        | typing.Literal["next_page"]
        | typing.Literal["previous_page"]
        | typing.Literal["items"],
        typing.Any,
    ]:
        self.number_of_pages = self._get_number_of_pages(total_count)
        return {
            "total_count": total_count,
            "next_page": self._get_next_page(),
            "previous_page": self._get_previous_page(),
            "items": items,
        }


async def paginate(
    db: AsyncSession,
    query: Select,
    cast_to: typing.Optional[typing.Type[M]],
    page: int,
    per_page: int,
) -> dict:
    paginator = Paginator(db, query, page, per_page)
    return await paginator.get_response(cast_to=cast_to)


def paginate_raw(
    page: int,
    per_page: int,
    total_count: int,
    items: list[typing.Optional[dict]] | dict,
):
    paginator = RawPaginator(page=page, per_page=per_page)
    return paginator.paginate_raw_sql_query(total_count=total_count, items=items)
