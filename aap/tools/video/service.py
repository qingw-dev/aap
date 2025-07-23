import os
import traceback
from typing import Literal

from dotenv import load_dotenv
from fastmcp.server.server import FastMCP
from google import genai
from google.genai import types
from google.genai.client import Client
from google.genai.types import GenerateContentResponse, Part
from pydantic import Field

from aap.tools.video.views import VideoResult

from .views import VideoResult

load_dotenv(override=True)

mcp = FastMCP("video")


@mcp.tool(
    description=(
        "Summarize a video using Gemini API. "
        "Supports local files (<20MB), YouTube URLs, or uploaded files. "
        "Returns a summary and optionally a quiz with answer key."
    )
)
async def summarize_video(
    video_path: str = Field(
        ..., description="Path to local video file (<20MB) or YouTube URL"
    ),
    summary_type: Literal["summary", "quiz"] = Field(
        "summary",
        description=(
            "Type of summary: 'summary' for plain summary, "
            "'quiz' for summary and quiz with answer key."
        ),
    ),
) -> VideoResult:
    """
    Summarize a video using Gemini API.
    Supports local files (<20MB) or YouTube URLs.
    Returns summary and optionally a quiz with answer key.
    """
    prompt = "Summarize this video."
    if summary_type == "quiz":
        prompt += (
            " Then create a quiz with an answer key "
            "based on the information in this video."
        )

    result: VideoResult = VideoResult(prompt=prompt, video_path=video_path)
    try:
        client: Client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # Handle YouTube URL
        if video_path.startswith("http"):
            file_part: Part = types.Part(
                file_data=types.FileData(file_uri=video_path),
                video_metadata=types.VideoMetadata(fps=2),
            )
            contents: list[Part] = [file_part, types.Part(text=prompt)]
        else:
            # Local file (must be <20MB)
            with open(file=video_path, mode="rb") as f:
                video_bytes: bytes = f.read()
            file_part: Part = types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type="video/mp4"),
                video_metadata=types.VideoMetadata(fps=2),
            )
            contents: list[Part] = [file_part, types.Part(text=prompt)]
        response: GenerateContentResponse = client.models.generate_content(
            model="models/gemini-2.5-flash", contents=types.Content(parts=contents)
        )
        result.answer = response.text
        result.execution_successful = True
    except Exception as e:
        result.errors = [traceback.format_exc(), str(e)]
        result.execution_successful = False
    return result


@mcp.tool(
    description=(
        "Ask a question about a specific timestamp "
        "or segment in a video using Gemini API."
    )
)
async def video_qa(
    video_path: str = Field(
        ..., description="Path to local video file (<20MB) or YouTube URL"
    ),
    question: str = Field(
        ..., description="Question about the video at the given timestamp"
    ),
    timestamp: str = Field(
        None,
        description=(
            "Timestamp in MM:SS format, e.g., '01:15'. "
            "If None, question is about the whole video."
        ),
    ),
) -> VideoResult:
    """
    Ask a question about a specific timestamp or segment in a video using Gemini API.
    """
    prompt: str = f"At {timestamp}, {question}" if timestamp else question
    result: VideoResult = VideoResult(prompt=prompt, video_path=video_path)
    try:
        client: Client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        if video_path.startswith("http"):
            file_part: Part = types.Part(
                file_data=types.FileData(file_uri=video_path),
                video_metadata=types.VideoMetadata(fps=2),
            )
            contents: list[Part] = [file_part, types.Part(text=prompt)]
        else:
            with open(file=video_path, mode="rb") as f:
                video_bytes: bytes = f.read()
            file_part: Part = types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type="video/mp4"),
                video_metadata=types.VideoMetadata(fps=2),
            )
            contents: list[Part] = [file_part, types.Part(text=prompt)]
        response: GenerateContentResponse = client.models.generate_content(
            model="models/gemini-2.5-flash", contents=types.Content(parts=contents)
        )
        result.answer = response.text
        result.execution_successful = True
    except Exception as e:
        result.errors = [traceback.format_exc(), str(e)]
        result.execution_successful = False
    return result


@mcp.tool(
    description=(
        "Transcribe the audio from a video and "
        "provide visual descriptions using Gemini API."
    )
)
async def transcribe_and_describe_video(
    video_path: str = Field(
        ..., description="Path to local video file (<20MB) or YouTube URL"
    ),
) -> VideoResult:
    """
    Transcribe the audio from a video and provide visual descriptions using Gemini API.
    """
    prompt = (
        "Transcribe the audio from this video, "
        "giving timestamps for salient events in the video. "
        "Also provide visual descriptions."
    )
    result: VideoResult = VideoResult(prompt=prompt, video_path=video_path)
    try:
        client: Client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        if video_path.startswith("http"):
            file_part: Part = types.Part(
                file_data=types.FileData(file_uri=video_path),
                video_metadata=types.VideoMetadata(fps=2),
            )
            contents: list[Part] = [file_part, types.Part(text=prompt)]
        else:
            with open(file=video_path, mode="rb") as f:
                video_bytes: bytes = f.read()
            file_part: Part = types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type="video/mp4"),
                video_metadata=types.VideoMetadata(fps=2),
            )
            contents: list[Part] = [file_part, types.Part(text=prompt)]
        response: GenerateContentResponse = client.models.generate_content(
            model="models/gemini-2.5-flash", contents=types.Content(parts=contents)
        )
        result.answer = response.text
        result.execution_successful = True
    except Exception as e:
        result.errors = [traceback.format_exc(), str(e)]
        result.execution_successful = False
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
