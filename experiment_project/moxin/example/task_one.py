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
            if dora_event['id'] == 'run_task_num':
                input = dora_event["value"][0].as_py()
                if '1' in input:
                    print(f'任务运行时间  {now_time()}','完成task-one的任务')
                    send_output('task_one_loop_num',pa.array(['task_one']),dora_event['metadata'])
                    return DoraStatus.CONTINUE

        return DoraStatus.STOP