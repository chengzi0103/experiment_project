from typing import Any, Union

import dspy


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