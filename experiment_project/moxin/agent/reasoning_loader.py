import json

from dora import Node, DoraStatus
import pyarrow as pa
from experiment_project.utils.files.read import read_yaml



class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:

        params = read_yaml('reasoning_config.yaml')
        model_config,agent_config,env_config = params['MODEL'],params['AGENT'],params['env']
        if dora_event["type"] == "INPUT":
            config = {}
            config.update(model_config)
            config.update(agent_config)
            config.update(env_config)
            config = {k.lower():v  for k,v in config.items() }
            send_output("agent_config", pa.array([json.dumps(config)]),dora_event['metadata'])
        return DoraStatus.STOP