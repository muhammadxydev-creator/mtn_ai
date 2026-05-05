"""Project endpoints."""

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from bson import ObjectId

from app.core.database import get_current_project
from app.core.logging import get_logger
from app.core.security import generate_api_key, get_current_active_user
from app.models.project import Project
from app.models.staff import Staff
from app.schemas import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
    ProjectAIConfigUpdate,
    ProjectAIConfigResponse,
)
from app.api.common_responses import LIST_RESPONSES
from app.services.project_ai_config_sync import sync_config_with_retry_and_update

logger = get_logger("endpoints.projects")
router = APIRouter()


@router.get(
    "",
    response_model=ProjectListResponse,
    responses=LIST_RESPONSES
)
async def list_projects(
    current_user: Staff = Depends(get_current_active_user),
) -> ProjectListResponse:
    """
    List projects.

    Retrieve a list of projects. This endpoint is typically used by system administrators
    to manage multiple tenant projects.
    """
    logger.info(f"User {current_user.username} listing projects")

    # Query projects (non-deleted)
    projects = await Project.find(Project.deleted_at == None).to_list()

    project_responses = [ProjectResponse.model_validate(project) for project in projects]

    return ProjectListResponse(data=project_responses)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Staff = Depends(get_current_active_user),
) -> ProjectResponse:
    """
    Create project.

    Create a new project (tenant). This automatically generates an API key for the project
    and publishes a project creation event for AI Service synchronization.
    """
    logger.info(f"User {current_user.username} creating project: {project_data.name}")

    # Generate API key
    api_key = generate_api_key()

    # Create project
    project = Project(
        name=project_data.name,
        api_key=api_key,
    )

    await project.insert()

    logger.info(f"Created project {project.id} with name: {project.name}")

    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Staff = Depends(get_current_active_user),
) -> ProjectResponse:
    """Get project details."""
    logger.info(f"User {current_user.username} getting project: {project_id}")

    try:
        project_id_obj = ObjectId(project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    project = await Project.find_one(Project.id == project_id_obj, Project.deleted_at == None)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: Staff = Depends(get_current_active_user),
) -> ProjectResponse:
    """
    Update project.

    Update project information. This publishes a project update event
    for AI Service synchronization.
    """
    logger.info(f"User {current_user.username} updating project: {project_id}")

    try:
        project_id_obj = ObjectId(project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    project = await Project.find_one(Project.id == project_id_obj, Project.deleted_at == None)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    project.updated_at = datetime.utcnow()

    await project.save()

    logger.info(f"Updated project {project.id}")

    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: Staff = Depends(get_current_active_user),
) -> None:
    """
    Delete project (soft delete).

    Soft delete a project. This publishes a project deletion event
    for AI Service synchronization and cleanup.
    """
    logger.info(f"User {current_user.username} deleting project: {project_id}")

    try:
        project_id_obj = ObjectId(project_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

    project = await Project.find_one(Project.id == project_id_obj, Project.deleted_at == None)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Soft delete
    project.deleted_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()

    await project.save()

    logger.info(f"Deleted project {project.id}")

    return None


@router.get("/{project_id}/ai-config", response_model=ProjectAIConfigResponse)
async def get_project_ai_config(
    project_id: str,
    current_user: Staff = Depends(get_current_active_user),
) -> ProjectAIConfigResponse:
    """Get default AI model configuration for a project.

    If a record does not exist yet, create an empty configuration and return it (HTTP 200).
    Validates that referenced provider IDs exist and are active; if not, returns None for those fields.
    """
    from app.models.project_ai_config import ProjectAIConfig
    from app.models.ai_provider import AIProvider
    
    # Only allow accessing own project's config
    try:
        project_id_obj = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format")
    
    if current_user.project_id != project_id_obj:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    project = await Project.find_one(Project.id == project_id_obj, Project.deleted_at == None)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    cfg = await ProjectAIConfig.find_one(ProjectAIConfig.project_id == project_id_obj, ProjectAIConfig.deleted_at == None)
    if not cfg:
        # Auto-create empty config
        cfg = ProjectAIConfig(project_id=project_id_obj)
        await cfg.insert()

    # Build response from config
    response_data = {
        "id": str(cfg.id),
        "project_id": str(cfg.project_id),
        "default_chat_provider_id": str(cfg.default_chat_provider_id) if cfg.default_chat_provider_id else None,
        "default_chat_model": cfg.default_chat_model,
        "default_embedding_provider_id": str(cfg.default_embedding_provider_id) if cfg.default_embedding_provider_id else None,
        "default_embedding_model": cfg.default_embedding_model,
        "created_at": cfg.created_at,
        "updated_at": cfg.updated_at,
        "deleted_at": cfg.deleted_at,
        "last_synced_at": cfg.last_synced_at,
        "sync_status": cfg.sync_status,
        "sync_error": cfg.sync_error,
    }

    # Collect provider IDs to validate in a single query
    provider_ids_to_check = []
    if cfg.default_chat_provider_id:
        provider_ids_to_check.append(cfg.default_chat_provider_id)
    if cfg.default_embedding_provider_id:
        provider_ids_to_check.append(cfg.default_embedding_provider_id)

    # Query all referenced providers at once (avoid N+1)
    valid_provider_ids = set()
    if provider_ids_to_check:
        valid_providers = await AIProvider.find(
            AIProvider.id.in_(provider_ids_to_check),
            AIProvider.project_id == project_id_obj,
            AIProvider.is_active == True,
            AIProvider.deleted_at == None,
        ).to_list()
        valid_provider_ids = {p.id for p in valid_providers}

    # Validate chat provider
    if cfg.default_chat_provider_id and cfg.default_chat_provider_id not in valid_provider_ids:
        logger.warning(
            "Invalid or inactive default_chat_provider_id detected",
            extra={
                "project_id": str(project_id),
                "default_chat_provider_id": str(cfg.default_chat_provider_id),
            }
        )
        response_data["default_chat_provider_id"] = None
        response_data["default_chat_model"] = None

    # Validate embedding provider
    if cfg.default_embedding_provider_id and cfg.default_embedding_provider_id not in valid_provider_ids:
        logger.warning(
            "Invalid or inactive default_embedding_provider_id detected",
            extra={
                "project_id": str(project_id),
                "default_embedding_provider_id": str(cfg.default_embedding_provider_id),
            }
        )
        response_data["default_embedding_provider_id"] = None
        response_data["default_embedding_model"] = None

    return ProjectAIConfigResponse.model_validate(response_data)


@router.put("/{project_id}/ai-config", response_model=ProjectAIConfigResponse)
async def upsert_project_ai_config(
    project_id: str,
    payload: ProjectAIConfigUpdate,
    current_user: Staff = Depends(get_current_active_user),
) -> ProjectAIConfigResponse:
    """Upsert default AI model configuration for a project.

    - Validates provider IDs belong to the same project
    - Optionally validates model is in provider.available_models when both provided
    """
    from app.models.project_ai_config import ProjectAIConfig
    from app.models.ai_provider import AIProvider
    from app.models.ai_model import AIModel
    
    try:
        project_id_obj = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format")
    
    if current_user.project_id != project_id_obj:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    project = await Project.find_one(Project.id == project_id_obj, Project.deleted_at == None)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    data = payload.model_dump(exclude_unset=True)

    # Validate providers
    chat_pid = data.get("default_chat_provider_id")
    emb_pid = data.get("default_embedding_provider_id")

    async def _validate_provider(provider_id, model_key: str | None) -> None:
        prov = await AIProvider.find_one(
            AIProvider.id == provider_id,
            AIProvider.project_id == project_id_obj,
            AIProvider.deleted_at == None,
        )
        if not prov:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid provider for this project")
        if model_key:
            model_value = data.get(model_key)
            # Fetch available models from relation
            available_models = await AIModel.find(AIModel.provider_id == provider_id, AIModel.deleted_at == None).to_list()
            available_model_ids = [m.model_id for m in available_models]
            if model_value and available_model_ids and model_value not in available_model_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model '{model_value}' not in selected provider's available models",
                )

    if chat_pid:
        await _validate_provider(chat_pid, "default_chat_model")
    if emb_pid:
        await _validate_provider(emb_pid, "default_embedding_model")

    cfg = await ProjectAIConfig.find_one(ProjectAIConfig.project_id == project_id_obj, ProjectAIConfig.deleted_at == None)

    if cfg:
        for k, v in data.items():
            setattr(cfg, k, v)
        cfg.updated_at = datetime.utcnow()
        await cfg.save()
    else:
        cfg = ProjectAIConfig(project_id=project_id_obj, **data)
        await cfg.insert()

    # Attempt to sync to AI service with retry (non-blocking for main flow)
    try:
        await sync_config_with_retry_and_update(cfg)
    except Exception as e:
        logger.warning("ProjectAIConfig sync after upsert failed", extra={"project_id": str(project_id), "error": str(e)})

    return ProjectAIConfigResponse.model_validate(cfg)


@router.post("/{project_id}/ai-config/sync", response_model=ProjectAIConfigResponse)
async def sync_project_ai_config_now(
    project_id: str,
    current_user: Staff = Depends(get_current_active_user),
) -> ProjectAIConfigResponse:
    """Manually trigger sync of a project's AI config to AI service."""
    from app.models.project_ai_config import ProjectAIConfig
    
    try:
        project_id_obj = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format")
    
    if current_user.project_id != project_id_obj:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    cfg = await ProjectAIConfig.find_one(ProjectAIConfig.project_id == project_id_obj, ProjectAIConfig.deleted_at == None)
    if not cfg:
        # Auto-create empty config then sync
        cfg = ProjectAIConfig(project_id=project_id_obj)
        await cfg.insert()

    try:
        await sync_config_with_retry_and_update(cfg)
    except Exception as e:
        logger.warning("ProjectAIConfig manual sync failed", extra={"project_id": str(project_id), "error": str(e)})

    return ProjectAIConfigResponse.model_validate(cfg)
