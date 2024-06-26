from typing import Any, Union
import dspy
from typing import Union

from experiment_project.utils.variable.util import get_variable_name


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






def init_costar_signature(role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None, input_fields: list[str] = None,objective:str=None,specifics:str=None,actions:str=None,results:str=None,example:str=None,answer:str=None):
    """
    backstory（上下文）: 提供任务的背景信息。
    Objective（目标）: 明确任务的主要目标。
    Specifics（细节）: 列出任务的具体要求。
    Tasks（任务）: 描述需要完成的任务。
    Actions（行动）: 列出需要执行的具体步骤。
    Results（结果）: 描述预期的结果或成果
    example（案例）: 任务的案例
    """
    inputs = {}

    for input_field in [role,backstory,objective,specifics,actions,results,example,answer]:
        if input_field is None:
            input_field = ''
        inputs[get_variable_name(input_field, locals())[0]] = input_field

    # 定义CO-STAR字段
    fields = {
        'question': dspy.InputField(desc="The question we're trying to answer."),
        'objective': dspy.OutputField(desc=inputs.get('objective', '')),
        'specifics': dspy.OutputField(desc=inputs.get('specifics', '')),
        'actions': dspy.OutputField(desc=inputs.get('actions','')),
        'results': dspy.OutputField(desc=inputs.get('results','')),
        'example': dspy.OutputField(desc=inputs.get('example','')),
        'answer': dspy.OutputField(desc=inputs.get('answer','')),
        'role': dspy.OutputField(desc=inputs.get('role','')),
        'backstory': dspy.OutputField(desc=inputs.get('backstory',''))
    }

    # 动态添加额外字段
    if input_fields:
        for field_name in input_fields:
            fields[field_name] = dspy.InputField()

    if output_fields:
        for field_name, field_desc in output_fields.items():
            fields[field_name] = dspy.OutputField(desc=field_desc)
    # all_fields = {}
    # for field_name, field_desc in fields.items():
    #
    #     if field_desc.json_schema_extra.get('__dspy_field_type') == 'output':
    #
    #         if field_desc.json_schema_extra.get('desc') != '':
    #             all_fields[field_name] = field_desc
    #         if field_name in ['answer', 'role', 'backstory']:
    #             all_fields[field_name] = field_desc
    #
    #     if field_desc.json_schema_extra.get('__dspy_field_type') == 'input':
    #         all_fields[field_name] = field_desc
    # 动态创建新的Signature类
    COStarSignature = type('COStarSignature', (dspy.Signature,), fields)

    return COStarSignature


def init_costar_signature_input(role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None, input_fields: list[str] = None,objective:str=None,specifics:str=None,actions:str=None,results:str=None,example:str=None,answer:str=None):
    """
    backstory（上下文）: 提供任务的背景信息。
    Objective（目标）: 明确任务的主要目标。
    Specifics（细节）: 列出任务的具体要求。
    Tasks（任务）: 描述需要完成的任务。
    Actions（行动）: 列出需要执行的具体步骤。
    Results（结果）: 描述预期的结果或成果
    example（案例）: 任务的案例
    """
    inputs = {}

    for input_field in [role,backstory,objective,specifics,actions,results,example,answer]:
        if input_field is None:
            input_field = ''
        inputs[get_variable_name(input_field, locals())[0]] = input_field

    # 定义CO-STAR字段
    fields = {
        'question': dspy.InputField(desc="The question we're trying to answer."),
        'objective': dspy.InputField(desc=inputs.get('objective', 'Provides the background information for the task.')),
        'specifics': dspy.InputField(desc=inputs.get('specifics', 'Lists specific requirements for the task.')),
        'actions': dspy.InputField(desc=inputs.get('actions','Enumerates the specific steps that need to be executed.')),
        'results': dspy.InputField(desc=inputs.get('results','Task result output type')),
        'example': dspy.InputField(desc=inputs.get('example','Provides an example related to the task.')),
        'answer': dspy.OutputField(desc=inputs.get('answer','')),
        'role': dspy.InputField(desc=inputs.get('role','Specifies the role or purpose of the module.')),
        'backstory': dspy.InputField(desc=inputs.get('backstory','Provides the background information for the task.'))
    }

    # 动态添加额外字段
    if input_fields:
        for field_name in input_fields:
            fields[field_name] = dspy.InputField()

    if output_fields:
        for field_name, field_desc in output_fields.items():
            fields[field_name] = dspy.OutputField(desc=field_desc)
    all_fields = {}
    for field_name, field_desc in fields.items():

        if field_desc.json_schema_extra.get('__dspy_field_type') == 'output':
            all_fields[field_name] = field_desc

        if field_desc.json_schema_extra.get('__dspy_field_type') == 'input':
            if field_desc.json_schema_extra.get('desc') != '':
                all_fields[field_name] = field_desc
            if field_name in ['answer', 'role', 'backstory']:
                all_fields[field_name] = field_desc
            all_fields[field_name] = field_desc
    # 动态创建新的Signature类
    COStarSignature = type('COStarSignature', (dspy.Signature,), fields)

    return COStarSignature




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
