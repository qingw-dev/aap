import os

from aworld.agents.llm_agent import Agent
from aworld.config.conf import AgentConfig
from aworld.runner import Runners
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()

    mcp_config = {
        "mcpServers": {
            # thrid-party mcp servers
            "code": {
                "command": "npx",
                "args": ["-y", "@e2b/mcp-server"],
                "env": {
                    "E2B_API_KEY": "${E2B_API_KEY}",
                },
            },
            # agent tools
            "browser-use": {
                "command": "python",
                "args": ["-m", "aap.tools.browser.service"],
            },
            "search": {
                "command": "python",
                "args": ["-m", "aap.tools.search.service"],
            },
        }
    }

    browser: Agent = Agent(
        agent_id="browser",
        name="browser",
        desc="browser",
        conf=AgentConfig(
            llm_model_name=os.getenv(
                "MODEL_NAME",
                "google/gemini-2.5-pro",
            ),
            llm_base_url=os.getenv("BASE_URL", "https://openrouter.ai/api/v1"),
            llm_api_key=os.getenv("API_KEY", ""),
            llm_temperature=float(os.getenv("TEMPERATURE", "1.0")),
        ),
        mcp_config=mcp_config,
        mcp_servers=["browser-use", "search", "code"],
    )

    task = "给我获取https://huggingface.co/datasets/xbench/DeepSearch数据源地址"
    result = Runners.sync_run(task, agent=browser)
    print(f"{result=}")
