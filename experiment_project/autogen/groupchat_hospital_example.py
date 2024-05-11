import autogen
from autogen import AssistantAgent, GroupChat, GroupChatManager
from extra.autogen.log_token import load_log_token, create_sqlite_db_name

import random
log_db_name = create_sqlite_db_name()

qwn_32b_llm_config = {"model": "qwen:32b", "api_key": 'ollama' ,"base_url" :"http://127.0.0.1:11434/v1"}
qwn_16b_llm_config = {"model": "qwen:14b", "api_key": 'ollama' ,"base_url" :"http://192.168.0.11:11434/v1"}
llama3_16b_llm_config = {"model": "llama3:8b", "api_key": 'ollama' ,"base_url" :"http://192.168.0.11:11434/v1"}
yi_llm_config = {"model": "yi-34b-chat-0205", "api_key": '1f2808c63ec94c369999da6e3b13056c'
                 ,"base_url" :"https://api.lingyiwanwu.com/v1"}
openai_llm_config = {"model": "gpt-4", "api_key": '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'}
zhipu_llm_config = {"model": "glm-4", "api_key": '094eaeab9c33bacde4365f834e4f259a.TGRRXWqpYE3FPyFx'
                    ,'base_url' :'https://open.bigmodel.cn/api/paas/v4'}
deepseek_llm_config = {"model": "deepseek-chat", "api_key": 'sk-e64f21fb757148a59a8a2edc23094ab2'
                       ,'base_url' :'https://api.deepseek.com/v1'}
llm_config_list = [yi_llm_config ,openai_llm_config ,zhipu_llm_config
                   ,deepseek_llm_config]
logging_session_id = autogen.runtime_logging.start(config={"dbname": log_db_name})

# 患者代理
user_agent = AssistantAgent(
   name="liming",
   system_message='你是一个人类，姓名：橙子，25岁，男，昨天打球时脚崴了',
    llm_config={"config_list": [random.choice(llm_config_list)]},
    human_input_mode="NEVER",
)

# 挂号代理
registered_agent = AssistantAgent(
    name="registered",
    system_message="你是医院的挂号系统，患者来到医院，引导患者完成挂号。需要根据患者选择的科室推荐对应科室的医生及收费情况，当患者选择对应医生并且输入对应医生的挂号费用时，告诉患者:挂号完成，并可前往诊室候诊 ",
    llm_config={"config_list": [random.choice(llm_config_list)]},
    human_input_mode="NEVER",
    # function_map={
    #     "get_doctor_info": get_doctor_info
    # }
)

#护士代理
nurse_agent = AssistantAgent(
    name="nurse",
    system_message="你是医院护士，为患者进行基础护理和专业护理,执行医嘱，配合各项诊疗工作，了解病人的病情状况和情绪状态，协调与病人和医生的沟通工作",
    llm_config={"config_list": [random.choice(llm_config_list)]},
    human_input_mode="NEVER"
)

# 医生代理，可以创建多个
doctor_zhao_agent = AssistantAgent(
    name="doctor_zhao",
    system_message="你是一名骨科医生，名字赵六，只接收挂号完成的患者，应该介绍自己然后询问患者病情，根据患者病情给予合适的治疗方案,并开具对应的药品处方",
    llm_config={"config_list": [random.choice(llm_config_list)]},
    human_input_mode="NEVER"
)

# 药房代理
medicine_agent = AssistantAgent(
    name="medicine_store",
    system_message="你是一名药房管理员，根据用户的处方及缴费信息给用户出售对应的药品，当用户未缴费时提醒用户先去缴费窗口进行缴费",
    llm_config={"config_list": [random.choice(llm_config_list)]},
    human_input_mode="NEVER"
)

# 收费代理
cashier_agent = AssistantAgent(
    name="cashier",
    system_message="你是一名药品收费员，根据用户的处方收取对应药品的费用，当用户输入费用时,代表用户缴费完成,并开具收据，提醒用户取药房取药",
    llm_config={"config_list": [random.choice(llm_config_list)]},
    human_input_mode="NEVER"
)
group_chat = GroupChat(
    agents=[user_agent, registered_agent, doctor_zhao_agent, medicine_agent, cashier_agent,nurse_agent],
    messages=[],
    max_round=25,
    send_introductions=True
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": [openai_llm_config]},
    system_message = '患者就诊完毕后结束对话,不需要患者和医院进行多余的告别'

)

user_agent.initiate_chat(
    group_chat_manager,
    message="你好,我的脚受伤了",
    summary_method="last_msg",
)

autogen.runtime_logging.stop()
print(load_log_token(logging_session_id=logging_session_id,dbname=log_db_name, table="chat_completions"))