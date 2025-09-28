from tortoise import Model
from tortoise.queryset import QuerySet
from typing import Type, Callable, Optional, List
from src.error.base import ErrorHandler


class BaseModelService:
    def __init__(self, model: Type[Model], methods: Optional[List[Callable]] = None):
        self.model = model
        self.error = ErrorHandler(model)
        self.methods = methods or []  # list of query modifiers

    def _apply_methods(self, query: QuerySet):
        """Apply all query modification methods before execution."""
        for method in self.methods:
            query = method(query)
        return query

    async def get_list_or_404(self, **kwargs) -> List[Model]:
        query = self.model.filter(**kwargs).order_by("created_at")
        query = self._apply_methods(query)
        objs = await query.all()
        if not objs:
            raise self.error.get(404)
        return objs

    async def get_object_or_404(self, **kwargs) -> Model:
        query = self.model.filter(**kwargs)
        query = self._apply_methods(query)
        obj = await query.first()
        if not obj:
            raise self.error.get(404)
        return obj

    async def list_active(self) -> List[Model]:
        query = self.model.filter(is_deleted=False).order_by("created_at")
        query = self._apply_methods(query)
        return await query.all()

    async def all(self) -> List[Model]:
        query = self.model.all().order_by("created_at")
        query = self._apply_methods(query)
        return await query

    async def delete(self, id: str) -> Model:
        obj = await self.get_object_or_404(id=id)
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
            await obj.save()
        else:
            await obj.delete()
        return obj

    async def all_with_related(self, related: List[str]) -> List[Model]:
        """Return all with related/prefetched relations"""
        query = self.model.all().order_by("created_at").prefetch_related(*related)
        query = self._apply_methods(query)
        return await query
