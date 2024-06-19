from dora import DoraStatus


class Operator:
    def on_event(
        self,
        dora_event,
        send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            if dora_event['id'] == 'reasoner_result':
                input = dora_event["value"][0].as_py()
                print(f'reasoner_result: {input}')
                return DoraStatus.STOP
        return DoraStatus.CONTINUE