from aworld.core.agent.base import AgentFactory
from aworld.core.context.base import Context
from aworld.core.event.base import Message
from aworld.runners.hook.hook_factory import HookFactory
from aworld.runners.hook.hooks import PostLLMCallHook, PreLLMCallHook
from aworld.utils.common import convert_to_snake


@HookFactory.register(
    name="LogObservationHook",
    desc="log observation before the LLM call",
)
class LogObservationHook(PreLLMCallHook):
    def name(self) -> str:
        return convert_to_snake("LogObservationHook")

    async def exec(self, message: Message, context: Context = None) -> Message:
        agent = AgentFactory.agent_instance(message.sender)
        context = agent.context
        context.context_info.set("step", 1)
        return message


@HookFactory.register(
    name="LogActionLLMHook",
    desc="log actions after the LLM call",
)
class LogActionLLMHook(PostLLMCallHook):
    def name(self) -> str:
        return convert_to_snake("LogActionLLMHook")

    async def exec(self, message: Message, context: Context = None) -> Message:
        agent = AgentFactory.agent_instance(message.sender)
        context = agent.context
        assert context.context_info.get("step") == 1
        return message
