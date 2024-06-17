import os
from typing import Optional, Union
from crewai_tools import tool


def set_api_keys(
    model_api_key: str,
    module_api_url: Union[str] = None,
    model_name: Union[str] = None,
    model_max_tokens: Union[int,str] = None
) -> None:
    os.environ["OPENAI_API_KEY"] = model_api_key

    if module_api_url:
        os.environ["OPENAI_API_BASE"] = module_api_url
    if model_name:
        os.environ["OPENAI_MODEL_NAME"] = model_name
    if model_max_tokens:
        os.environ["OPENAI_MAX_TOKENS"] = str(model_max_tokens)

def make_crewai_tool(func):
    tool.name = func.__name__
    return tool(func)
