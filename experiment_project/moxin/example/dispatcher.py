import json

from dora import Node, DoraStatus
import pyarrow as pa


class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            if dora_event["id"] == "task_one_loop_num":
                print('task-one 任务结束,开始触发task-two任务')
                send_output('run_task_num', pa.array([json.dumps('2')]), dora_event['metadata'])
                return DoraStatus.CONTINUE
            if dora_event["id"] == "task_two_loop_num":
                print('task-two任务结束')
                return DoraStatus.STOP
            if dora_event["id"] == "direction":
                print('开始发送任务')
                send_output('run_task_num',pa.array([json.dumps('1')]),dora_event['metadata'])
                return DoraStatus.CONTINUE
        return DoraStatus.CONTINUE