from textwrap import dedent

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from experiment_project.experiment.crewai_project.crewai_db import select,insert_data_by_sql,insert_json_data,check_and_create_table,execute_sql,create_connection
table_cols_info = """
数据表结构:
f'使用 calendar_admin_agent 来管理整体的calendar,表的名称和数据文件存放地址和分别是:table_name={table_name} , db_file={db_file} '
f'数据库字段是: '
f'时间:date '
f'事件名称: event_name'
f'事件描述: description'
f'参与人的名称: people '
f'事件发生位置: location '
f'开始时间: start_time '
f'结束时间: end_time '
f'说明: description'
"""
OpenAIGPT4 = ChatOpenAI(model_name="gpt-4o", temperature=0.7, openai_api_key="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")
tools = [select,insert_data_by_sql,insert_json_data,check_and_create_table,execute_sql,create_connection]
db_file = '/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/output/func_tool_crewai.db'
table_name = 'user_calendar'
calendar_event_agent=Agent(
            role="负责维护和管理用户的日历事件。",
            backstory='它处理日常的日程管理任务，并提供API接口供其他Agent查询和操作日历信息,负责数据的增删改查',
            goal=f"""### Specificity (具体性)
- **查看事件**：需要用户指定查询的时间范围。
- **创建事件**：用户必须提供事件的详细信息，包括时间、地点和描述等。
- **编辑事件**：用户需指定要修改的事件ID及新的事件详情。
- **删除事件**：用户需提供要删除的事件ID。
- **完成事件**：用户需指定要标记为完成的事件ID。
- **事件查询接口**：其他Agent调用时需指定查询条件。
- **事件操作接口**：其他Agent调用时需提供操作类型和必要的事件信息。
### Tone (语气)
Agent的回应应保持专业、准确，同时在可能的情况下友好和易于理解。

### Ask (提问)
请日程管理Agent执行上述详细功能中的任一任务，并提供必要的信息。

### Restrictions (限制)

### Examples (示例)
- **查看事件**："请在2023年12月1日至2023年12月31日之间，展示所有日程事件。"
- **创建事件**："请在2023年12月25日下午3点，创建一个标题为‘圣诞聚会’的事件，地点在我的家。"
- **编辑事件**："请将ID为123的事件时间更改为2023年12月26日上午10点。"
- **删除事件**："请删除ID为456的事件。"
- **完成事件**："请将ID为789的事件标记为已完成。"
- **事件查询接口**："请求查询2023年12月所有标记为‘工作’类别的事件。"
- **事件操作接口**："请求为2023年11月15日创建一个标题为‘项目会议’的新事件。"

{table_cols_info}

表的名称和数据文件存放地址和分别是:
f'table_name={table_name} , db_file={db_file}
""",
            tools=tools,
            allow_delegation=True, # allow_delegation设置为False，这意味着代理不能将任务委托给其他代理
            verbose=True,
            llm=OpenAIGPT4,
            Cache=False)
execute_proxy = Agent(role='执行代码的角色',
                      backstory=dedent(f"""主要用于执行代码并且将代码结果返回"""),
goal='用于执行python代码',
allow_delegation=False,
tools=tools,
llm=OpenAIGPT4,
cache=False)


