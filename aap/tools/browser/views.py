from pydantic import BaseModel, Field


class BrowserResult(BaseModel):
    """Metadata for browser automation results."""

    task: str
    execution_successful: bool = False
    task_completion: str | None = None
    extracted_content: str | None = None
    visited_urls: list[str] = Field(default_factory=list)
    screenshots: list[str] = Field(default_factory=list)
    errors: list[str] | None = None
