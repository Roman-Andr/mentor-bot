"""Template management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from jinja2 import BaseLoader, TemplateError
from jinja2.sandbox import SandboxedEnvironment

from notification_service.api.deps import AdminUser, DatabaseSession, HRUser
from notification_service.models import NotificationTemplate
from notification_service.repositories.unit_of_work import SqlAlchemyUnitOfWork
from notification_service.schemas import (
    TemplateCreate,
    TemplateListResponse,
    TemplatePreviewRequest,
    TemplateRenderRequest,
    TemplateRenderResponse,
    TemplateResponse,
    TemplateUpdate,
)
from notification_service.services.template import (
    MissingTemplateVariablesError,
    TemplateNotFoundError,
    TemplateRenderError,
    TemplateService,
)

router = APIRouter()


@router.get("/list")
async def list_templates(
    db: DatabaseSession,
    _current_user: HRUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    name: Annotated[str | None, Query()] = None,
    channel: Annotated[str | None, Query()] = None,
    language: Annotated[str | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
) -> TemplateListResponse:
    """Get paginated list of notification templates with filtering."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        templates, total = await uow.templates.find_templates(
            skip=skip,
            limit=limit,
            name=name,
            channel=channel,
            language=language,
            is_active=is_active,
        )

    pages = (total + limit - 1) // limit if limit > 0 else 0
    return TemplateListResponse(
        total=total,
        templates=[TemplateResponse.model_validate(t) for t in templates],
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=pages,
    )


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: DatabaseSession,
    _current_user: HRUser,
) -> TemplateResponse:
    """Get a specific template by ID."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        template = await uow.templates.get_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found",
            )
        return TemplateResponse.model_validate(template)


@router.get("/by-name/{name}")
async def get_template_by_name(
    name: str,
    db: DatabaseSession,
    _current_user: HRUser,
    channel: Annotated[str, Query()] = "telegram",
    language: Annotated[str, Query()] = "en",
) -> TemplateResponse:
    """Get a template by name, channel, and language."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        template = await uow.templates.get_by_name_channel_language(name, channel, language)

        # If not found in DB, try defaults
        if not template:
            service = TemplateService(uow)
            template = service._get_default_template(name, channel, language)  # noqa: SLF001

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{name}' not found for channel '{channel}' and language '{language}'",
            )
        return TemplateResponse.model_validate(template)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: DatabaseSession,
    current_user: AdminUser,
) -> TemplateResponse:
    """Create a new notification template (admin only)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        # Check if an active template with same name/channel/language exists
        existing = await uow.templates.get_by_name_channel_language(
            template_data.name, template_data.channel, template_data.language
        )

        if existing and not existing.is_default:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Active template already exists for "
                    f"name='{template_data.name}', channel='{template_data.channel}', "
                    f"language='{template_data.language}'. Use update instead."
                ),
            )

        # Create new template
        template = NotificationTemplate(
            name=template_data.name,
            channel=template_data.channel,
            language=template_data.language,
            subject=template_data.subject,
            body_html=template_data.body_html,
            body_text=template_data.body_text,
            variables=template_data.variables,
            version=1,
            is_active=True,
            is_default=False,
            created_by=current_user.id,
        )

        created = await uow.templates.create(template)
        await uow.commit()
        return TemplateResponse.model_validate(created)


@router.put("/{template_id}")
async def update_template(
    template_id: int,
    update_data: TemplateUpdate,
    db: DatabaseSession,
    current_user: AdminUser,
) -> TemplateResponse:
    """Update a template (creates new version, keeps old one inactive)."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        # Get existing template
        existing = await uow.templates.get_by_id(template_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found",
            )

        # Cannot update default templates
        if existing.is_default:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update default templates. Create a new template to override.",
            )

        # Deactivate old version
        existing.is_active = False
        await uow.templates.update(existing)

        # Create new version
        new_template = NotificationTemplate(
            name=existing.name,
            channel=existing.channel,
            language=existing.language,
            subject=update_data.subject if update_data.subject is not None else existing.subject,
            body_html=update_data.body_html if update_data.body_html is not None else existing.body_html,
            body_text=update_data.body_text if update_data.body_text is not None else existing.body_text,
            variables=update_data.variables if update_data.variables is not None else existing.variables,
            version=existing.version + 1,
            is_active=True,
            is_default=False,
            created_by=current_user.id,
        )

        created = await uow.templates.create(new_template)
        await uow.commit()
        return TemplateResponse.model_validate(created)


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: DatabaseSession,
    _current_user: AdminUser,
) -> dict[str, str]:
    """Delete a template (admin only). Cannot delete default templates."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        template = await uow.templates.get_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with ID {template_id} not found",
            )

        if template.is_default:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete default templates",
            )

        await uow.templates.delete(template_id)
        await uow.commit()
        return {"message": f"Template {template_id} deleted successfully"}


@router.post("/render")
async def render_template(
    render_request: TemplateRenderRequest,
    db: DatabaseSession,
    _current_user: HRUser,
) -> TemplateRenderResponse:
    """Render a template with variables for preview."""
    async with SqlAlchemyUnitOfWork(lambda: db) as uow:
        service = TemplateService(uow)

        try:
            rendered = await service.render(
                template_name=render_request.template_name,
                channel=render_request.channel,
                language=render_request.language,
                variables=render_request.variables,
            )
        except TemplateNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from e
        except MissingTemplateVariablesError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e
        except TemplateRenderError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            ) from e

    return TemplateRenderResponse(
        template_name=render_request.template_name,
        channel=render_request.channel,
        language=render_request.language,
        subject=rendered.subject,
        body=rendered.body,
        variables_used=rendered.variables_used,
    )


@router.post("/preview")
async def preview_template(
    preview_request: TemplatePreviewRequest,
    _current_user: HRUser,
) -> TemplateRenderResponse:
    """Preview a template body with variables (no DB lookup)."""
    env = SandboxedEnvironment(loader=BaseLoader(), autoescape=True)

    try:
        # Determine which body to render
        body_template = preview_request.body_text or preview_request.body_html or ""

        # Render subject if provided
        rendered_subject = None
        if preview_request.subject:
            subject_template = env.from_string(preview_request.subject)
            rendered_subject = subject_template.render(**preview_request.variables)

        # Render body
        body_jinja = env.from_string(body_template)
        rendered_body = body_jinja.render(**preview_request.variables)

    except TemplateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template rendering failed: {e!s}",
        ) from e

    return TemplateRenderResponse(
        template_name="preview",
        channel="preview",
        language="en",
        subject=rendered_subject,
        body=rendered_body,
        variables_used=list(preview_request.variables.keys()),
    )
