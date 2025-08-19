MCP_CONFIG = {
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
