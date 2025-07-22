from typing import Any

from pydantic import BaseModel


class ThinkResult(BaseModel):
    """Structured output for reasoning tasks"""

    task: str
    reasoning_steps: list[str] = []
    final_conclusion: str | None = None
    visited_urls: list[str] = []
    errors: list[str] | None = None
    execution_successful: bool = False
    metadata: dict[str, Any] = {}
