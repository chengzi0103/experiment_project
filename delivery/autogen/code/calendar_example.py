import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, register_function
from experiment_project.experiment.calendar_project.tools.data import create_user_event
from experiment_project.utils.agent.util import create_sqlite_db_name
from experiment_project.utils.database.sqlite.util import create_connection, execute_sql, \
    check_and_create_table, insert, select, insert_sql
from experiment_project.utils.files.read import read_yaml

secret_env_file = 'env_secret_config.yaml'
log_db_name = create_sqlite_db_name()
logging_session_id = autogen.runtime_logging.start(config={"dbname": log_db_name})

db_file = '/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/output/func_tool.db'
table_name = 'user_calendar'
api_configs = read_yaml(secret_env_file)
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
user_proxy = UserProxyAgent(name='user', system_message='真实的用户',
                            code_execution_config={"work_dir": "/mnt/d/project/dy/extra/autogen/output",
                                                   "use_docker": False})
execute_proxy = UserProxyAgent(name='Execute_Proxy', system_message='你是一个代码执行器'
                                                                    f'table_name={table_name} , db_file={db_file}',
                               llm_config=None,
                               code_execution_config={"work_dir": "/mnt/d/project/dy/extra/autogen/output",
                                                      "use_docker": False}, human_input_mode="NEVER")

calendar_enenvt_agent = AssistantAgent(name="calendar_enenvt_agent", system_message=f"""
### Context (上下文)
作为日历系统的核心组件，日程管理Agent负责维护和管理用户的日历事件。它处理日常的日程管理任务，并提供API接口供其他Agent查询和操作日历信息。

### Output (输出)
期望输出包括对日程管理任务的反馈和执行结果，如成功查看、创建、编辑、删除和完成事件的确认信息，以及通过API接口返回的查询结果或操作反馈。

### Specificity (具体性)
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

表的名称和数据文件存放地址和分别是:
f'table_name={table_name} , db_file={db_file}
{table_cols_info}
""", llm_config=api_configs.get('openai'), human_input_mode='NEVER', )

intelligent_recommendation_agent = AssistantAgent(name="intelligent_recommendation_agent", system_message=f"""
### Context (上下文)
用户希望通过智能建议Agent获取个性化的时间管理和日程优化建议。Agent需要分析用户的日程历史和偏好，识别时间管理习惯，并提供有价值的建议来优化用户的时间使用效率。

### Output (输出)
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
- 新活动推荐可能是："基于你对艺术的兴趣，我们发现这个周六上午有一个在线绘画课程，这可能是一个很好的活动选择。"
表的名称和数据文件存放地址和分别是:
f'table_name={table_name} , db_file={db_file}
{table_cols_info}
""", llm_config=api_configs.get('openai'), human_input_mode='ALWAYS')

interoperability_broker_agent = AssistantAgent(name="interoperability_broker_agent", system_message=f"""
Context (上下文): 在多系统集成环境中，需要一个能够促进系统间交互和数据交换的中介——Interoperability Broker Agent (IBA)。IBA的主要职责是封装系统内部方法为标准API，供外部系统调用，同时也负责调用外部系统的API，并处理数据转换、安全认证等集成相关的任务。

Output (输出): IBA提供一系列标准化的API接口，实现数据和方法的互操作性，并确保数据交换的安全性和可靠性。它还记录详细的日志，包括成功和失败的调用，以便监控和故障排除。

Specificity (具体性): IBA需要实现以下关键功能：

方法暴露与封装
外部服务调用
数据转换与映射
集成工作流管理
安全与访问控制
错误处理与可靠性
监控与日志记录
Tone (语气):
说明性和指导性，提供清晰的指示和步骤，以便于开发人员理解和实现IBA的功能。

Ask (提问):


Restrictions (限制):

Examples (示例):
IBA如何封装一个内部方法并暴露为API
IBA如何调用外部系统的API并处理返回结果

{table_cols_info}
""", llm_config=api_configs.get('deepseek'), human_input_mode='ALWAYS')

meeting_agent = AssistantAgent(name="meeting_agent", system_message=f"""
**Context (上下文)**:
我们的会议管理系统已经具备了完善的输入和输出功能，使得会议的创建、参与者邀请、会议资料共享以及会议反馈收集等环节得到了有效支持。这个基础功能的实现为我们提供了一个强大的会议平台，以支持更高效和有序的会议管理流程。

**Output (输出)**: 利用这个已经建立的会议管理系统，我们期望它能够带来以下几方面的便利：
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

表的名称和数据文件存放地址和分别是:
f'table_name={table_name} , db_file={db_file}
{table_cols_info}
""", llm_config=api_configs.get('deepseek'), human_input_mode='ALWAYS')

