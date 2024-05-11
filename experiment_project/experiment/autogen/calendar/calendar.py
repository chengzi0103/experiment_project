import autogen
from autogen import AssistantAgent, GroupChat, GroupChatManager

from experiment_project.utils.agent.util import load_log_token,create_sqlite_db_name, load_api_config
from autogen import register_function
import random
from experiment_project.utils.files.read import read_yaml

secret_env_file = '/mnt/d/project/dy/extra/autogen/env_secret_config.yaml'
log_db_name = create_sqlite_db_name()

api_configs = read_yaml(secret_env_file)
calendar_enenvt_agent = AssistantAgent(name="calendar_enenvt_agent",system_message='该Agent作为日历系统的核心组件，负责维护和管理用户的日历事件。它不仅处理日常的日程管理任务，如查看、创建、编辑、删除和完成事件，还提供API接口供其他Agent调用，以查询日历信息或进行事件操作。',
                                       llm_config=api_configs.get('zhipu'))
