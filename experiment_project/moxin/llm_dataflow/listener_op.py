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
            print(dora_event["value"].to_pylist())
        return DoraStatus.CONTINUE