import json
import os
import random

from autogen import ConversableAgent, AssistantAgent
from autogen import GroupChat
from autogen import GroupChatManager

# The Number Agent always returns the same numbers.
qwn_32b_llm_config = {"model": "qwen:32b", "api_key": 'ollama',"base_url":"http://127.0.0.1:11434/v1"}
llama3_8b_llm_config = {"model": "llama3:8b", "api_key": 'ollama', "base_url": "http://192.168.0.11:11434/v1"}
yi_llm_config = {"model": "yi-34b-chat-0205", "api_key": '1f2808c63ec94c369999da6e3b13056c',"base_url":"https://api.lingyiwanwu.com/v1"}
openai_llm_config = {"model": "gpt-4", "api_key": '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'}
zhipu_llm_config = {"model": "glm-4", "api_key": '094eaeab9c33bacde4365f834e4f259a.TGRRXWqpYE3FPyFx','base_url':'https://open.bigmodel.cn/api/paas/v4'}
deepseek_llm_config = {"model": "deepseek-chat", "api_key": 'sk-e64f21fb757148a59a8a2edc23094ab2','base_url':'https://api.deepseek.com/v1'}
# llm_config_list = [qwn_32b_llm_config, llama3_8b_llm_config, yi_llm_config, openai_llm_config, zhipu_llm_config, deepseek_llm_config]
llm_config_list = [yi_llm_config,zhipu_llm_config,deepseek_llm_config,qwn_32b_llm_config,openai_llm_config]
role_descriptions = {
    "狼人": "狼人需要在夜晚选择一名玩家进行杀害，白天则需要隐藏自己的身份，通过误导和欺骗来保护自己和同伴。",
    "村民": "村民需要通过讨论和投票来找出狼人，并在夜晚保护自己不被杀害。",
    "预言家": "预言家在夜晚可以查看一名玩家的身份，白天则需要决定是否公开自己的身份和所看到的信息。",
    "女巫": "女巫拥有一瓶解药和一瓶毒药。在夜晚，女巫可以选择使用解药来救活一名被狼人杀害的玩家，或者使用毒药来杀害一名玩家。",
    "猎人": "猎人在被狼人杀害或者被村民误杀时，可以选择带走一名玩家。",
    "守卫": "守卫可以选择在夜晚保护一名玩家不被杀害，但不能连续两晚保护同一名玩家。"
}
werewolf_tips_dict = {
    "观察和分析": ["注意玩家的发言和行为，寻找矛盾和不一致之处。", "观察玩家的投票行为，看是否有玩家总是与多数人一致。", "分析玩家的逻辑和推理，看是否有玩家的发言显得过于牵强或不合逻辑。"],
    "伪装和欺骗": ["狼人需要学会伪装成村民，避免引起怀疑。", "使用逻辑和推理来支持自己的观点，同时也可以适当提出一些模糊的线索来迷惑村民。", "在必要时，可以牺牲队友来转移注意力，但要确保这样做不会暴露自己的身份。"],
    "信息收集": ["尽量收集关于其他玩家的信息，包括他们的角色、行为模式和可能的策略。", "通过提问和讨论来获取更多信息，但要注意不要显得过于急切。"],
    "投票策略": ["在投票时，尽量不要让自己的投票显得过于明显，以免成为狼人的目标。", "如果你是村民，尽量与多数人保持一致，但也要注意不要盲目跟随。", "如果你是狼人，可以尝试引导村民的投票，或者在关键时刻改变投票方向。"],
    "角色扮演": ["根据自己的角色，扮演好自己的角色，无论是狼人还是村民。", "狼人要尽量避免暴露自己的身份，而村民则要尽量揭露狼人的身份。"],
    "团队协作": ["狼人之间需要有良好的协作，共同制定策略和计划。", "村民也需要通过讨论和投票来协作，找出狼人。"],
    "保持冷静": ["游戏过程中可能会出现紧张和混乱的情况，保持冷静，不要被情绪影响判断。", "如果你是狼人，即使局势不利也不要慌张，寻找机会扭转局面。"],
    "学习和适应": ["每次游戏后，回顾自己的表现，学习其他玩家的策略和技巧。", "根据不同的游戏情况和玩家群体，调整自己的策略和行为。"]
}

all_player = []
for num in range(1,12):
    player_assistant = AssistantAgent(f"player_{num}", llm_config={"config_list": [random.choice(llm_config_list)]},
                            system_message=f'你现在正在参与一个叫做狼人杀的游戏,规则是这样的:  '
                                           '游戏分为狼人阵营和村民阵营，游戏开始的时候,游戏主持人会告诉你和你队友的身份.游戏的目标是通过夜晚的行动和白天的讨论来找出并消灭对方阵营的成员。 '
                                           # f'{json.dumps(role_descriptions)}  '
                                           f'  你只返回你自己角色应该说的话,不要编写代码 '
                                           f'  你要尽量隐藏自己的身份,误导对面的阵营做出错误的选择,可以指责 '
                                           # f'  狼人需要学会伪装成村民，避免引起怀疑  在必要时，可以牺牲队友来转移注意力  根据自己的角色，扮演好自己的角色，无论是狼人还是村民。 '
                                           # f'以下是一些技巧和提示:  {json.dumps(werewolf_tips_dict)}'
                                      )
    all_player.append(player_assistant)

game_master = AssistantAgent(
    "GameMaster",
    llm_config={"config_list": [zhipu_llm_config]},
    system_message="你是狼人杀游戏的主持人,负责游戏的进行，包括分配角色、引导夜晚行动、宣布白天的讨论结果和投票结果，以及确保游戏规则的正确执行。游戏主持人是游戏的中立裁判，需要确保所有玩家都有公平的游戏体验，同时也要处理游戏中的突发事件和争议。主持人不会参与游戏的推理和投票过程，以保持游戏的公正性"
                   "你在游戏的开始的时候,需要给每个玩家分配角色   "
                   "在游戏的过程中,记录被"
                   "投票出局或者被狼人杀,被女巫毒死,被猎人带走的玩家,他们将不能说话,跳过他们的回合",
    human_input_mode="NEVER",
)
all_player.append(game_master)
group_chat = GroupChat(
    agents=all_player,
    messages=[],
    send_introductions=True,
    max_round=100,
    speaker_selection_method= 'round_robin'
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": [zhipu_llm_config]},
)
chat_result = group_chat_manager.initiate_chat(
    game_master,
    message="狼人杀游戏开始, 请 Game Master 开始这个游戏,并且在第一局给每个玩家分配角色.直到最后游戏结束  "
            "游戏的局势和发言顺序由 Game Master 控制,如果玩家被杀 跳过此玩家的回合"
            "所有对话全部使用中文回答",
    summary_method="reflection_with_llm",
)