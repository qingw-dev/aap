from pathlib import Path
from typing import Literal

from datalab_sdk.models import ConversionResult
from pydantic import BaseModel, Field

# pylint: disable=line-too-long


class DocumentResult(BaseModel):
    file_path: str = Field(..., description="Path to the processed document")
    conversion_result: ConversionResult | None = (
        Field(None, description="Conversion result"),
    )
    errors: list[str] | None = Field(
        None, description="Error messages if processing failed"
    )


class DocumentEntity(BaseModel):
    """Represents a document entity with its metadata and content."""

    file_name: str = Field(..., description="Name of the document file")
    file_path: str | Path = Field(..., description="Absolute path to the document file")
    file_types: Literal[
        # pdf
        "application/pdf",
        # spreadsheet
        "application/vnd.ms-excel",  # xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
        "application/vnd.oasis.opendocument.spreadsheet",  # ods
        # word
        "application/msword",  # doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
        "application/vnd.oasis.opendocument.text",  # odt
        # presentation
        "application/vnd.ms-powerpoint",  # ppt
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
        "application/vnd.oasis.opendocument.presentation",  # odp
        # html
        "text/html",
        # image
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/tiff",
        "image/webp",
        # epub
        "application/epub+zip",
    ] = Field(..., description="MIME type of the document file")
