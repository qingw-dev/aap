import asyncio
import os
import traceback
from pathlib import Path

import filetype
import requests
from aworld.tools import FunctionTools
from datalab_sdk.models import ConversionResult, ConvertOptions, OCROptions
from dotenv import load_dotenv
from pydantic import Field
from pydantic.fields import FieldInfo
from requests.models import Response

from aap.tools.document.views import DocumentEntity, DocumentResult

from .views import DocumentEntity, DocumentResult

DATALAB_URL = "https://www.datalab.to/api/v1"

load_dotenv()
workspace: Path = Path(os.getenv("AWORLD_WORKSPACE", "~/")) / "processed_documents"
workspace.mkdir(parents=True, exist_ok=True)

document_tools: FunctionTools = FunctionTools(
    name="document",
    description="Document processing tools using Datalab SDK",
)


def _prepare_file_entity(file_path: [str | Path]) -> DocumentEntity:
    """
    Prepare a DocumentEntity from the given file path.
    """
    file_path: Path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return DocumentEntity(
        file_name=file_path.resolve().name,
        file_path=file_path.resolve(),
        file_types=filetype.guess(file_path).mime or "application/pdf",
    )


async def _establish_document_session(
    file_entity: DocumentEntity,
    options: [ConvertOptions | OCROptions],
    endpoint: str = "/marker",
) -> dict:
    """
    Establish a session for document processing with Datalab API.
    """
    if not os.getenv("DATALAB_API_KEY"):
        raise ValueError("DATALAB_API_KEY environment variable is not set.")

    try:
        response: Response = requests.post(
            url=DATALAB_URL + endpoint,
            files={
                "file": (
                    file_entity.file_name,
                    open(file_entity.file_path, "rb"),
                    file_entity.file_types,
                ),
                "force_ocr": (None, False),
                "paginate": (
                    None,
                    options.paginate if isinstance(options, ConvertOptions) else False,
                ),
                "output_format": (None, "markdown"),
                "use_llm": (
                    None,
                    options.use_llm if isinstance(options, ConvertOptions) else False,
                ),
                "strip_existing_ocr": (None, False),
                "disable_image_extraction": (None, False),
            },
            headers={"X-Api-Key": os.getenv("DATALAB_API_KEY")},
            timeout=120,
        )
        return response.json()
    except Exception as e:
        raise RuntimeError(
            f"Failed to establish document session: {traceback.format_exc()}"
        ) from e


async def _poll_result(
    check_url: str,
    max_polls: int = 300,
    poll_interval: int = 2,
) -> ConversionResult:
    """
    Poll the Datalab API for the result of the document processing.
    """
    try:
        for _ in range(max_polls):
            await asyncio.sleep(poll_interval)
            response: Response = requests.get(
                check_url,
                headers={"X-Api-Key": os.getenv("DATALAB_API_KEY")},
                timeout=5,
            )
            result_data: dict = response.json()
            if result_data["status"] == "complete":
                return ConversionResult(
                    success=result_data.get("success", False),
                    output_format="markdown",
                    markdown=result_data.get("markdown"),
                    html=result_data.get("html"),
                    json=result_data.get("json"),
                    images=result_data.get("images"),
                    metadata=result_data.get("metadata"),
                    error=result_data.get("error"),
                    page_count=result_data.get("page_count"),
                    status=result_data.get("status", "complete"),
                )
        raise TimeoutError("Document processing timed out.")
    except Exception as e:
        raise RuntimeError(
            f"Failed to poll document result: {traceback.format_exc()}"
        ) from e


@document_tools.tool(
    description=(
        "Convert document to markdown foramt. "
        "Support PDFs, DOCX, XLSX, PPTX, HTML, and images."
    )
)
async def convert_document_to_markdown(
    file_path: str = Field(..., description="Path to the document file"),
    paginate: bool = Field(False, description="Add page delimiters to the output"),
) -> DocumentResult:
    """
    Process document using Datalab SDK with advanced OCR capabilities.

    Convert document to markdown foramt. "
    Support PDFs, DOCX, XLSX, PPTX, HTML, and images.

    Returns DocumentResult with conversion results.
    """
    if isinstance(file_path, FieldInfo):
        file_path: str = file_path.default
    if isinstance(paginate, FieldInfo):
        paginate: bool = paginate.default

    result: DocumentResult = DocumentResult(file_path=file_path)
    try:
        file_entity: DocumentEntity = _prepare_file_entity(file_path)
        session: dict = await _establish_document_session(
            file_entity,
            options=ConvertOptions(
                output_format="markdown",
                paginate=paginate,
                use_llm=True,
                max_pages=None,
            ),
        )
        conversion_result: ConversionResult = await _poll_result(
            session["request_check_url"]
        )
        result.conversion_result = conversion_result
    except Exception as e:
        result.errors = [traceback.format_exc(), str(e)]

    return result


if __name__ == "__main__":

    async def main() -> None:
        result = await convert_document_to_markdown(
            file_path="/Users/arac/Desktop/QW_CV.pdf"
        )
        print(result)

    asyncio.run(main())
