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

        params = read_yaml('reasoner_rag_config.yml')
        model_config,env_config,rag_config = params['MODEL'],params['ENV'],params['AGENT']['RAG']
        if dora_event["type"] == "INPUT":
            config = {}
            config.update(model_config)
            config.update(rag_config)
            config.update(env_config)
            config = {k.lower():v  for k,v in config.items() }
            config['task'] = params['AGENT']['TASK']
            send_output("agent_config", pa.array([json.dumps(config)]),dora_event['metadata'])
        return DoraStatus.STOP