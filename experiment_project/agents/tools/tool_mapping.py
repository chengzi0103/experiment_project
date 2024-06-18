from typing import List, Union

from experiment_project.agents.tools.util import stock_data
from experiment_project.utils.date.util import now_time
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

from langchain.tools import DuckDuckGoSearchRun


tool_mapping = {'now_time':now_time,'stock_data':stock_data,'DuckDuckGoSearchRun':DuckDuckGoSearchRun}

def agent_tools(tool_names:Union[List[str],None]=None):
    if tool_names is None:
        return []
    tools = []
    for tool_name in tool_names:
        tool_func = tool_mapping.get(tool_name, None)
        if tool_func is not None:
            tools.append(tool_func)
    return tools
