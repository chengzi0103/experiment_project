import json

from dora import Node
import pyarrow as pa
from experiment_project.utils.files.read import read_yaml
node = Node()
custom_agent_config = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/moxin/agent/custom_agent_config.yml')
agent_task,agent_config,agent_list = custom_agent_config.get('CUSTOM-AGENT').get('TASK'),custom_agent_config.get('MODEL'),custom_agent_config.get('CUSTOM-AGENT').get('AGENT_LIST')

event = node.next()
if event["type"] == "INPUT":
    config = {}
    config.update(agent_config)
    config.update(agent_task)
    config = {k.lower():v  for k,v in config.items() }
    node.send_output("agent_config", pa.array([json.dumps(config)]),event['metadata'])
