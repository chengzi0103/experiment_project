

from dora import Node, DoraStatus
import pyarrow as pa

from experiment_project.utils.date.util import now_time


class Operator:
    def on_event( self,
        dora_event,
        send_output,)->DoraStatus:

        if dora_event["type"] == "INPUT":
            print('当前刷新时间: ',now_time())
            if dora_event["id"] == 'reasoner_result':
                print(f'这是 reasoner_result的result : {dora_event["value"].to_pylist()}')
            elif dora_event["id"] == 'selfrefine_result':
                print(f'这是 selfrefine_result的result  {dora_event["value"].to_pylist()}')

        send_output('output_result',pa.array(['This is Output Loader ']),dora_event['metadata'])
        return DoraStatus.CONTINUE
