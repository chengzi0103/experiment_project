import json

from dora import Node
import pyarrow as pa
from experiment_project.utils.files.read import read_yaml
x = input('请输入你的内容:   ')
node = Node()

params = read_yaml('selfrefine_config.yml')
model_config,agent_config = params['MODEL'],params['AGENT']

event = node.next()
if event["type"] == "INPUT":
    config = {}
    config.update(model_config)
    config.update(agent_config)
    config = {k.lower():v  for k,v in config.items() }
    node.send_output("agent_config", pa.array([json.dumps(config)]),event['metadata'])
