"""Pydantic schemas for notification template request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TemplateBase(BaseModel):
    """Base template schema."""

    name: str = Field(..., min_length=1, max_length=100, description="Template identifier name")
    channel: str = Field(..., min_length=1, max_length=20, description="Channel: email, telegram, sms")
    language: str = Field(default="en", min_length=2, max_length=10, description="Language code (e.g., 'en', 'ru')")
    subject: str | None = Field(None, max_length=500, description="Email subject line")
    body_html: str | None = Field(None, description="HTML body for email")
    body_text: str | None = Field(None, description="Plain text body (fallback for email, required for telegram)")
    variables: list[str] = Field(default_factory=list, description="List of required template variables")

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        """Validate channel is one of the allowed values."""
        allowed = {"email", "telegram", "sms"}
        if v.lower() not in allowed:
            msg = f"Channel must be one of: {allowed}"
            raise ValueError(msg)
        return v.lower()

    @model_validator(mode="after")
    def validate_body_content(self) -> "TemplateBase":
        """Validate that at least one body format is provided."""
        if self.body_text is None and self.body_html is None:
            msg = "At least one of body_text or body_html must be provided"
            raise ValueError(msg)
        return self


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template (creates new version)."""

    subject: str | None = Field(None, max_length=500)
    body_html: str | None = Field(None)
    body_text: str | None = Field(None)
    variables: list[str] | None = Field(None)
    is_active: bool | None = Field(None)


class TemplateResponse(TemplateBase):
    """Template response schema."""

    id: int
    version: int
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime
    created_by: int | None

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Paginated list of templates response schema."""

    total: int
    templates: list[TemplateResponse]
    page: int
    size: int
    pages: int


class TemplateRenderRequest(BaseModel):
    """Request to render a template for preview."""

    template_name: str = Field(..., min_length=1, max_length=100)
    channel: str = Field(..., min_length=1, max_length=20)
    language: str = Field(default="en", min_length=2, max_length=10)
    variables: dict[str, str] = Field(default_factory=dict, description="Variables to substitute in template")


class TemplateRenderResponse(BaseModel):
    """Response with rendered template content."""

    template_name: str
    channel: str
    language: str
    subject: str | None
    body: str
    variables_used: list[str]


class TemplatePreviewRequest(BaseModel):
    """Request to preview a template with sample variables."""

    body_text: str | None = Field(None)
    body_html: str | None = Field(None)
    subject: str | None = Field(None)
    variables: dict[str, str] = Field(default_factory=dict)
