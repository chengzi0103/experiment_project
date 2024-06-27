#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

import agentops
from dora import Node, DoraStatus
import dspy
import pyarrow as pa

from experiment_project.agents.utils.util import init_agentops
from experiment_project.utils.initial.util import init_sys_env, init_env
import time



class ReasoningModule(dspy.Module):
    def __init__(self,reasoning_signature: dspy.Signature):
        super().__init__()
        self.prog = dspy.Predict(reasoning_signature)

    def forward(self, question:str):
        return self.prog(question=question)
class Operator:
    def on_event(
            self,
            dora_event,
            send_output,
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            if dora_event['id'] == 'agent_config':
                inputs = dora_event["value"][0].as_py()
                inputs = json.loads(inputs)
                # if 'reasoning' in inputs.get('agent_list') or 'reasoner' in inputs.get('agent_list'):
                if inputs.get('proxy_url', None) is not None:
                    init_sys_env(proxy_url=inputs.get('proxy_url', None))
                if inputs.get('env', None) is not None: init_env(env=inputs['env'])

                turbo = dspy.OpenAI(model=inputs.get('model_name'), max_tokens=inputs.get('model_max_tokens'), api_key=inputs.get('model_api_key'),api_base=inputs.get('model_api_url',None))
                dspy.settings.configure(lm=turbo)

                class ReasoningSignature(dspy.Signature):
                    question = dspy.InputField()
                    answer = dspy.OutputField(desc='')
                    role = dspy.InputField(desc=inputs.get('role', ''))
                    backstory = dspy.InputField(desc=inputs.get('backstory', ''))

                reasoning = ReasoningModule(reasoning_signature=ReasoningSignature)
                task,result = inputs.get('task'),''
                if task is not None:
                    result = reasoning.forward(question=task).answer
                print('result is  ',result)
                agentops.end_session('Success Record Token ')
                send_output("reasoner_result", pa.array([result]),dora_event['metadata'])  # add this line
                return DoraStatus.STOP
        return DoraStatus.CONTINUE



