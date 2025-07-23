import base64
import os
import traceback
from pathlib import Path

from browser_use import Agent, BrowserSession
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.profile import BrowserProfile
from browser_use.llm import ChatOpenAI
from dotenv import load_dotenv
from fastmcp.server.server import FastMCP
from pydantic import Field
from pydantic.fields import FieldInfo

from .prompts import extended_browser_system_prompt
from .views import BrowserResult

load_dotenv(override=True)

mcp = FastMCP("browser")


@mcp.tool(
    description="""Use browser to visit a web page, extract content,
    and optionally download files/images, ...

    Returns a dict with execution trace, answer (extracted content),
    and downloaded file/image paths."""
)
async def complete_browser_task(
    task: str = Field(
        ...,
        description=(
            "Detailed task description e.g., 'Extract the main content from the page'"
        ),
    ),
    message_context=Field(
        ...,
        description="Additional information about the task",
    ),
) -> BrowserResult:
    """
    Use browser-use to visit a web page, extract content,
    and optionally download files/images.

    Returns a dict with execution trace, answer (extracted content),
    and downloaded file/image paths.
    """
    workspace: Path = Path(os.getenv("AWORLD_WORKSPACE", "~/")).expanduser()
    workspace.mkdir(parents=True, exist_ok=True)
    screenshots_dir = workspace / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    task: str = task.default if isinstance(task, FieldInfo) else task

    browser_profile: BrowserProfile = BrowserProfile(
        stealth=True,
        viewport={"width": 1280, "height": 1024},
        # All elements from the entire page will be included,
        # regardless of visibility
        # (highest token usage but most complete).
        viewport_expansion=-1,
        # playwright options
        headless=False,
        user_data_dir=Path(
            "~/.config/browseruse/profiles/default-google-chrome"
        ).expanduser(),
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/85.0.4183.102 Safari/537.36"
        ),
        highlight_elements=True,
    )
    browser_session: BrowserSession = BrowserSession(browser_profile=browser_profile)
    agent = Agent(
        task=task,
        message_context=message_context.default
        if isinstance(message_context, FieldInfo)
        else None,
        llm=ChatOpenAI(
            model=os.getenv("MODEL_NAME"),
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "1.0")),
        ),
        extend_system_message=extended_browser_system_prompt,
        use_vision=True,
        browser_session=browser_session,
        save_conversation_path=workspace / "logs/conversation",
    )

    result: BrowserResult = BrowserResult(task=task)
    try:
        history: AgentHistoryList = await agent.run()
        # status
        is_done: bool = history.is_done()
        has_errors: bool = history.has_errors()
        # answer
        task_completion: str | None = history.final_result()
        # assets
        extracted_content: list[str] = history.extracted_content()
        visited_urls: list[str | None] = history.urls()
        saved_screenshot_paths: list[str] = []
        for idx, screenshot in enumerate(history.screenshots()):
            if screenshot is None:
                continue
            # Use task slug and index for filename
            task_slug = "".join(
                c if c.isalnum() or c in "-_" else "_"
                for c in task.lower().replace(" ", "_")
            )[:40]
            filename = f"{task_slug}_{idx + 1}.png"
            dest_path = screenshots_dir / filename
            # Screenshot is always bytes, so write it directly
            with open(dest_path, "wb") as f:
                f.write(base64.b64decode(screenshot))
            saved_screenshot_paths.append(str(dest_path))

        result.execution_successful = is_done and not has_errors
        result.task_completion = task_completion
        result.extracted_content = extracted_content[0] if extracted_content else None
        result.visited_urls = [url for url in visited_urls if url is not None]
        result.screenshots = saved_screenshot_paths
        result.errors = (
            [error for error in history.errors() if error is not None]
            if has_errors
            else None
        )
    except Exception:
        result.errors = history.errors() + [traceback.format_exc()]
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
