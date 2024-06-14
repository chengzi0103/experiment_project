# from experiment_project.utils.files.read import read_yaml
# import json
#
# from dora import Node
# import pyarrow as pa
# from experiment_project.utils.files.read import read_yaml
# node = Node()
# custom_agent_config = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/moxin/agent/custom_agent_config.yml')
# agent_task,agent_config,agent_list = custom_agent_config.get('CUSTOM-AGENT').get('TASK'),custom_agent_config.get('MODEL'),custom_agent_config.get('CUSTOM-AGENT').get('AGENT_LIST')
#
# event = node.next()
# if event["type"] == "INPUT":
#     if event["id"] == 'direction':
#         config = {}
#         config.update(agent_config)
#         config.update(agent_task)
#         config['agent_list'] = agent_list
#         config = {k.lower():v  for k,v in config.items() }
#         node.send_output("agent_config", pa.array([json.dumps(config)]),event['metadata'])
#     elif event["id"] == 'listener' :
#         print(f'Event id is {event["id"]}')
#
from experiment_project.utils.files.read import read_yaml
import json

from dora import Node, DoraStatus
import pyarrow as pa
from experiment_project.utils.files.read import read_yaml
custom_agent_config = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/moxin/agent/custom_agent_config.yml')
agent_task,agent_config,agent_list = custom_agent_config.get('CUSTOM-AGENT').get('TASK'),custom_agent_config.get('MODEL'),custom_agent_config.get('CUSTOM-AGENT').get('AGENT_LIST')

class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            print(dora_event["id"])
            # if dora_event["id"] == '':
            config = {}
            config.update(agent_config)
            config.update(agent_task)
            config['agent_list'] = agent_list
            config = {k.lower():v  for k,v in config.items() }
            print(f'开始发送config  {config}')
            send_output("agent_config", pa.array([json.dumps(config)]),dora_event['metadata'])


        # return DoraStatus.CONTINUE

