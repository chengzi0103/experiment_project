#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from dora import Node
import dspy
import pyarrow as pa
from experiment_project.utils.initial.util import init_sys_env

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
    if inputs.get('proxy_url', None) is not None:

        init_sys_env(proxy_url=inputs.get('proxy_url', None))

    turbo = dspy.OpenAI(model=inputs.get('model_name'), max_tokens=inputs.get('model_max_tokens'), api_key=inputs.get('model_api_key'))
    dspy.settings.configure(lm=turbo)

    class ReasoningSignature(dspy.Signature):
        """
        根据问题回答
        """
        question = dspy.InputField()
        answer = dspy.OutputField(desc='', prefix=inputs.get('prefix',''))
        role = dspy.OutputField(desc=inputs.get('ROLE', ''))
        backstory = dspy.OutputField(desc=inputs.get('BACKSTORY', ''))


    print('完成dspy的配置初始化')
    reasoning = ReasoningModule(reasoning_signature=ReasoningSignature)
    task = inputs.get('task')
    result = ''
    if task is not None:
        result = reasoning.forward(question=task).answer
    node.send_output("result", pa.array([result]))  # add this line