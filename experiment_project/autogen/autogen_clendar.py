import copy
import json
import os
import random
from autogen import ConversableAgent, AssistantAgent, UserProxyAgent
from autogen import GroupChat
from autogen import GroupChatManager
from autogen.graph_utils import visualize_speaker_transitions_dict
import matplotlib.pyplot as plt
from autogen.token_count_utils import count_token


def get_agent_of_name(agents, name) -> ConversableAgent:
    for agent in agents:
        if agent.name == name:
            return agent


def add_all_values_to_each_other(data:dict):
    """
    对字典d中的每一对键，将它们的值相互添加。

    参数:
    d (dict): 目标字典。
    """
    # 获取所有键的列表
    keys = list(data.keys())

    # 遍历所有键的组合
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            key1 = keys[i]
            key2 = keys[j]

            # 将key1的值添加到key2的值列表中，如果它还不在那里的话
            if key1 not in data[key2]:
                data[key2].append(key1)

            # 将key2的值添加到key1的值列表中，如果它还不在那里的话
            if key2 not in data[key1]:
                data[key1].append(key2)
    return data

# 示例


# The Number Agent always returns the same numbers.
qwn_32b_llm_config = {"model": "qwen:32b", "api_key": 'ollama', "base_url": "http://127.0.0.1:11434/v1"}
llama3_8b_llm_config = {"model": "llama3:8b", "api_key": 'ollama', "base_url": "http://192.168.0.11:11434/v1"}
yi_llm_config = {"model": "yi-34b-chat-0205", "api_key": '1f2808c63ec94c369999da6e3b13056c',
                 "base_url": "https://api.lingyiwanwu.com/v1"}
openai_llm_config = {"model": "gpt-4", "api_key": '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'}
zhipu_llm_config = {"model": "glm-4", "api_key": '094eaeab9c33bacde4365f834e4f259a.TGRRXWqpYE3FPyFx',
                    'base_url': 'https://open.bigmodel.cn/api/paas/v4'}
deepseek_llm_config = {"model": "deepseek-chat", "api_key": 'sk-e64f21fb757148a59a8a2edc23094ab2',
                       'base_url': 'https://api.deepseek.com/v1'}
# llm_config_list = [qwn_32b_llm_config, llama3_8b_llm_config, yi_llm_config, openai_llm_config, zhipu_llm_config, deepseek_llm_config]
llm_config_list = [yi_llm_config, zhipu_llm_config, deepseek_llm_config, qwn_32b_llm_config, openai_llm_config]
meeting_scheduling_flow  = {
'User': '通过群聊界面发起会议请求,提供初始信息(如会议主题、拟定时间等)',
'group_chat_agent': '接收用户请求,开始收集和提取关键信息,可能会与用户进行多轮对话以获取更多必要细节;将收集到的信息传递给meeting_topic_agent;将会议主题建议呈现给用户,并获取用户的选择或确认;将相关信息(如主题、参与者、拟定时间等)传递给schedule_recommender;将推荐的会议时间提供给用户选择或确认;将用户选定的会议时间连同其他会议细节(主题、参与者等)发送给conflict_detector;根据conflict_detector的结果,与用户进行确认或重新选择时间;将最终的会议细节发送给schedule_manager;在整个过程中,如果用户有任何关于日程的查询(如某天的安排),可以将查询请求转发给calendar_query,由它负责处理查询并返回结果',
'meeting_topic_agent': '分析收到的信息,提取关键词和主题,可能会结合参与者的角色和专业知识,生成会议主题建议,并将其返回给group_chat_agent',
'schedule_recommender': '综合考虑参与者的日程安排、会议室的可用性等因素,推荐可行的会议时间,并将结果返回给group_chat_agent',
'conflict_detector': '检查选定的会议时间是否与参与者的现有日程存在冲突,如果没有冲突,返回"无冲突"结果;如果有冲突,提供解决建议(如重新选择时间),并将结果返回给group_chat_agent',
'schedule_manager': '正式创建会议日程,将其添加到日历中,设置提醒,并生成会议通知;将会议通知发送给所有参与者,可能通过group_chat_agent转发',
'calendar_query': '负责处理用户关于日程的查询并返回结果'
}
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "/mnt/d/project/dy/extra/autogen/output","use_docker":False},)
calendar_assistant_info = {'schedule_manager':f'日程管理agent: '
                                                 f'负责管理用户的日程安排,包括添加、删除、修改日程 '
                                                 f'能够根据优先级、时间等对日程进行排序、分类'
                                                 f'可以设置日程提醒,在日程开始前提醒用户 ',
                           'calendar_query':f'日历查询agent: '
                                               f'负责处理用户对日历的各种查询,如查询某天、某周、某月的日程安排 '
                                               f'可以按类别、时间段等条件筛选和汇总日程'
                                               f'能生成日、周、月的日程总览 ',
                           'conflict_detector':f'日程冲突检测agent: '
                                                  f'在添加新日程时,检查是否与已有日程存在时间冲突 '
                                                  f'如果发现冲突,提示用户,并给出建议的解决方案,如重新安排时间',
                           'schedule_recommender':f'第三方服务集成agent : '
                                                  f'负责与第三方日历服务(如Google Calendar)进行数据同步 '
                                                  f'定期从第三方日历拉取数据,发现新的日程变化',
                           'group_chat_agent':f'实现群聊交互功能 : '
                                                  f'在群聊中与其他人类或机器人交互,收集相关信息 '
                                                  f'提取关键信息,如会议主题、时间、地点、参与者等 '
                                                  f' 根据收集到的信息生成会议日程'
                                                  f' 可以考虑参与者的时间安排、会议室的可用性等因素'
                                                  f' 生成一个结构化的会议日程数据',
                           'meeting_topic_agent':f'实现会议主题的功能 : '
                                                  f'分析群聊中的讨论内容,提取关键词和主题 '
                                                  f'获取参与者的角色和expertise信息 '
                                                  f' 根据讨论内容和参与者信息生成会议主题建议'
                                                  f' 总结会议内容,生成会议报告',
                           'calendar_manage':'用于控制整个calendar系统'}