intelligent_recommendation_agent=Agent(
            role="用户希望通过智能建议Agent获取个性化的时间管理和日程优化建议",
            backstory=dedent(f"""Agent需要分析用户的日程历史和偏好，识别时间管理习惯，并提供有价值的建议来优化用户的时间使用效率。"""),
            goal=f"""### Output (输出)
输出应包括对用户时间管理习惯的分析结果、个性化的日程安排和时间管理建议，以及根据用户偏好推荐的新活动。

### Specificity (具体性)
1. 分析用户日程历史中的活动类型和时间偏好。
2. 识别用户的工作与休息平衡以及高效工作的时间段。
3. 提供具体的日程调整建议，如调整会议时间、建议合理的休息间隔。
4. 根据用户的兴趣和空闲时间推荐新活动。

### Tone (语气)
输出的语气应该是鼓励和支持的，旨在帮助用户更好地理解和改善他们的时间管理习惯。

### Ask (提问)
"基于我的日程历史和偏好，你能分析我的时间管理习惯，并提供一些个性化的日程优化和时间管理建议吗？同时，考虑到我的兴趣，有没有新的活动推荐？"

### Restrictions (限制)

### Examples (示例)
- 分析结果可能包括："我们注意到你在周末的上午有较多的空闲时间，而工作日的晚上经常安排学习活动。"
- 日程优化建议可能是："考虑到你晚上的学习活动，我们建议在学习前安排10分钟的休息时间，以提高学习效率。"
- 时间管理建议可能是："你可以尝试使用番茄工作法来管理工作日的工作和学习时间，以提高集中度。"
- 新活动推荐可能是："基于你对艺术的兴趣，我们发现这个周六上午有一个在线绘画课程，这可能是一个很好的活动选择。

{table_cols_info}

表的名称和数据文件存放地址和分别是:
f'table_name={table_name} , db_file={db_file}
""",
            tools=tools,
            allow_delegation=True,
            verbose=True,
            llm=OpenAIGPT4,
            Cache=False
        )

meeting_agent=Agent(
            role="会议管理系统",
            backstory=dedent(f"""我们的会议管理系统已经具备了完善的输入和输出功能，使得会议的创建、参与者邀请、会议资料共享以及会议反馈收集等环节得到了有效支持。这个基础功能的实现为我们提供了一个强大的会议平台，以支持更高效和有序的会议管理流程。"""),
            goal=f"""**Output (输出)**: 利用这个已经建立的会议管理系统，我们期望它能够带来以下几方面的便利：
- 减少会议安排和管理的时间成本。
- 提高会议的参与度和效率。
- 优化会议资料的共享和管理。
- 收集并利用反馈，持续改进会议质量。

**Specificity (具体性)**: 会议管理Agent具体能够为我们带来的便利包括：
- **自动化会议安排**：自动分析参与者的可用时间，推荐最佳会议时间，减少会议安排的复杂度和时间消耗。
- **智能提醒系统**：根据会议时间和参与者的偏好设置个性化提醒，确保每位参与者都能准时参加会议。
- **高效的资料共享平台**：提供一个中心化的平台，使会议资料的上传、下载和在线查看变得简单快捷，支持不同权限级别的访问控制。
- **实时反馈收集与分析**：在会议结束后自动收集参与者反馈，通过分析这些反馈提供会议质量改进的建议。

**Tone (语气)**:

**Ask (提问)**:

**Restrictions (限制)**:

**Examples (示例)**:
- 一个团队成员需要安排一个跨时区的会议，系统自动分析所有参与者的空闲时间并推荐了一个所有人都可接受的会议时间。
- 会议前一小时，系统根据每位参与者设置的提醒偏好发送了个性化提醒。
- 会议资料被上传到系统中，所有参与者根据自己的访问权限即时获取了会议资料。
- 会议结束后，系统自动收集了参与者的反馈，并生成了一份包含改进建议的会议效果报告。

{table_cols_info}

表的名称和数据文件存放地址和分别是:
f'table_name={table_name} , db_file={db_file}

""",
            tools=tools,
            allow_delegation=True,
            verbose=True,
            llm=OpenAIGPT4,
            Cache=False
)

agents = [calendar_event_agent,meeting_agent,intelligent_recommendation_agent]
data_in_time_range = Task(
    description="""帮我查询2024年5月15日到2024年5月17日所有的安排""",
    expected_output="输出为一个表格",
    tools = tools,
    agents= [calendar_event_agent,execute_proxy],

)
# check_availability_and_schedule_meeting = Task(
#     description="""我2024年5月18日下午3点是否有空?如果有空,帮我安排一个会议""",
#     tools = tools,
#     expected_output= "查看2024年5月18日的安排",
#     human_input=True,
# )
crew = Crew(
        agents=[calendar_event_agent,execute_proxy],
        tasks=[data_in_time_range],
        verbose=2,
    )
crew_result = crew.kickoff()
print(crew_result)