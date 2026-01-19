"""Base repository with generic CRUD operations."""

from typing import Generic, TypeVar
from uuid import UUID


TEntity = TypeVar("TEntity")


class BaseRepository(Generic[TEntity]):
    """Base repository for in-memory storage."""

    def __init__(self) -> None:
        """Initialize repository with empty storage."""
        self._storage: dict[UUID, TEntity] = {}

    async def save(self, entity: TEntity) -> TEntity:
        """Save entity to storage."""
        entity_id = getattr(entity, "id")
        self._storage[entity_id] = entity
        return entity

    async def get_by_id(self, entity_id: UUID) -> TEntity | None:
        """Get entity by ID."""
        return self._storage.get(entity_id)

    async def get_all(self) -> list[TEntity]:
        """Get all entities."""
        return list(self._storage.values())

    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

