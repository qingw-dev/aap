# Objective 
I plan to build a multi-agent project with carefully designed [Context Engineering](https://rlancemartin.github.io/2025/06/23/context_engineering/) and LLM-friendly communication protocols. Given structured inputs and outputs, the project will be able to handle complex multi-agent scenarios. 

Rather than building monolithic agents that try to do everything, build small, focused agents that do one thing well. Each agent will have its own context and its own set of tools.

# Design Rules
The project will have the following traits:
- Modern python code with Pydantic [Models](https://docs.pydantic.dev/latest/concepts/models/), [Types](https://docs.pydantic.dev/latest/concepts/types/), [Validators](https://docs.pydantic.dev/latest/concepts/validators/), and [Fields](https://docs.pydantic.dev/latest/concepts/fields/) as backend for type annotations and checks
- Templated prompt manipulation for dynamic context adaptations, you could reference [Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- Compact error handling for self-healing agent operations
    - Self-Healing: The LLM can read the error message and figure out what to change in a subsequent tool call
    - Durable: The agent can continue to run even if one tool call fails
- Unified execution state and business state
    - Execution state: current step, next step, waiting status, retry counts, etc.
    - Business state: What's happened in the agent workflow so far (e.g. list of OpenAI messages, list of tool calls and results, etc.)
- Extensive memory design for agents might select few-shot examples (episodic memories) for examples of desired behavior, instructions (procedural memories) to steer behavior, or facts (semantic memories) for task-relevant context.
    - Episodic memories: Examples of desired behavior from the past
    - Procedural memories: Instructions to steer the agent's behavior
    - Semantic memories: Facts relevant to the current task
- Modular code design that breaks down a complex software system into smaller, independent, and reusable components called modules. Each module focuses on a specific functionality, making it easier to develop, test, and debug. 
- Clear and consice documentations for both code and project. You could reference [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) and [PEP8 Style Guide for Python Code](https://peps.python.org/pep-0008/)
- Use python>=3.12 syntax strictly. Type hinting is required and native annotation is preferred (list, tuple, ...; rather than List, Tuple, Optional...).
- Use relative imports wherever possible for better code readability and maintainability.
- Try to avoid raising general exceptions and log errors with `traceback.format_exc()` for details.

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

# Multi-Agent Implementation
Let's construct the following agents.

| Agent    | Reference                                                                        | LLM Model Name                 |
|:---------|:---------------------------------------------------------------------------------|-------------------------------:|
| Planner  | https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking | google/gemini-2.5-pro          |
| Think    | [think_collection.py](../gaia/services/intelligence/think_collection.py)         | deepseek/deepseek-r1-0528:free |
| Search   | [search_collection.py](../gaia/services/tools/search_collection.py)              | google/gemini-2.5-pro          |
| Browser  | https://docs.browser-use.com/quickstart                                          | google/gemini-2.5-pro          |
| Document | https://www.datalab.to/app/pages/documentation                                   | google/gemini-2.5-pro          |
| Audio    | https://glama.ai/mcp/servers/@hugohow/mcp-music-analysis                         | google/gemini-2.5-pro          |
| Image    | https://ai.google.dev/gemini-api/docs/image-understanding                        | google/gemini-2.5-pro          |
| Video    | https://ai.google.dev/gemini-api/docs/video-understanding                        | google/gemini-2.5-pro          |
| Coder    | https://e2b.dev/docs/quickstart                                                  | anthropic/claude-sonnet-4      |

## LLM Settings
We use [OpenRouter](https://openrouter.ai) as provider and [Gemini-2.5-pro](https://openrouter.ai/google/gemini-2.5-pro) as the LLM model. You could reference [Gemini API](https://openrouter.ai/google/gemini-2.5-pro/api) for the standard implementation.

Notice: use native google genai api for image and video agents. [Gemini API quickstart](https://ai.google.dev/gemini-api/docs/quickstart).

## Base Agent
The base agent is responsible for accepting natural language input and producing structured outputs. It serves as the foundation for all other agents.

It introduces the basic interface, the [control flow](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md) and the [memory]() for agents.

Each agent is initialized with LLM model as the core component. You should check [OpenRouter](https://openrouter.ai/google/gemini-2.5-pro/api) for the standard implementation. Watch carefully for different modality inputs, such as image, audio, or file.

All agents should follow the same interface, and use LLM to hanlde the task by utilizing proper functions, tools, and workflows.

## Planner Agent
This agent utilizes the reasoning model to break down complex problems into manageable subproblems. Each subproblem could be distributed to a different agent.

- INPUT: a natural language description of the problem and a set of descriptions of available agents
- OUTPUT: a detailed execution plan

Capabilities:
- MCP: [向左看](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- LLM Provider: openrouter
- LLM Model: google/gemini-2.5-pro

## Think Agent
This agent utilizes the reasoning model to answer complex questions.

Supports advanced reasoning for:
    - Mathematical problems and proofs
    - Code contest and programming challenges
    - Logic puzzles and riddles
    - Competition-level STEM problems
    - Multi-step analytical reasoning

- INPUT: a natural language description of the question
- OUTPUT: a triplet tuple (reasoning trace, answer, confidence level)
    - reasoning trace: a detailed description of the reasoning trace
    - answer: the final answer to the question
    - confidence level: a measure of the agent's confidence in the answer

Capabilities:
- Implementation Reference: [think_collection.py](../gaia/services/intelligence/think_collection.py)
- LLM Provider: openrouter
- LLM Model: deepseek/deepseek-r1-0528:free

## Search Agent
This agent utilizes Goole Search API to fetch the relevant documents given the user query.

- INPUT: the user query
- OUTPUT: a list of documents, with each document structured as the following
    - url: the url of the document
    - title: the title of the document
    - summary: the summary of the document

Capabilities:
- Implementation Reference: [search_collection.py](../gaia/services/tools/search_collection.py)
- Implementation Document: [Google Search API](https://developers.google.com/custom-search/v1/overview)
- LLM Provider: openrouter
- LLM Model: google/gemini-2.5-pro

## Browser Agent
This agent utilizes [browser-use](https://github.com/browser-use/browser-use) for web browsing.

- INPUT: a natural language description of the task
- OUTPUT: a triplet tuple (execution trace, answer, downloaded files/images paths)
    - execution trace: a detailed description of the execution trace
    - answer: the final answer to the task
    - downloaded files/images paths: a list of paths to the downloaded files/images

Capabilities:
- Implementation Reference: [browser_collection.py](../gaia/services/tools/browser_collection.py)
- Implementation Document: [browser-use](https://docs.browser-use.com/quickstart)
- LLM Provider: openrouter
- LLM Model: google/gemini-2.5-pro


## Document Agent
This agent utilizes [marker-pdf](https://www.datalab.to/app/pages/documentation) for document processing.

- INPUT: a natural language description of the task and the document file uri path
- OUTPUT: a triplet tuple (converted markdown content, extracted images/resources paths, summary)
    - converted markdown content: the converted markdown content
    - extracted images/resources paths: a list of paths to the extracted images/resources
    - summary: the summary of the document

Capabilities:
- Implementation Document: [marker-pdf](https://www.datalab.to/app/pages/documentation)
- LLM Provider: openrouter
- LLM Model: google/gemini-2.5-pro


## Audio Agent
This agent utilizes [audio-mcp-server](https://glama.ai/mcp/servers/@hugohow/mcp-music-analysis) for audio processing.

- INPUT: a natural language description of the task and the audio file uri path
- OUTPUT: an answer to the task

Capabilities:
- MCP: [Audio Analysis](https://glama.ai/mcp/servers/@hugohow/mcp-music-analysis)
- LLM Provider: openrouter
- LLM Model: google/gemini-2.5-pro

## Image Agent
This agent utilizes [Google Gemini - Image Understanding](https://ai.google.dev/gemini-api/docs/image-understanding) for image reasoning.

- INPUT: a natural language description of the task and the image file uri path
- OUTPUT: an answer to the task

Capabilities:
- Implementation Document: [Google Gemini - Image Understanding](https://ai.google.dev/gemini-api/docs/image-understanding)
- LLM Provider: Google
- LLM Model: gemini-2.5-pro

## Video Agent
This agent utilizes [Google Gemini - Video Understanding](https://ai.google.dev/gemini-api/docs/video-understanding) for video reasoning.

- INPUT: a natural language description of the task and the video file uri path
- OUTPUT: an answer to the task

Capabilities:
- Implementation Document: [Google Gemini - Video Understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- LLM Provider: Google
- LLM Model: gemini-2.5-pro

## Coder Agent
This agent solves code-related task (calculation, data analysis, validation, third-party apis, etc.) using the flexible workflow:
1. Generate python code snipet using `anthropic/claude-sonnet-4`
    1.1. Research the task given all inputs
    1.2. Generate a general implementation requirements
    1.3. List a detailed procedure satisfying the requirements
    1.4. Generate the final code snipet
    1.5. Identify necessary third-party packages for executions
2. Execute code using [E2B Code Sandbox](https://e2b.dev/docs/quickstart)
3. Check the result
    3.1. If the result is correct, return the result
    3.2. If the result is incorrect, repeat the workflow

- INPUT: a natural language description of the task and the relevant context (initial code snipet, error messages, fetched docs, etc.)
- OUTPUT: a triplet tuple (final code snipet, response, assets)
    - final code snipet: the final code snipet
    - response: the terminal text output or trace
    - assets: assets generated during the code execution, such as temporary files, images, etc

Capabilities:
- Implementation Reference: [code_collection.py](../gaia/services/intelligence/code_collection.py)
- Implementation Document: [E2B Code Sandbox](https://e2b.dev/docs/quickstart)
- LLM Provider: openrouter
- LLM Model: google/gemini-2.5-pro

# Memory Implementation
The memory layer provides tractable and scalable memory for not only a single agent but a group of agents sharing the critical context. You could reference [Memory Design](https://github.com/browser-use/browser-use/tree/0.2.7/browser_use/agent/memory) and [Memory Injection](https://github.com/browser-use/browser-use/blob/0.2.7/browser_use/agent/service.py).