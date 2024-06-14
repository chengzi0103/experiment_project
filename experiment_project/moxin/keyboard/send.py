
import json

from dora import Node
import pyarrow as pa
from experiment_project.utils.files.read import read_yaml
node = Node()

event = node.next()
if event["type"] == "INPUT":
    node.send_output("recording", pa.array(['你好']),event['metadata'])
