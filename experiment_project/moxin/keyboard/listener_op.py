import numpy as np
import pyarrow as pa
from dora import DoraStatus
class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            if dora_event["id"] == 'buffer':
                value = dora_event["value"][0].as_py()
                print(value, flush=True)
            if dora_event["id"] == 'submitted':
                print(dora_event["value"][0].as_py(),flush=True)
            if dora_event["id"] == 'record':
                print(dora_event["value"][0].as_py(),flush=True)
            if dora_event["id"] == 'ask':
                print(dora_event["value"][0].as_py(),flush=True)
            if dora_event["id"] == 'send':
                print(dora_event["value"][0].as_py(),flush=True)
            if dora_event["id"] == 'change':
                print(dora_event["value"][0].as_py(),flush=True)
        return DoraStatus.CONTINUE