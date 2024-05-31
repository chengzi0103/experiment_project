from pprint import pprint
from paddlenlp import Taskflow
import os
os.environ['LD_LIBRARY_PATH'] ='/usr/local/lib'
schema = [
    "Total GBP",
    "No.",
    "Date",
    "Customer No.",
    "Subtotal without VAT",
    {
        "Description": [
            "Quantity",
            "Amount"
        ]
    }
]
ie = Taskflow('information_extraction', schema=schema,model='uie-x-base')
pprint(ie("2月8日上午北京冬奥会自由式滑雪女子大跳台决赛中中国选手谷爱凌以188.25分获得金牌！")) # Better print results using pprint
