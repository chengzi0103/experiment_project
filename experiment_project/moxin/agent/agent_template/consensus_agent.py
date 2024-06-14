import json
import os
from dora import Node
import dspy
import pyarrow as pa
from experiment_project.utils.initial.util import init_sys_env

node = Node()

event = node.next()
if event["type"] == "INPUT":
    print(event['id'])
