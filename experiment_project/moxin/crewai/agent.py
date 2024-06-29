import json

from dora import Node, DoraStatus
import pyarrow as pa

from experiment_project.agents.crewai.run_task import run_crewai
from experiment_project.utils.files.read import read_yaml
crewai_agent_config = read_yaml('rag_config.yml')

class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            if dora_event["id"] == "agent_config":
                inputs = dora_event["value"][0].as_py()
                agent_config = json.loads(inputs)
                result = run_crewai(crewai_config=agent_config)
                # result = '任务结束'
                send_output("agent_result", pa.array([result]),dora_event['metadata'])
        return DoraStatus.STOP