
from autogen import AssistantAgent, UserProxyAgent
import autogen

from extra.autogen.log_token import load_log_token, create_sqlite_db_name

log_db_name = create_sqlite_db_name()
logging_session_id = autogen.runtime_logging.start(config={"dbname": log_db_name})

deepseek_llm_config = {"model": "deepseek-chat", "api_key": 'sk-e64f21fb757148a59a8a2edc23094ab2','base_url':'https://api.deepseek.com/v1'}
yi_llm_config = {"model": "yi-34b-chat-0205", "api_key": '1f2808c63ec94c369999da6e3b13056c',"base_url":"https://api.lingyiwanwu.com/v1"}
openai_llm_config = {"model": "gpt-4", "api_key": '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'}
zhipu_llm_config = {"model": "glm-4", "api_key": '094eaeab9c33bacde4365f834e4f259a.TGRRXWqpYE3FPyFx','base_url':'https://open.bigmodel.cn/api/paas/v4'}

assistant = AssistantAgent("assistant", llm_config={"config_list": [openai_llm_config]},human_input_mode='NEVER')
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "/mnt/d/project/dy/extra/autogen/output","use_docker":False},)
user_proxy.initiate_chat(assistant, message="生成一个 NVDA 和 TESLA 2021年至今股价变化图,按照png的格式保存到本地")
autogen.runtime_logging.stop()
print(load_log_token(logging_session_id=logging_session_id,dbname=log_db_name, table="chat_completions"))