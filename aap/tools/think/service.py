import os
import re
import traceback
from typing import Literal

from aworld.config.conf import AgentConfig
from aworld.models.llm import acall_llm_model, get_llm_model
from aworld.models.model_response import ModelResponse
from aworld.tools import FunctionTools
from pydantic import Field

from aap.tools.think.views import ThinkResult

from .views import ThinkResult

# Initialize workspace and tools
workspace = os.getenv("AWORLD_WORKSPACE", "~/think_workspace")
os.makedirs(workspace, exist_ok=True)

# Define the think tools with description
think_tools: FunctionTools = FunctionTools(
    name="think",
    description=(
        "Advanced reasoning capabilities for mathematical, coding, and logical problems"
    ),
)


@think_tools.tool(
    description="""Process complex reasoning tasks with structured output.

    Handles mathematical proofs, programming challenges, and logical problems
    while maintaining processing context and metadata."""
)
async def complex_problem_reasoning(
    question: str = Field(
        description="The input question requiring complex reasoning (math, code, logic)"
    ),
    original_task: str = Field(
        default="", description="Original task context for reference"
    ),
    reasoning_style: Literal["step-by-step", "concise", "detailed"] = Field(
        default="step-by-step",
        description="Reasoinging style: detailed/concise/step-by-step",
    ),
) -> ThinkResult:
    """
    Process complex reasoning tasks with structured output.

    Returns detailed results containing:
    - Processing status
    - Reasoning steps
    - Final solution
    - Error information (if any)
    - Metadata about processing
    """
    result: ThinkResult = ThinkResult(task=question)

    try:
        response: ModelResponse = await acall_llm_model(
            llm_model=get_llm_model(
                AgentConfig(
                    llm_api_key=os.getenv("API_KEY"),
                    llm_base_url=os.getenv("BASE_URL"),
                    llm_model_name="deepseek/deepseek-r1-0528:free",
                    llm_temperature=0.0,
                )
            ),
            messages=_prepare_reasoning_prompt(
                question, original_task, reasoning_style
            ),
        )

        # Extract <think>...</think> and <answer>...</answer> using regex
        match: re.Match = re.search(
            r"<think>(.*?)</think>.*?<answer>(.*?)</answer>",
            response.content,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            think_process: str | None = match.group(1).strip()
            answer: str | None = match.group(2).strip()

            result.final_conclusion = answer
            result.reasoning_steps = think_process.split("\n")

        else:
            result.final_conclusion = response.content

        result.metadata = {
            "model": os.getenv("MODEL_NAME"),
            "response_length": len(result.final_conclusion),
            "style": reasoning_style,
        }
        result.execution_successful = True

    except Exception as e:
        result.errors = [str(e), traceback.format_exc()]
        result.execution_successful = False

    return result


def _prepare_reasoning_prompt(
    question: str,
    original_task: str,
    reasoning_style: Literal["step-by-step", "concise", "detailed"] = "step-by-step",
) -> str:
    """Prepare standardized prompt for reasoning tasks"""
    prompt = (
        f"Question: {question}\n\nContext: {original_task}"
        if original_task
        else question
    )
    style_instructions: dict[str, str] = {
        "step-by-step": "\n\nProvide a clear step-by-step breakdown.",
        "concise": "\n\nProvide a concise but complete solution.",
        "detailed": "\n\nProvide detailed analysis with comprehensive reasoning.",
    }

    return [
        {
            "role": "user",
            "content": prompt + style_instructions.get(reasoning_style, ""),
        }
    ]
