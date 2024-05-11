import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen import ConversableAgent,GroupChat,GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor


openai_llm_config = {"model": "gpt-4", "api_key": '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'}
zhipu_llm_config = {"model": "glm-4", "api_key": '094eaeab9c33bacde4365f834e4f259a.TGRRXWqpYE3FPyFx','base_url':'https://open.bigmodel.cn/api/paas/v4'}



financial_tasks = [
    """Nvidia和Tesla目前的股价是多少，过去一个月的百分比变化表现如何？""",
    """利用市场新闻调查股票表现的可能原因?""",
]

writing_tasks = ["""使用提供的任何信息撰写一篇吸引人的博客文章"""]

financial_assistant = autogen.AssistantAgent(
    name="Financial_assistant",
    llm_config=zhipu_llm_config,
)
research_assistant = autogen.AssistantAgent(
    name="Researcher",
    llm_config=zhipu_llm_config,
)
writer = autogen.AssistantAgent(
    name="writer",
    llm_config=openai_llm_config,
    system_message="""
       您是一名专业作家，以富有洞察力和引人入胜的文章而闻名。您把复杂的概念转化为引人入胜的叙事。当一切都完成时，请回复“终止”。
        """,
)

user_proxy_auto = autogen.UserProxyAgent(
    name="User_Proxy_Auto",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    human_input_mode="ALWAYS",  # ask human for input at each step
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)


chat_results = autogen.initiate_chats(
    [
        {
            "sender": user_proxy_auto,
            "recipient": financial_assistant,
            "message": financial_tasks[0],
            "clear_history": True,
            "silent": False,
            "summary_method": "last_msg",
        },
        {
            "sender": user_proxy_auto,
            "recipient": research_assistant,
            "message": financial_tasks[1],
            "max_turns": 2,  # max number of turns for the conversation (added for demo purposes, generally not necessarily needed)
            "summary_method": "reflection_with_llm",
        },
        {
            "sender": user_proxy,
            "recipient": writer,
            "message": writing_tasks[0],
            "carryover": "I want to include a figure or a table of data in the blogpost.",  # additional carryover to include to the conversation (added for demo purposes, generally not necessarily needed)
        },
    ]
)