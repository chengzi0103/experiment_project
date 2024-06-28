from typing import List, Union
from experiment_project.agents.tools.util import stock_data, whisper_translate_audio, text_rag
from experiment_project.utils.date.util import now_time
# from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from crewai_tools import TXTSearchTool
# from langchain.tools import DuckDuckGoSearchRun

from experiment_project.utils.files.read import read_excel
from experiment_project.utils.rag.embedding.huggingface import load_embedding_model
from experiment_project.utils.rag.vector.pgvector import create_pgvector, delete_vector_collection, \
    upload_files_to_vector, search_vector

# TXTSearchTool 会出现这个问题
# 024-06-28 17:29:12,928 - 139805933430336 - _common.py-_common:105 - INFO: Backing off send_request(...) for 0.2s (requests.exceptions.SSLError: HTTPSConnectionPool(host='us-api.i.posthog.com', port=443): Max retries exceeded with url: /batch/ (Caused by SSLError(SSLError(1, '[SSL] record layer failure (_ssl.c:1006)'))))
# 2024-06-28 17:29:12,954 - 139805925037632 - _common.py-_common:105 - INFO: Backing off send_request(...) for 0.7s (requests.exceptions.SSLError: HTTPSConnectionPool(host='us-api.i.posthog.com', port=443): Max retries exceeded with url: /batch/ (Caused by SSLError(SSLError(1, '[SSL] record layer failure (_ssl.c:1006)'))))
# 2024-06-28 17:29:12,982 - 139805916644928 - _common.py-_common:105 - INFO: Backing off send_request(...) for 0.9s (requests.exceptions.SSLError: HTTPSConnectionPool(host='us-api.i.posthog.com', port=443): Max retries exceeded with url: /batch/ (Caused by SSLError(SSLError(1, '[SSL] record layer failure (_ssl.c:1006)'))))
# 2024-06-28 17:29:13,002 - 139805908252224 - _common.py-_common:105 - INFO: Backing off send_request(...) for 1.0s (requests.exceptions.SSLError: HTTPSConnectionPool(host='us-api.i.posthog.com', port=443): Max retries exceeded with url: /batch/ (Caused by SSLError(SSLError(1, '[SSL] record layer failure (_ssl.c:1006)'))))
# 2024-06-28 17:29:13,029 - 139805899859520 - _common.py-_common:105 - INFO: Backing off send_request(...) for 0.2s (requests.exceptions.SSLError: HTTPSConnectionPool(host='us-api.i.posthog.com', port=443): Max retries exceeded with url: /batch/ (Caused by SSLError(SSLError(1, '[SSL] record layer failure (_ssl.c:1006)'))))
# 2024-06-28 17:29:13,106 - 1398


def get_tool_func(func_name:str):
    # tool_mapping = {'now_time':now_time,'stock_data':stock_data,'DuckDuckGoSearchRun':DuckDuckGoSearchRun,'text_rag':text_rag,'whisper_translate_audio':whisper_translate_audio,'TXTSearchTool':TXTSearchTool(),'PDFSearchTool':PDFSearchTool(),'read_excel':read_excel,'create_pgvector':create_pgvector,'delete_vector_collection':delete_vector_collection,'upload_files_to_vector':upload_files_to_vector,"search_vector":search_vector,"load_embedding_model":load_embedding_model}
    tool_mapping = {'now_time':now_time,'stock_data':stock_data,'text_rag':text_rag,'whisper_translate_audio':whisper_translate_audio,'read_excel':read_excel,'create_pgvector':create_pgvector,'delete_vector_collection':delete_vector_collection,'upload_files_to_vector':upload_files_to_vector,"search_vector":search_vector,"load_embedding_model":load_embedding_model}
    # tool_mapping = {'now_time':now_time,'stock_data':stock_data,'text_rag':text_rag,'whisper_translate_audio':whisper_translate_audio,'read_excel':read_excel,}
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
