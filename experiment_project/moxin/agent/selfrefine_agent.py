#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

import agentops
from dora import Node, DoraStatus
import dspy
import pyarrow as pa

from experiment_project.agents.dspy_module.base_module import SelfRefineModule
from experiment_project.agents.dspy_module.base_signature import init_base_signature
from experiment_project.agents.utils.util import init_agentops

from experiment_project.utils.initial.util import init_sys_env

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
                # if 'selfrefine' in inputs.get('agent_list') or 'self_refine' in inputs.get('agent_list'):

                if inputs.get('proxy_url', None) is not None:
                    init_sys_env(proxy_url=inputs.get('proxy_url', None))

                turbo = dspy.OpenAI(model=inputs.get('model_name'), max_tokens=inputs.get('model_max_tokens'),
                                    api_key=inputs.get('model_api_key'))
                dspy.settings.configure(lm=turbo)
                init_agentops(inputs['agentops_api_key'])
                agentops.start_session()
                base_signature = init_base_signature(role=inputs.get('role', None),backstory=inputs.get('backstory', None))
                refine_module = SelfRefineModule(self_refine_signature=base_signature)
                task, result = inputs.get('task'), ''
                if task is not None:
                    result = refine_module.forward(question=task)
                agentops.end_session('Success Record Token ')
                send_output("selfrefine_result", pa.array([result]),dora_event['metadata'])  # add this line