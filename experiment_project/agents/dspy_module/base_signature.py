from typing import Any, Union

import dspy

import dspy
from typing import Union

def init_custom_signature(role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None,input_fields:list[str]=None):
    inputs = {'role': role, 'backstory': backstory}

    # 定义基本字段
    fields = {
        'question': dspy.InputField(),
        # 'context': dspy.InputField(),
        'answer': dspy.OutputField(desc=''),
        'role': dspy.OutputField(desc=inputs.get('role', 'Please optimize and combine the following responses provided by multiple agents into a single coherent, comprehensive, and accurate final answer. Ensure that the combined response includes all key information, eliminates redundancy, maintains logical consistency, and presents the final result in a clear and concise manner.')),
        'backstory': dspy.OutputField(desc=inputs.get('backstory'))
    }
    if input_fields:
        for field_name in input_fields:
            fields[field_name] = dspy.InputField()
    # 动态添加额外字段
    if output_fields:
        for field_name, field_desc in output_fields.items():
            fields[field_name] = dspy.OutputField(desc=field_desc)

    # 动态创建新的Signature类
    CustomSignature = type('CustomSignature', (dspy.Signature,), fields)

    return CustomSignature

# 示例用法










def init_base_signature(role:Union[str,None]=None,backstory:Union[str,None]=None):
    inputs = {'role':role,'backstory':backstory}
    class BaseSignature(dspy.Signature):

        question = dspy.InputField()
        answer = dspy.OutputField(desc='')
        role = dspy.OutputField(desc=inputs.get('role'))
        backstory = dspy.OutputField(desc=inputs.get('backstory'))
    return BaseSignature


def init_multiple_inputs_signature(role:Union[str,None]=None,backstory:Union[str,None]=None):
    inputs = {'role': role, 'backstory': backstory}

    class MultipleInputSignature(dspy.Signature):
        question = dspy.InputField()
        context = dspy.InputField()
        answer = dspy.OutputField(desc='')
        role = dspy.OutputField(desc=inputs.get('role'))
        backstory = dspy.OutputField(desc=inputs.get('backstory'))

    return MultipleInputSignature


def init_consensus_signature(role:Union[str,None]=None,backstory:Union[str,None]=None):
    inputs = {'role': role, 'backstory': backstory}
    class ConsensusSignature(dspy.Signature):
        question = dspy.InputField()
        context = dspy.InputField()
        answer = dspy.OutputField(desc='')
        role = dspy.OutputField(desc=inputs.get('role','Please optimize and combine the following responses provided by multiple agents into a single coherent, comprehensive, and accurate final answer . Ensure that the combined response includes all key information, eliminates redundancy, maintains logical consistency, and presents the final result in a clear and concise manner.'))
        backstory = dspy.OutputField(desc=inputs.get('backstory'))
    return ConsensusSignature


# def init_custom_signature(role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None, input_fields:list[str]=None):
#     inputs = {'role': role, 'backstory': backstory}
#
#     # 定义基本字段
#     fields = {
#         'question': dspy.InputField(),
#         # 'context': dspy.InputField(),
#         'answer': dspy.OutputField(desc=''),
#         'role': dspy.OutputField(desc=inputs.get('role', 'Please optimize and combine the following responses provided by multiple agents into a single coherent, comprehensive, and accurate final answer. Ensure that the combined response includes all key information, eliminates redundancy, maintains logical consistency, and presents the final result in a clear and concise manner.')),
#         'backstory': dspy.OutputField(desc=inputs.get('backstory'))
#     }
#     if input_fields :
#         for field_name in input_fields:
#             fields[field_name] = dspy.InputField()
#     # 动态添加额外字段
#     if output_fields:
#         for field_name, field_desc in output_fields.items():
#             fields[field_name] = dspy.OutputField(desc=field_desc)
#
#     # 动态创建新的Signature类
#     CustomSignature = type('CustomSignature', (dspy.Signature,), fields)
#
#     return CustomSignature
