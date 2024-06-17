from dora import Node, DoraStatus
import pyarrow as pa
from experiment_project.utils.date.util import now_time


class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            if dora_event['id'] == 'agent_result':
                input = dora_event["value"][0].as_py()
                print(f'Crewai Agent Result: {input}')

        return DoraStatus.CONTINUE