import random
from typing import Union

import dspy

from experiment_project.agents.dspy.base_signature import init_consensus_signature


# from experiment_project.dspy.agent_signature import init_base_signature, init_multiple_inputs_signature, \
#     init_consensus_signature


class ReasonerModule(dspy.Module):
    def __init__(self,reasoning_signature: dspy.Signature,):
        super().__init__()

        self.prog = dspy.Predict(reasoning_signature)

    def forward(self, question):
        return self.prog(question=question)


class CoT(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.prog(question=question)


class ConsensusModule(dspy.Module):
    def __init__(self, consensus_signature:Union[ dspy.Signature,None]=None, temperature:float=0.7):
        super().__init__()
        if consensus_signature is None:
            self.consensus_signature = init_consensus_signature()
        self.predict = dspy.Predict(consensus_signature)
        self.temperature = temperature

    @property
    def no_cache(self):
        return dict(temperature=self.temperature + 0.0001 * random.uniform(-1, 1))

    def forward(self, question:str,contexts:list[str]):
        answer = self.predict(question=question,contexts=contexts,**self.no_cache).answer
        return answer



