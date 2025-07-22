from typing import Any

from pydantic import BaseModel


class ImageResult(BaseModel):
    """Structured output for image processing tasks"""

    question: str
    answer: str | None = None
    errors: list[str] | None = None
    execution_successful: bool = False
    metadata: dict[str, Any] = {}
