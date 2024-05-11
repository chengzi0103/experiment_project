# pip3 install pyautogen pyautogen[graph]
import os
import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen import ConversableAgent,GroupChat,GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor

executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir='/mnt/d/project/dy/extra/autogen',  # Use the temporary directory to store the code files.
)
# llm_config = {"model": "qwen:32b", "api_key": 'ollama',"base_url":"http://127.0.0.1:11434/v1"}
qwn_32b_llm_config = {"model": "qwen:32b", "api_key": 'ollama',"base_url":"http://127.0.0.1:11434/v1"}
qwn_16b_llm_config = {"model": "qwen:14b", "api_key": 'ollama',"base_url":"http://192.168.0.11:11434/v1"}
llama3_16b_llm_config = {"model": "llama3:8b", "api_key": 'ollama',"base_url":"http://192.168.0.11:11434/v1"}
yi_llm_config = {"model": "yi-34b-chat-0205", "api_key": '1f2808c63ec94c369999da6e3b13056c',"base_url":"https://api.lingyiwanwu.com/v1"}
openai_llm_config = {"model": "gpt-4", "api_key": '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'}
zhipu_llm_config = {"model": "glm-4", "api_key": '094eaeab9c33bacde4365f834e4f259a.TGRRXWqpYE3FPyFx','base_url':'https://open.bigmodel.cn/api/paas/v4'}
deepseek_llm_config = {"model": "deepseek-chat", "api_key": 'sk-e64f21fb757148a59a8a2edc23094ab2','base_url':'https://api.deepseek.com/v1'}

# assistant = AssistantAgent("assistant", llm_config=zhipu_llm_config)
#
user_proxy = UserProxyAgent("Admin", code_execution_config={"work_dir": "/mnt/d/project/dy/extra/autogen", "use_docker": False},system_message='人类管理员。与规划者互动，讨论计划。计划执行需要此管理员的批准。')


qwen = AssistantAgent(
    "Qwen",
    system_message="我是'Qwen'，一个精通Python和AI的程序员。我擅长编写高质量的代码并解决复杂的逻辑问题。我将与团队成员紧密合作，共同推进项目的技术实现。",
    llm_config={"config_list":[qwn_32b_llm_config]},
    human_input_mode="NEVER",
    code_execution_config={"executor": executor},
)

yi = AssistantAgent(
    "Yi",
    system_message="我叫'Yi'，专长于Python和AI领域。我的强项是逻辑思维和算法设计，致力于在项目中实现创新的解决方案。我期待与队友们共同克服技术挑战，实现目标。",
    llm_config={"config_list": [yi_llm_config]},
    human_input_mode="NEVER",
    code_execution_config={"executor": executor},
)


zhipu = AssistantAgent(
    "ZhiPu",
    system_message="我是'ZhiPu'，项目副组长，精通Python和AI。我负责团队协调和任务分配，利用我的管理能力和技术知识，确保项目顺利进行.",
    llm_config={"config_list": [zhipu_llm_config]},
    human_input_mode="NEVER",  # Never ask for human input.
code_execution_config={"executor": executor},

)
openai = AssistantAgent(
    "Openai",
    system_message="我是'Openai'，项目管理和需求分析专家。作为团队领导，我将负责规划和任务拆分，以及提供AI领域的技术指导，带领团队达成目标。",
    llm_config={"config_list": [zhipu_llm_config]},
    human_input_mode="NEVER",  # Never ask for human input.
code_execution_config={"executor": executor},
)

deepseek = AssistantAgent(
    "DeepSeek",
    system_message="我是'DeepSeek'，专长于Python和AI领域。我的强项是逻辑思维和算法设计，致力于在项目中实现创新的解决方案。我期待与队友们共同克服技术挑战，实现目标。",
    llm_config={"config_list": [deepseek_llm_config]},
    human_input_mode="NEVER",  # Never ask for human input.
code_execution_config={"executor": executor},
)
llama3 = AssistantAgent(
    "Llama3",
    system_message="我是'Llama3'，专长于Python和AI领域。我的强项是逻辑思维和算法设计，致力于在项目中实现创新的解决方案。我期待与队友们共同克服技术挑战，实现目标。",
    llm_config={"config_list": [deepseek_llm_config]},
    human_input_mode="NEVER",  # Never ask for human input.
code_execution_config={"executor": executor},
)

group_chat = GroupChat(
    agents=[zhipu, yi,qwen,openai,deepseek,llama3],
    # agents=[qwen, yi,zhipu],
    messages=[],
    # max_round=15,
    send_introductions=True, # Send introductions to all agents# \
    # allow_repeat_speaker=False, # 不允许一个代理连续发言
)
manage_group = GroupChatManager(
    name="manage",
    system_message="我是'manage'，负责监督和管理整个团队",
    llm_config={"config_list": [llama3_16b_llm_config]},
    # max_consecutive_auto_reply=15,
    groupchat=group_chat,
)

chat_result  = user_proxy.initiate_chat(manage_group, message="我现在想实现一个功能,就是自动快速的生成图数据库的模型.以下是我的需求"
                                                              "1, 我有很多的数据,包括不同的文件,但是这个数据读取和数据清理不是重点,不用太多注意"
                                                              "2, 我的核心需求是如何利用当前的技术,快速的构建基于图数据库的模型? 例如,我有一个 三体小说.txt 那么我应该如何快速的创建出里面所有的知识图谱网络  例如 (事件,地点,人物) 他们每个实体的具体细节和关系  "
                                                              "3, 我想尽可能的使用 nlp + langchain + llm 这几个ai的框架,但是只要能完成这个任务都可以,技术框架不限"
                                                              "下面是我对团队中的职位和定位"
                                                              "项目组长: Openai,主要负责分析需求和管理团队,负责这个任务更好的完成"
                                                              "项目副组长: ZhiPu,主要负责团队协调和任务分配,辅助组长完成这个项目,如果有开发人员技术不到位,协助开发人员完成代码开发"
                                                              # "项目开发人员: Yi, 主要对分析出来的需求进行代码编写和测试"
                                                              "项目开发人员: Qwen, 主要对分析出来的需求进行代码编写和测试"
                                                              "项目开发人员: DeepSeek, 主要对分析出来的需求进行代码编写和测试"
                                                              "项目开发人员: Llama3, 主要对分析出来的需求进行代码编写和测试"
                                                              "请你们通力合作,一起完成这个项目把"
                                                              "注意,如果项目组中的每个人员收到的内容是空的话,请跳过这一次查询"

                                                              ,summary_method="reflection_with_llm")

# chat_result  = user_proxy.initiate_chat(manage_group, message="数30游戏,请在游戏开始后第一个玩家从1开始数，每人每轮可以给原数字增加1~3个数，然后看谁先数到30，谁就输了! "
#                                                               "请Qwen选手先开始 让我看看谁最后会输",summary_method="reflection_with_llm")