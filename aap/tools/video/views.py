from typing import Any

from pydantic import BaseModel


class VideoResult(BaseModel):
    """Structured output for video processing tasks"""

    prompt: str
    video_path: str
    answer: str | None = None
    processed_videos: list[str] = []
    errors: list[str] | None = None
    execution_successful: bool = False
    metadata: dict[str, Any] = {}