speaker_transitions_dict,all_agents,user_list = {},[],['user_A','user_B']
for user_name in user_list:
    user_agents = []
    for explanation_name, explanation in calendar_assistant_info.items():

        explanation_agent = AssistantAgent(f"{user_name}_{explanation_name}", llm_config={"config_list": [random.choice(llm_config_list)]},
                                   system_message=explanation
                                   )
        user_agents.append(explanation_agent)
    allowed_speaker_transitions_dict = {user_agents[-1]: [other_agent for other_agent in user_agents] for agent in user_agents}
    speaker_transitions_dict.update(allowed_speaker_transitions_dict)
    all_agents+=user_agents
calendar_manage_agents = add_all_values_to_each_other(speaker_transitions_dict)

# visualize_speaker_transitions_dict(speaker_transitions_dict, all_agents)


group_chat = GroupChat(
    agents=all_agents,
    messages=[],
    send_introductions=True,
    max_round=6,
    allowed_or_disallowed_speaker_transitions=speaker_transitions_dict,
    speaker_transitions_type='allowed'
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": [zhipu_llm_config]},
)



chat_result = user_proxy.initiate_chat(
    group_chat_manager,
    message="假设我现在有两个角色,user_A和user_B,A角色在中国,周一到周五每天早8.30到下午5.30是工作时间,周末双休,B角色在美国纽约,工作时间是早9.30到下午6.30,周末双休.   "
            "模拟B角色在群聊中约A,约一个关于Autogen的讨论会议,分别询问双方是否有时间,最后完成会议安排"
            "不需要实际上的代码  只需要逻辑就可以了  ",
            # f" 下面是系统逻辑 {json.dumps(meeting_scheduling_flow)}",
            # "假设一个场景，有A，B，C，D四个人，通过Instant Messaging，A的机器人助手小冰为他们四人定一个会议，请分别模拟A，B，C，D和小冰，模拟一个他们的对话过程，直到确定一切细节，小冰发会议通知给大家。",
    summary_method="reflection_with_llm",
)


#
# teams = ["A", "B", "C"]
# team_size = 5
#
#
#
#
#
# # Create a list of 15 agents 3 teams x 5 agents
# agents = [ConversableAgent(name=f"{team}{i}", llm_config=False) for team in teams for i in range(team_size)]
#
# # Loop through each team and add members and their connections
# for team in teams:
#     for i in range(team_size):
#         member = f"{team}{i}"
#         # Connect each member to other members of the same team
#         speaker_transitions_dict[get_agent_of_name(agents, member)] = [
#             get_agent_of_name(agents, name=f"{team}{j}") for j in range(team_size) if j != i
#         ]
#
# # Team leaders connection
# print(get_agent_of_name(agents, name="B0"))
# speaker_transitions_dict[get_agent_of_name(agents, "A0")].append(get_agent_of_name(agents, name="B0"))
# speaker_transitions_dict[get_agent_of_name(agents, "B0")].append(get_agent_of_name(agents, name="C0"))
#
# visualize_speaker_transitions_dict(speaker_transitions_dict, agents)


# short_prediction_model_path = '/opt/cc/StockFormer/code/Transformer/pretrained/csi/Short/checkpoint.pth'
# long_prediction_model_path =  '/opt/cc/StockFormer/code/Transformer/pretrained/csi/Long/checkpoint.pth'
# mae_model_path = '/opt/cc/StockFormer/code/Transformer/pretrained/csi/mae/checkpoint.pth'
# full_stock_dir = '/opt/cc/StockFormer/data/CSI/'
