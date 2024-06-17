#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from dora import Node
import dspy
import pyarrow as pa

from experiment_project.dspy_module.agent_module import SelfRefineModule
from experiment_project.dspy_module.agent_signature import init_base_signature
from experiment_project.utils.initial.util import init_sys_env

node = Node()

event = node.next()
if event["type"] == "INPUT":
    inputs = event["value"][0].as_py()
    inputs = json.loads(inputs)
    if inputs.get('proxy_url', None) is not None:
        init_sys_env(proxy_url=inputs.get('proxy_url', None))

    turbo = dspy.OpenAI(model=inputs.get('model_name'), max_tokens=inputs.get('model_max_tokens'),
                        api_key=inputs.get('model_api_key'))
    dspy.settings.configure(lm=turbo)
    base_signature = init_base_signature(role=inputs.get('role', None),backstory=inputs.get('backstory', None))
    refine_module = SelfRefineModule(self_refine_signature=base_signature)
    task, result = inputs.get('task'), ''
    if task is not None:
        result = refine_module.forward(question=task)
    print(f'完成llm问题回答: {result}')
    node.send_output("result", pa.array([result]))  # add this line