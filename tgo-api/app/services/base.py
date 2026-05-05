"""Base service class for business logic with MongoDB/Beanie support."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from beanie import Document
from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

ModelType = TypeVar("ModelType", bound=Document)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

logger = get_logger("services.base")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with common CRUD operations for MongoDB."""
    
    def __init__(self, model: Type[ModelType]):
        """Initialize service with model class."""
        self.model = model
        self.model_name = model.__name__
    
    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        return await self.model.get(id)
    
    async def get_or_404(self, id: Any) -> ModelType:
        """Get a single record by ID or raise 404."""
        obj = await self.get(id)
        if not obj:
            raise NotFoundError(self.model_name, str(id))
        return obj
    
    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        project_id: Optional[UUID] = None,
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering."""
        # Build query
        query = {}
        
        # Add project filter if model has project_id
        if project_id is not None:
            query["project_id"] = project_id
        
        # Add soft delete filter if model supports it
        if hasattr(self.model, "deleted_at"):
            query["deleted_at"] = None
        
        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query[key] = value
        
        # Execute query with pagination
        results = await self.model.find_many(query).skip(skip).limit(limit).to_list()
        return results
    
    async def count(
        self,
        filters: Optional[Dict[str, Any]] = None,
        project_id: Optional[UUID] = None,
    ) -> int:
        """Count records with optional filtering."""
        # Build query
        query = {}
        
        # Add project filter if model has project_id
        if project_id is not None:
            query["project_id"] = project_id
        
        # Add soft delete filter if model supports it
        if hasattr(self.model, "deleted_at"):
            query["deleted_at"] = None
        
        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query[key] = value
        
        return await self.model.find_many(query).count()
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_in_data)
        await db_obj.insert()
        logger.info(f"Created {self.model_name} with ID: {db_obj.id}")
        return db_obj
    
    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Update an existing record."""
        obj_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Update timestamp if available
        if hasattr(db_obj, 'updated_at'):
            from datetime import datetime
            db_obj.updated_at = datetime.utcnow()
        
        await db_obj.save()
        logger.info(f"Updated {self.model_name} with ID: {db_obj.id}")
        return db_obj
    
    async def remove(self, id: Any) -> ModelType:
        """Remove a record (hard delete)."""
        obj = await self.get(id)
        if not obj:
            raise NotFoundError(self.model_name, str(id))
        
        await obj.delete()
        logger.info(f"Deleted {self.model_name} with ID: {id}")
        return obj
    
    async def soft_delete(self, id: Any) -> ModelType:
        """Soft delete a record (if model supports it)."""
        obj = await self.get(id)
        if not obj:
            raise NotFoundError(self.model_name, str(id))
        
        if hasattr(obj, 'deleted_at'):
            from datetime import datetime
            obj.deleted_at = datetime.utcnow()
            if hasattr(obj, 'updated_at'):
                obj.updated_at = datetime.utcnow()
            
            await obj.save()
            logger.info(f"Soft deleted {self.model_name} with ID: {id}")
            return obj
        else:
            # Fall back to hard delete if soft delete not supported
            return await self.remove(id=id)
    
    async def get_by_project(
        self,
        *,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """Get records filtered by project ID (for multi-tenant models)."""
        return await self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            project_id=project_id,
        )
    
    async def count_by_project(
        self,
        *,
        project_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count records filtered by project ID."""
        return await self.count(
            filters=filters,
            project_id=project_id,
        )
