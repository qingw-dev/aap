import mimetypes
import os
import traceback
from typing import Any

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from google import genai
from google.genai import types
from pydantic import Field

from aap.tools.image.views import ImageResult

from .views import ImageResult

load_dotenv(override=True)

mcp = FastMCP("search")


@mcp.tool(
    description="""Process images with multi-modal reasoning capabilities.

    Supports image captioning, classification, and visual question answering
    through Gemini's multi-modal architecture."""
)
async def process_image(
    question: str = Field(
        ..., description="User's question or prompt for image processing"
    ),
    image_paths: list[str] = Field(
        default_factory=list, description="Local paths to images"
    ),
    image_urls: list[str] = Field(
        default_factory=list, description="URLs of images to process"
    ),
) -> ImageResult:
    """
    Process images with Gemini's multi-modal capabilities.

    Returns structured results containing:
    - Generated analysis/caption
    - Processing metadata
    - Error information (if any)
    - Image references
    """
    result: ImageResult = ImageResult(question=question)

    image_parts: list = []
    try:
        for image_path in image_paths:
            with open(file=image_path, mode="rb") as f:
                image_parts.append(
                    types.Part.from_bytes(
                        data=f.read(),
                        mime_type=mimetypes.guess_type(url=image_path)[0]
                        or "image/jpeg",
                    )
                )
        for image_url in image_urls:
            image_bytes: bytes | Any = requests.get(image_url, timeout=30).content
            image_parts.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mimetypes.guess_type(url=image_url)[0] or "image/jpeg",
                )
            )
    except Exception as e:
        result.errors = [str(e), traceback.format_exc()]
        return result

    try:
        client: genai.Client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response: types.GenerateContentResponse = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                question,
                *image_parts,  # Include all image parts
            ],
        )
        result.answer = response.text

        result.metadata = {
            "model": "google/gemini-2.5-pro",
            "total_images": len(image_parts),
            "image_uris": image_paths + image_urls,
        }
        result.execution_successful = True
    except Exception as e:
        result.execution_successful = False
        result.errors = [str(e), traceback.format_exc()]
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
