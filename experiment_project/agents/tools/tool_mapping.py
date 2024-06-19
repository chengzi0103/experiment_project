from typing import List, Union

from experiment_project.agents.tools.util import stock_data, whisper_translate_audio, text_rag
from experiment_project.utils.date.util import now_time
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from crewai_tools import TXTSearchTool
from langchain.tools import DuckDuckGoSearchRun
from crewai_tools import PDFSearchTool

def get_tool_func(func_name:str):
    tool_mapping = {'now_time':now_time,'stock_data':stock_data,'DuckDuckGoSearchRun':DuckDuckGoSearchRun,'text_rag':text_rag,'whisper_translate_audio':whisper_translate_audio,'TXTSearchTool':TXTSearchTool(),'PDFSearchTool':PDFSearchTool()}
    return tool_mapping.get(func_name,None)

def agent_tools(tool_names:Union[List[str],None]=None):
    if tool_names is None:
        return []
    tools = []
    for tool_name in tool_names:
        # tool_func = tool_mapping.get(tool_name, None)
        tool_func = get_tool_func(func_name=tool_name)
        if tool_func is not None:
            tools.append(tool_func)
    return tools
