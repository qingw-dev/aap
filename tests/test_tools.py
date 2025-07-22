import asyncio

from aap.tools import (
    complete_browser_task,
    complex_problem_reasoning,
    convert_document_to_markdown,
    google_search,
    process_image,
    summarize_video,
    transcribe_and_describe_video,
    video_qa,
)
from aap.tools.image.views import ImageResult
from aap.tools.video.views import VideoResult


def test_all() -> None:
    methods = (
        summarize_video,
        transcribe_and_describe_video,
        video_qa,
        complex_problem_reasoning,
        google_search,
        process_image,
        convert_document_to_markdown,
        complete_browser_task,
    )
    print(methods)


async def test_video_qa_youtube() -> None:
    result: VideoResult = await video_qa(
        "https://www.youtube.com/watch?v=tm09cMTBTSU",
        "What is the main topic of the video?",
    )
    assert result is not None
    print(result)


async def test_video_qa_local() -> None:
    result: VideoResult = await video_qa(
        "/Users/arac/Desktop/test_video.mp4",
        "What is the main topic of the video?",
    )
    assert result is not None
    print(result)


async def test_image_qa() -> None:
    result: ImageResult = await process_image(
        "Describe the two images.",
        image_paths=[
            "/Users/arac/Desktop/qw.jpg",
        ],
        image_urls=[
            "https://gw.alipayobjects.com/zos/bmw-prod/f99a542e-cf8d-45d3-bdb7-a0baa5f229a2/lrpqgxdr_w720_h404.png",  # pylint: disable=line-too-long
        ],
    )
    assert result is not None
    print(result)


async def test_reasoning() -> None:
    result = await complex_problem_reasoning(
        # 'In Unlambda, what exact charcter or text needs to be added to correct the following code to output "For penguins"? If what is needed is a character, answer with the name of the character. If there are different names for the character, use the shortest. The text location is not needed. Code:\n\n`r```````````.F.o.r. .p.e.n.g.u.i.n.si',  # pylint: disable=line-too-long
        "How many r is in strawberry",
        None,
        "step-by-step",
    )
    assert result is not None
    print(result)


async def test_google_search() -> None:
    result = await google_search(
        query="What is the capital of France?",
    )
    assert result is not None
    print(result)


async def test_convert_pdf_to_markdown() -> None:
    result = await convert_document_to_markdown(
        file_path="/Users/arac/Desktop/QW_CV.pdf"
    )
    assert result is not None
    print(result)


async def test_convert_xlsx_to_markdown() -> None:
    result = await convert_document_to_markdown(
        file_path="/Users/arac/Desktop/outing.xlsx"
    )
    assert result is not None
    print(result)


async def test_convert_docx_to_markdown() -> None:
    result = await convert_document_to_markdown(
        file_path="/Users/arac/Desktop/test_docx.docx"
    )
    assert result is not None
    print(result)


async def test_convert_pptx_to_markdown() -> None:
    result = await convert_document_to_markdown(
        file_path="/Users/arac/Desktop/test_pptx.pptx"
    )
    assert result is not None
    print(result)


async def test_browser_use() -> None:
    result = await complete_browser_task(
        task="Open taobao then report the first product"
    )
    assert result is not None
    # print(result)
    with open("browser_result.txt", "w", encoding="utf-8") as f:
        f.write(result.model_dump_json())


if __name__ == "__main__":
    # asyncio.run(test_video_qa_youtube())
    # asyncio.run(test_video_qa_local())
    # asyncio.run(test_image_qa())
    # asyncio.run(test_reasoning())
    # asyncio.run(test_google_search())
    # asyncio.run(test_convert_pdf_to_markdown())
    asyncio.run(test_convert_xlsx_to_markdown())
    asyncio.run(test_convert_docx_to_markdown())
    asyncio.run(test_convert_pptx_to_markdown())
    # asyncio.run(test_browser_use())
