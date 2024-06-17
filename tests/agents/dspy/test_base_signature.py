from typing import Union

import dspy

from experiment_project.agents.dspy_module.base_signature import init_custom_signature
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
    if input_fields is not None:
        for field_name in input_fields:
            fields[field_name] = dspy.InputField()
    # 动态添加额外字段
    if output_fields is not None:
        for field_name, field_desc in output_fields.items():
            fields[field_name] = dspy.OutputField(desc=field_desc)

    # 动态创建新的Signature类
    CustomSignature = type('CustomSignature', (dspy.Signature,), fields)

    return CustomSignature
class TestConsensusSignatureClass(dspy.Signature):
    question = dspy.InputField()
    context = dspy.InputField()
    answer = dspy.OutputField(desc='')
    role = dspy.OutputField(desc='Agent Role')
    backstory = dspy.OutputField(desc='Agent Backstory')
    additional_info = dspy.OutputField(desc='This field is for additional information.')
    summary = dspy.OutputField(desc='This field will contain a summary of the responses.')
def test_init_custom_signature():
    output_fields = {
        'additional_info': 'This field is for additional information.',
        'summary': 'This field will contain a summary of the responses.'
    }
    input_fields = ['context']
    CustomSignatureClass = init_custom_signature(input_fields=input_fields,role='Agent Role', backstory='Agent Backstory', output_fields=output_fields,)

# assert ConsensusSignatureClass.additional_info == TestConsensusSignatureClass.__dict__

