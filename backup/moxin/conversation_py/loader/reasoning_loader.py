import os
from dora import Node
import dspy
import pyarrow as pa
from experiment_project.utils.files.read import read_yaml
from experiment_project.utils.initial.util import init_sys_env
node = Node()
params = read_yaml('reasoning.yaml')
model_config,agent_config = params['MODEL'],params['AGENT']
event = node.next()
if event["type"] == "INPUT":
    node.send_output("proxy_url", pa.array([agent_config.get('PROXY_URL',None)]))
    node.send_output("prefix", pa.array([agent_config.get('PREFIX',None)]))
    node.send_output("role", pa.array([agent_config.get('ROLE',None)]))
    node.send_output("backstory", pa.array([agent_config.get('BACKSTORY',None)]))
    node.send_output("task", pa.array([agent_config.get('BACKSTORY',None)]))
    node.send_output("model_api_key", pa.array([model_config.get('MODEL_API_KEY')]))
    node.send_output("model_name", pa.array([model_config.get('MODEL_NAME')]))
    node.send_output("model_max_tokens", pa.array([model_config.get('MODEL_MAX_TOKENS')]))