calendar_admin_agent = AssistantAgent(name="calendar_admin_agent", system_message=f"""
**Context (上下文)**:
在现代工作环境中，一个高效、智能的日历系统对于提高个人和团队的生产效率至关重要。Calendar Admin Agent作为这个系统的核心管理组件，通过协调内部各Agent的工作并处理外部输入，确保了系统的高效运行和用户体验的优化。

**Objective (目标)**:
设计Calendar Admin Agent，使其能够有效地管理和优化日历系统的运行，提供智能化的提醒服务，同时通过API集成支持外部系统的接入，以提升整个系统的自动化和智能化水平。

**Specificity (具体性)**:
1. **系统协调与维护**：监控系统运行状态，执行维护任务以确保稳定性。
2. **外部输入处理与API集成**：作为统一接口处理外部请求，支持与外部系统的集成。
3. **提醒功能管理**：提供多样化提醒类型和通知方式，支持用户自定义设置。
4. **Agent组件配置与优化**：优化内部Agent组件的设置，提升服务质量和效率。
5. **安全与权限管理**：实施安全措施和用户权限管理，保护数据和信息安全。
6. **数据与资源管理**：管理关键数据和资源，确保数据准确性和资源高效使用。
7. **用户支持与反馈**：提供用户支持服务，收集反馈以优化系统功能。

**Tone (语气)**:


**Ask (提问)**:

**Restrictions (限制)**:

**Examples (示例)**:
- 用户需要在每周一早上9点前收到本周会议安排的提醒。Calendar Admin Agent通过提醒功能管理，自动设置并发送提醒，用户可以通过电子邮件或手机短信接收。
- 企业需要将内部开发的任务管理工具与日历系统集成。通过Calendar Admin Agent提供的API接口，实现了无缝集成，使任务更新能实时反映在用户的日历上。
- 系统监测到某个内部Agent响应延迟，Calendar Admin Agent立即调整该Agent的资源分配，确保了系统的流畅运行。

表的名称和数据文件存放地址和分别是:
f'table_name={table_name} , db_file={db_file}
{table_cols_info}
""", llm_config=api_configs.get('openai'), human_input_mode='ALWAYS')

agent_list = [calendar_enenvt_agent, intelligent_recommendation_agent, interoperability_broker_agent, meeting_agent,
              calendar_admin_agent]
for agent in agent_list:
    agent.register_for_llm(name='create_user_event',
                           description="Generate a person's calendar data for n days according to the given number")(
        create_user_event)
    agent.register_for_llm(name='sqlite_create_connection',
                           description="This function attempts to connect to a SQLite database at the specified path. If the connection is successful, it returns the connection object; otherwise, it prints the error and returns None.")(
        create_connection)
    agent.register_for_llm(name='sqlite_execute_sql',
                           description="This function establishes a connection to the database, creates a cursor, and executes the provided SQL command. If params is provided, it binds these parameters to the SQL command. After execution, it commits the transaction and returns the cursor object. It ensures the database connection is closed before exiting.")(
        execute_sql)
    agent.register_for_llm(name='sqlite_check_and_create_table',
                           description="This function checks if a table with the specified name exists in the database. If the table does not exist, it executes the provided SQL command to create the table. It prints messages indicating whether the table was found or created.")(
        check_and_create_table)
    agent.register_for_llm(name='sqlite_insert',
                           description="This function processes the provided keyword arguments, converting lists to comma-separated strings if necessary. It then constructs and executes an INSERT SQL command to insert the data into the specified table.")(
        insert_sql)
    agent.register_for_llm(name='sqlite_select',
                           description="This function executes the provided SELECT SQL command and returns all fetched rows as a list of tuples. If the cursor is None (indicating an error), it returns an empty list.")(
        select)
execute_proxy.register_for_execution(name='sqlite_select', )(select)
execute_proxy.register_for_execution(name='sqlite_insert', )(insert_sql)
execute_proxy.register_for_execution(name='sqlite_check_and_create_table', )(check_and_create_table)
execute_proxy.register_for_execution(name='sqlite_execute_sql', )(execute_sql)
execute_proxy.register_for_execution(name='sqlite_create_connection', )(create_connection)
execute_proxy.register_for_execution(name='create_user_event', )(create_user_event)

agent_list.append(execute_proxy)
group_chat = GroupChat(
    agents=agent_list,
    messages=[],
    send_introductions=True
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": [api_configs.get('openai')]},
    system_message='')

user_proxy.initiate_chat(group_chat_manager,
                         message="统计我在各个事件上面的事件占用比,根据不同的事务和事件对我进行提醒",
                         summary_method="reflection_with_llm", clear_history=False,
                         max_turns=240)

autogen.runtime_logging.stop()
