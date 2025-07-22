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