import os
import autogen
from autogen import ConversableAgent
from extra.autogen.log_token import create_sqlite_db_name, load_log_token

# The Number Agent always returns the same numbers.
qwn_32b_llm_config = {"model": "qwen:32b", "api_key": 'ollama',"base_url":"http://127.0.0.1:11434/v1"}
qwn_16b_llm_config = {"model": "qwen:14b", "api_key": 'ollama',"base_url":"http://192.168.0.11:11434/v1"}
llama3_16b_llm_config = {"model": "llama3:8b", "api_key": 'ollama',"base_url":"http://192.168.0.11:11434/v1"}
yi_llm_config = {"model": "yi-34b-chat-0205", "api_key": '1f2808c63ec94c369999da6e3b13056c',"base_url":"https://api.lingyiwanwu.com/v1"}
openai_llm_config = {"model": "gpt-4", "api_key": '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'}
zhipu_llm_config = {"model": "glm-4", "api_key": '094eaeab9c33bacde4365f834e4f259a.TGRRXWqpYE3FPyFx','base_url':'https://open.bigmodel.cn/api/paas/v4'}
deepseek_llm_config = {"model": "deepseek-chat", "api_key": 'sk-e64f21fb757148a59a8a2edc23094ab2','base_url':'https://api.deepseek.com/v1'}
llm_config_list = [qwn_32b_llm_config,llama3_16b_llm_config,yi_llm_config,openai_llm_config,zhipu_llm_config,deepseek_llm_config]
llm_config_list = [openai_llm_config]
log_db_name = create_sqlite_db_name()
logging_session_id = autogen.runtime_logging.start(config={"dbname": log_db_name})
number_agent = ConversableAgent(
    name="Number_Agent",
    system_message="You return me the numbers I give you, one number each line.",
    # 你把我给你的数字还给我，每行一个数字。
    llm_config={"config_list": llm_config_list},
    human_input_mode="NEVER",
)

# The Adder Agent adds 1 to each number it receives.
adder_agent = ConversableAgent(
    name="Adder_Agent",
    system_message="You add 1 to each number I give you and return me the new numbers, one number each line.",
    # 你给我的每个数字加 1，然后把新数字还给我，每行一个数字。
    llm_config={"config_list": llm_config_list},
    human_input_mode="NEVER",
)

# The Multiplier Agent multiplies each number it receives by 2.
multiplier_agent = ConversableAgent(
    name="Multiplier_Agent",
    system_message="You multiply each number I give you by 2 and return me the new numbers, one number each line.",
    # 你把我给你的每个数字乘以 2，然后把新数字还给我，每行一个数字。
    llm_config={"config_list": llm_config_list},
    human_input_mode="NEVER",
)

# The Subtracter Agent subtracts 1 from each number it receives.
subtracter_agent = ConversableAgent(
    name="Subtracter_Agent",
    system_message="You subtract 1 from each number I give you and return me the new numbers, one number each line.",
    # 你从我给你的每个数字中减去 1，然后把新数字还给我，每行一个数字。
    llm_config={"config_list": llm_config_list},
    human_input_mode="NEVER",
)

# The Divider Agent divides each number it receives by 2.
divider_agent = ConversableAgent(
    name="Divider_Agent",
    system_message="You divide each number I give you by 2 and return me the new numbers, one number each line.",
    # 你把我给你的每个数字除以 2，然后把新数字还给我，每行一个数字。
    llm_config={"config_list": llm_config_list},
    human_input_mode="NEVER",
)

chat_results = number_agent.initiate_chats(
    [
        {
            "recipient": adder_agent,
            "message": "14",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": multiplier_agent,
            "message": "These are my numbers",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": subtracter_agent,
            "message": "These are my numbers",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": divider_agent,
            "message": "These are my numbers",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
    ]
)
autogen.runtime_logging.stop()
print(load_log_token(logging_session_id=logging_session_id,dbname=log_db_name, table="chat_completions"))