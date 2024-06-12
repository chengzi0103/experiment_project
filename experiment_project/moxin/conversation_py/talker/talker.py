#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from dora import Node
import pyarrow as pa
node = Node()
parameter = os.getenv('PARAMETER', 'default value')

event = node.next()
if event["type"] == "INPUT":
    print(
        f"""Node received:
    id: {event["id"]},
    value: {event["value"]},
    metadata: {event["metadata"]}"""
    )
    # node.send_output("speech", pa.array(["Hello World"]))  # add this line
    node.send_output("speech", pa.array([f"Hello {parameter}"]))

