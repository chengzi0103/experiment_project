#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from dora import Node
import dspy
import pyarrow as pa
from experiment_project.utils.initial.util import init_sys_env
import time
node = Node()



class ReasoningModule(dspy.Module):
    def __init__(self,reasoning_signature: dspy.Signature):
        super().__init__()
        self.prog = dspy.Predict(reasoning_signature)

    def forward(self, question):
        return self.prog(question=question)

event = node.next()
if event["type"] == "INPUT":
    inputs = event["value"][0].as_py()
    inputs = json.loads(inputs)
    if 'reasoning' in inputs.get('agent_list') or 'reasoner' in inputs.get('agent_list'):

        if inputs.get('proxy_url', None) is not None:

            init_sys_env(proxy_url=inputs.get('proxy_url', None))

        turbo = dspy.OpenAI(model=inputs.get('model_name'), max_tokens=inputs.get('model_max_tokens'), api_key=inputs.get('model_api_key'))
        dspy.settings.configure(lm=turbo)

        class ReasoningSignature(dspy.Signature):

            question = dspy.InputField()
            answer = dspy.OutputField(desc='')
            role = dspy.OutputField(desc=inputs.get('role', None))
            backstory = dspy.OutputField(desc=inputs.get('backstory', None))


        print(ReasoningSignature)
        reasoning = ReasoningModule(reasoning_signature=ReasoningSignature)
        task,result = inputs.get('task'),''
        if task is not None:
            result = reasoning.forward(question=task).answer
        time.sleep(2)
        result= 'reasoner_result'
        print(f'完成llm问题回答: {result}')
        node.send_output("reasoner_result", pa.array([result]))  # add this line




