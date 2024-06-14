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


def init_consensus_signature(role:Union[str,None]=None,backstory:Union[str,None]=None):
    inputs = {'role': role, 'backstory': backstory}
    class ConsensusSignature(dspy.Signature):
        question = dspy.InputField()
        context = dspy.InputField()
        answer = dspy.OutputField(desc='')
        role = dspy.OutputField(desc=inputs.get('role','Please optimize and combine the following responses provided by multiple agents into a single coherent, comprehensive, and accurate final answer . Ensure that the combined response includes all key information, eliminates redundancy, maintains logical consistency, and presents the final result in a clear and concise manner.'))
        backstory = dspy.OutputField(desc=inputs.get('backstory'))
    return ConsensusSignature