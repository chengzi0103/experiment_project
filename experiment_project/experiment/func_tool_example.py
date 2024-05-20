import autogen
from autogen import AssistantAgent,UserProxyAgent, GroupChat, GroupChatManager

from experiment_project.experiment.calendar_project.tools.data import create_user_event
from experiment_project.utils.agent.util import create_sqlite_db_name, load_log_token
from experiment_project.utils.database.sqlite.util import Database as SqliteDataBase, create_connection, execute_sql, \
    check_and_create_table, insert, select, update, delete, insert_json_data
from experiment_project.utils.files.read import read_yaml

log_db_name = create_sqlite_db_name()
logging_session_id = autogen.runtime_logging.start(config={"dbname": log_db_name})

secret_env_file = '/mnt/d/project/dy/extra/autogen/env_secret_config.yaml'
api_configs = read_yaml(secret_env_file)
assistant = AssistantAgent(
    name='assistant',
    llm_config=api_configs.get('openai'),
    is_termination_msg=lambda x: x.get("content", "") and "terminate" in x.get("content", "").lower(),
    system_message="""你是一个Ai助手,协助人类解决问题""",
)

user_proxy = UserProxyAgent(
    name='user_proxy',
    # human_input_mode='ALWAYS',
    human_input_mode='NEVER',
    is_termination_msg=lambda x: x.get("content", "") and "terminate" in x.get("content", "").lower(),
    code_execution_config={
        "work_dir": "/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/autogen_project/example/output",
        "use_docker": False
    },
    # llm_config=api_configs.get('kimi')
    # system_message="""你是一个运行代码的人员""",
)
assistant.register_for_llm(name='create_user_event',description="Generate a person's calendar data for n days according to the given number")(create_user_event)
user_proxy.register_for_execution(name='create_user_event',)(create_user_event)

assistant.register_for_llm(name='sqlite_create_connection', description="This function attempts to connect to a SQLite database at the specified path. If the connection is successful, it returns the connection object; otherwise, it prints the error and returns None.")(create_connection)
user_proxy.register_for_execution(name='sqlite_create_connection',)(create_connection)

assistant.register_for_llm(name='sqlite_execute_sql', description="This function establishes a connection to the database, creates a cursor, and executes the provided SQL command. If params is provided, it binds these parameters to the SQL command. After execution, it commits the transaction and returns the cursor object. It ensures the database connection is closed before exiting.")(execute_sql)
user_proxy.register_for_execution(name='sqlite_execute_sql',)(execute_sql)

assistant.register_for_llm(name='sqlite_check_and_create_table', description="This function checks if a table with the specified name exists in the database. If the table does not exist, it executes the provided SQL command to create the table. It prints messages indicating whether the table was found or created.")(check_and_create_table)
user_proxy.register_for_execution(name='sqlite_check_and_create_table',)(check_and_create_table)

assistant.register_for_llm(name='sqlite_insert', description="This function processes the provided keyword arguments, converting lists to comma-separated strings if necessary. It then constructs and executes an INSERT SQL command to insert the data into the specified table.")(insert)
user_proxy.register_for_execution(name='sqlite_insert',)(insert)

assistant.register_for_llm(name='sqlite_select', description="This function executes the provided SELECT SQL command and returns all fetched rows as a list of tuples. If the cursor is None (indicating an error), it returns an empty list.")(select)
user_proxy.register_for_execution(name='sqlite_select',)(select)


assistant.register_for_llm(name='sqlite_insert_json_data', description="Iterates over the list of dictionaries, calling the insert function for each one to insert the records into the specified table.")(insert_json_data)
user_proxy.register_for_execution(name='sqlite_insert_json_data',)(insert_json_data)
task_list = [
            "1, 生成一个人的15天的日历数据"
            "2, 你需要先创建一个数据库(如果这个数据库不存在)"
            "3, 生成一个表名,查看表是否存在,如果不存在,则获取日历数据所有的列,作为表的列,生成一个创建表的sql语句,然后创建表."
            "4, 表创建过后可以将刚才的日历数据入库"
            "5, 从数据库中查询2024年5月15日到2024年5月17日所有的数据"
            "6, 查询数据完成后 结束任务"
            "db_file = /mnt/d/project/zzbc/experiment_project/experiment_project/experiment/output/func_tool.db"
            "table_name = user_calendar"
    ]
all_task = [{'recipient':assistant,"message":task,"clear_history":False,"summary_method": "reflection_with_llm"} for task in task_list ]


result = user_proxy.initiate_chats(
all_task
)
#
# autogen.runtime_logging.stop()
