import os

from aworld.agents.llm_agent import Agent
from aworld.config.conf import AgentConfig
from aworld.core.agent.swarm import TeamSwarm
from aworld.core.task import TaskResponse
from aworld.planner.plan import PlannerOutputParser
from aworld.runner import Runners
from examples.multi_agents.deepresearch.prompts import plan_sys_prompt


class MultiAgentTeam:
    """
    Represents a team of multi-agent systems.
    """

    def __init__(self) -> None:
        """
        Initializes the MultiAgentTeam with a list of agents.

        :param agents: Dict of agents in the team.
        """
        self.mcp_config = {
            "mcpServers": {
                # third-party tools
                "music-analysis": {
                    "command": "uvx",
                    "args": ["-n", "mcp-music-analysis"],
                },
                "sequential-thinking": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-sequential-thinking",
                    ],
                },
                "code": {
                    "command": "npx",
                    "args": ["-y", "@e2b/mcp-server"],
                    "env": {
                        "E2B_API_KEY": "${E2B_API_KEY}",
                    },
                },
                "terminal": {
                    "command": "uvx",
                    "args": ["terminal_controller"],
                },
                # agent tools
                "browser-use": {
                    "command": "python",
                    "args": ["-m", "aap.tools.browser.service"],
                },
                "document": {
                    "command": "python",
                    "args": ["-m", "aap.tools.document.service"],
                    "env": {
                        "DATALAB_API_KEY": "${DATALAB_API_KEY}",
                    },
                },
                "search": {
                    "command": "python",
                    "args": ["-m", "aap.tools.search.service"],
                },
                "image": {
                    "command": "python",
                    "args": ["-m", "aap.tools.image.service"],
                },
                "video": {
                    "command": "python",
                    "args": ["-m", "aap.tools.video.service"],
                },
                "think": {
                    "command": "python",
                    "args": ["-m", "aap.tools.think.service"],
                },
            }
        }
        self.agent_config = AgentConfig(
            llm_model_name=os.getenv(
                "MODEL_NAME",
                "google/gemini-2.5-pro",
            ),
            llm_base_url=os.getenv("BASE_URL", "https://openrouter.ai/api/v1"),
            llm_api_key=os.getenv("API_KEY", ""),
            llm_temperature=float(os.getenv("TEMPERATURE", "1.0")),
        )

        main_agent: Agent = Agent(
            agent_id="main_agent",
            name="main_agent",
            desc="main_agent",
            conf=self.agent_config,
            use_tools_in_prompt=True,
            resp_parse_func=PlannerOutputParser("main_agent").parse,
            system_prompt_template=plan_sys_prompt,
            # system_prompt=(
            #     "You are a leading agent in the multi-agent system. "
            #     "You are responsible for planning subtask given the task, "
            #     "then coordinate with other agents by dispatching subtasks "
            #     "to other expert agents. "
            #     "Finally, you will collect the results from all agents, "
            #     "then reflect on the results and provide a final answer."
            # ),
        )
        search_agent: Agent = Agent(
            conf=self.agent_config,
            name="search_agent",
            desc=(
                "Provide Google search ability to "
                "fetch relevant documents based on the task."
            ),
            mcp_servers=["search"],
            mcp_config=self.mcp_config,
        )
        browser_agent: Agent = Agent(
            conf=self.agent_config,
            name="browser_agent",
            desc=(
                "Control a web browser to interact with web pages. "
                "Could read web content with flexible information gathering."
            ),
            mcp_servers=["browser-use"],
            mcp_config=self.mcp_config,
        )
        document_agent: Agent = Agent(
            conf=self.agent_config,
            name="document_agent",
            desc=(
                "Process document using Datalab SDK with advanced OCR capabilities. "
                "Convert document to markdown foramt. "
                "Support PDFs, DOCX, XLSX, PPTX, HTML, and images."
            ),
            mcp_servers=["document"],
            mcp_config=self.mcp_config,
        )
        audio_agent: Agent = Agent(
            conf=self.agent_config,
            name="audio_agent",
            desc="Answer audio file related questions.",
            mcp_servers=["music-analysis"],
            mcp_config=self.mcp_config,
        )
        image_agent: Agent = Agent(
            conf=self.agent_config,
            name="image_agent",
            desc="Answer image file related questions.",
            mcp_servers=["image"],
            mcp_config=self.mcp_config,
        )
        video_agent: Agent = Agent(
            conf=self.agent_config,
            name="video_agent",
            desc="Answer video file related questions.",
            mcp_servers=["video"],
            mcp_config=self.mcp_config,
        )
        think_agent: Agent = Agent(
            conf=self.agent_config,
            name="think_agent",
            desc=(
                "Process complex reasoning tasks with structured output. "
                "Handles mathematical proofs, programming challenges, "
                "and logical problems "
                "while maintaining processing context and metadata."
            ),
            mcp_servers=["think"],
            mcp_config=self.mcp_config,
        )
        code_agent: Agent = Agent(
            conf=self.agent_config,
            name="code_agent",
            desc="Write code to solve problems.",
            mcp_servers=["code", "terminal"],
            mcp_config=self.mcp_config,
        )
        self.swarm = TeamSwarm(
            main_agent,
            # tool agents
            browser_agent,
            search_agent,
            document_agent,
            # media agents
            audio_agent,
            image_agent,
            video_agent,
            # thinking agents
            think_agent,
            code_agent,
            # params
            max_steps=100,
        )

    def run(self, task: str) -> TaskResponse:
        """
        Runs the multi-agent team on a given task.

        :param task: The task to be executed by the team.
        """
        result: TaskResponse = Runners.sync_run(
            task,
            swarm=self.swarm,
        )
        return result


if __name__ == "__main__":
    team: MultiAgentTeam = MultiAgentTeam()
    result: TaskResponse = team.run(
        task="A paper about AI regulation that was originally submitted to arXiv.org in June 2022 shows a figure with three axes, where each axis has a label word at both ends. Which of these words is used to describe a type of society in a Physics and Society article submitted to arXiv.org on August 11, 2016?"
    )
    # agent: SingleAgentTest = SingleAgentTest()
    # result: TaskResponse = agent.run(
    #     "Search AntGroup then report the first document url."
    # )
    print(f"{result.answer=}")
