import pyarrow as pa
import whisper
import time
from dora import DoraStatus




class Operator:
    """
    Transforming Speech to Text using OpenAI Whisper model
    """

    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            send_output("text", pa.array(['Hello 你好 ! ']), dora_event["metadata"])
        return DoraStatus.CONTINUE