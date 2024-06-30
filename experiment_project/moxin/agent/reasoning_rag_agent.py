#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

import agentops
from dora import Node, DoraStatus
import dspy
import pyarrow as pa

from experiment_project.agents.dspy.rag import ReasonerRagModule
from experiment_project.agents.dspy.self_refine import SelfRefineModule
from experiment_project.agents.dspy.base_signature import init_base_signature
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
                print(inputs)
                if inputs.get('proxy_url', None) is not None:
                    init_sys_env(proxy_url=inputs.get('proxy_url', None))

                turbo = dspy.OpenAI(model=inputs.get('model_name'), max_tokens=inputs.get('model_max_tokens'),
                                    api_key=inputs.get('model_api_key'))
                dspy.settings.configure(lm=turbo)


                refine_module = ReasonerRagModule(module_path=inputs.get('module_path',None),model_name=inputs.get('model_name',None),collection_name=inputs.get('model_name','my_docs'),
                                                  is_upload_file=inputs.get('is_upload_file',False),files_path=inputs.get('files_path',None),encoding=inputs.get('encoding','utf-8'),
                                                  chunk_size=inputs.get('chunk_size',256),multi_process=inputs.get('multi_process',False),rag_search_num=inputs.get('rag_search_num',5))
                task, result = inputs.get('task'), ''
                if task is not None:
                    result = refine_module.forward(question=task)
                    print('任务完成的结果是  ：' ,result)
                send_output("reasoner_result", pa.array([result]),dora_event['metadata'])  # add this line
        return DoraStatus.CONTINUE
