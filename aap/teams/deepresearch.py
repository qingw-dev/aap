import os

from aworld.agents.llm_agent import Agent
from aworld.config.conf import AgentConfig, ModelConfig
from aworld.core.agent.swarm import TeamSwarm
from aworld.core.task import TaskResponse
from aworld.planner.plan import PlannerOutputParser
from aworld.runner import Runners
from examples.multi_agents.deepresearch.prompts import (
    plan_sys_prompt,
    reporting_sys_prompt,
    search_sys_prompt,
)
from examples.tools.common import Tools


def get_deepresearch_swarm() -> TeamSwarm:
    agent_config = AgentConfig(
        llm_config=ModelConfig(
            llm_model_name=os.getenv("MODEL_NAME"),
            llm_base_url=os.getenv("BASE_URL"),
            llm_api_key=os.getenv("API_KEY"),
        ),
        use_vision=False,
    )

    agent_id = "planner_agent"
    plan_agent = Agent(
        agent_id=agent_id,
        name="planner_agent",
        desc="planner_agent",
        conf=agent_config,
        use_tools_in_prompt=True,
        resp_parse_func=PlannerOutputParser(agent_id).parse,
        system_prompt_template=plan_sys_prompt,
    )

    web_search_agent = Agent(
        name="web_search_agent",
        desc="web_search_agent",
        conf=agent_config,
        system_prompt_template=search_sys_prompt,
        tool_names=[Tools.SEARCH_API.value],
    )

    reporting_agent = Agent(
        name="reporting_agent",
        desc="reporting_agent",
        conf=agent_config,
        system_prompt_template=reporting_sys_prompt,
    )

    return TeamSwarm(plan_agent, web_search_agent, reporting_agent, max_steps=1)


if __name__ == "__main__":
    user_input = "7天北京旅游计划"
    swarm: TeamSwarm = get_deepresearch_swarm()
    result: TaskResponse = Runners.sync_run(input=user_input, swarm=swarm)
    print("deepresearch result: ", result)
