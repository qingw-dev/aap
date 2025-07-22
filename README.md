# Objective 
I plan to build a multi-agent project with carefully designed [Context Engineering](https://rlancemartin.github.io/2025/06/23/context_engineering/) and LLM-friendly communication protocols. Given structured inputs and outputs, the project will be able to handle complex multi-agent scenarios. 

Rather than building monolithic agents that try to do everything, build small, focused agents that do one thing well. Each agent will have its own context and its own set of tools.

# Multi-Agent Implementation
Let's construct the following agents.
| Agent    | Core Capability                                                                                        | LLM Model Name                 |
|:---------|:-------------------------------------------------------------------------------------------------------|:-------------------------------|
| Planner  | [SequentialThinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) | google/gemini-2.5-pro          |
| Think    | [DeepSeek-R1](../gaia/services/intelligence/think_collection.py)                                       | deepseek/deepseek-r1-0528:free |
| Search   | [Google Search API](https://developers.google.com/custom-search/v1/overview)                           | google/gemini-2.5-pro          |
| Browser  | [Browser-Use](https://docs.browser-use.com/quickstart)                                                 | google/gemini-2.5-pro          |
| Document | [Marker](https://www.datalab.to/app/pages/documentation)                                               | google/gemini-2.5-pro          |
| Audio    | [Music Analysis](https://glama.ai/mcp/servers/@hugohow/mcp-music-analysis)                             | google/gemini-2.5-pro          |
| Image    | [Gemini Image Understanding](https://ai.google.dev/gemini-api/docs/image-understanding)                | gemini-2.5-pro                 |
| Video    | [Gemini Video Understanding](https://ai.google.dev/gemini-api/docs/video-understanding)                | gemini-2.5-pro                 |
| Coder    | [E2B Code Sandbox](https://e2b.dev/docs/quickstart)                                                    | anthropic/claude-sonnet-4      |

## LLM Settings
We use [OpenRouter](https://openrouter.ai) as provider and [Gemini-2.5-pro](https://openrouter.ai/google/gemini-2.5-pro) as the LLM model. You could reference [Gemini API](https://openrouter.ai/google/gemini-2.5-pro/api) for the standard implementation.

Notice: use native google genai api for image and video agents. [Gemini API quickstart](https://ai.google.dev/gemini-api/docs/quickstart).

# Project Context
This project uses:
- Language/Framework: Python3.13
- Build Tool: uv
- Format: `uv run ruff format .`
- Linting: `uv run ruff check .`
- Testing: `uv run pytest`
- Core packages:
    1. pydantic
    2. [aworld](https://github.com/inclusionAI/AWorld)

## Project Structure
    ./
    ├── prompts
    │   ├── browser.md
    │   ├── other agents' prompts
    ├── models
    │   ├── __init__.py
    │   ├── necessary dataclasses
    ├── agents
    │   ├── __init__.py
    │   ├── base.py (accept natural language input)
    │   ├── browser_agent.py
    │   ├── agents inheriting from base class that utilize tools
    ├── tools
    │   ├── __init__.py
    │   ├── audio
    │   │   ├── views.py # define pydantic models
    │   │   ├── service.py # implement core logic
    │   ├── other tools...
    ├── utils
    │   ├── __init__.py
    │   ├── logging_util.py
    │   ├── necessary utils
    ├── examples
    │   ├── __init__.py
    ├── README.md
    ├── DESIGN.md
    ├── __init__.py
    ├── main.py
    ├── cli.py
    ├── config.py
    ├── exceptions.py