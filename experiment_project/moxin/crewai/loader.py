import json
from dora import Node, DoraStatus
import pyarrow as pa
from experiment_project.utils.files.read import read_yaml
crewai_agent_config = read_yaml('audio_summarize.yml')

class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            send_output("agent_config", pa.array([json.dumps(crewai_agent_config)]),dora_event['metadata'])
        return DoraStatus.STOP