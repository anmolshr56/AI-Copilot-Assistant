from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from backend.llm_config import get_llm
from datetime import datetime

search_tool = DuckDuckGoSearchRun()

def get_current_time(_input=""):
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

time_tool = Tool(
    name="Current Time",
    func=get_current_time,
    description="Returns current date and time"
)

def get_agent_response(query, use_cloud=True):
    llm = get_llm(use_cloud=use_cloud)

    query_lower = query.lower()

    # Force time tool
    if "time" in query_lower or "date" in query_lower or "day" in query_lower:
        return f"Current Date & Time: {get_current_time()}"

    # Force search tool
    if (
        "latest" in query_lower
        or "news" in query_lower
        or "search" in query_lower
        or "current" in query_lower
    ):
        try:
            result = search_tool.run(query)
            return result
        except Exception as e:
            return f"Search Error: {str(e)}"

    # Normal LLM chat
    try:
        return llm.invoke(query)
    except Exception as e:
        return f"LLM Error: {str(e)}"