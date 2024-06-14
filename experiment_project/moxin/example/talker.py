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
            send_output('run',pa.array(['Run Task']),dora_event['metadata'])
        return DoraStatus.CONTINUE