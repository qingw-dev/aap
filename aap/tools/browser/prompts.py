# Extended system prompt for browser automation
extended_browser_system_prompt = """
10. URL ends with .pdf
- If the go_to_url function with `https://any_url/any_file_name.pdf` as the parameter, just report the url link and hint the user to download using `download` mcp tool or `curl`, then execute `done` action.

11. Robot Detection:
- If the page is a robot detection page, abort immediately. Then navigate to the most authoritative source for similar information instead

# Efficiency Guidelines
0. if download option is available, always **DOWNLOAD** as possible! Also, report the download url link in your result.
1. Use specific search queries with key terms from the task
2. Avoid getting distracted by tangential information
3. If blocked by paywalls, try archive.org or similar alternatives
4. Document each significant finding clearly and concisely
5. Precisely extract the necessary information with minimal browsing steps.
"""
