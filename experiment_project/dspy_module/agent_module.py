import random
from typing import Union

import dspy

from experiment_project.dspy_module.agent_signature import init_base_signature, init_multiple_inputs_signature


class ReasoningModule(dspy.Module):
    def __init__(self,reasoning_signature: dspy.Signature):
        super().__init__()
        self.prog = dspy.Predict(reasoning_signature)

    def forward(self, question):
        return self.prog(question=question)


class SelfRefineModule(dspy.Module):
    def __init__(self, self_refine_signature: dspy.Signature, max_iterations:int=3, feedback_prompt:Union[str,None]=None, refinement_prompt:Union[str,None]=None, stop_condition_prompt:Union[str,None]=None, temperature:float=0.7):

        super().__init__()
        self.max_iterations = max_iterations
        self.temperature = temperature
        if feedback_prompt is None:
            feedback_backstory = """ """
            self.feedback_prompt = f'你是一个内容评估助手.根据问题和答案评估内容在完整性、准确性、相关性、清晰度和用户满意度方面的表现。 给出自己的建议 (建议要简单、明了、指明方向). 回答只包含建议就可以了 {feedback_backstory}'
        else:
            self.feedback_prompt = feedback_prompt
            # self.evaluation = init_base_signature(role=feedback_prompt,backstory=evaluation_backstory)
        if refinement_prompt is None:
            self.refinement_prompt = '你是一个内容改进助手. 结合建议,对内容进行改进'
        else: self.refinement_prompt= refinement_prompt
        if stop_condition_prompt is None:
            self.stop_condition_prompt = '你是一个任务检查判断助手. 根据问题和答案检查否达到任务预期的完整性、准确性、相关性、清晰度和用户满意度标准？'
        else:
            self.stop_condition_prompt = stop_condition_prompt
        self.predict = dspy.Predict(self_refine_signature)

    @property
    def no_cache(self):
        return dict(temperature=self.temperature + 0.0001 * random.uniform(-1, 1))

    def replace_prefix(self,data:str):
        return data.replace('Question:','').replace('Answer:','')
    def feedback(self,question:str,context:str):
        """
        对任务和内容进行反馈 通过prompt的定义查看任务结果是否需要优化
        """
        predict_evaluation = dspy.Predict(init_multiple_inputs_signature(role=self.feedback_prompt,backstory='说明对内容的建议是什么?'),**self.no_cache)
        evaluate = predict_evaluation(question=self.replace_prefix(question),context=self.replace_prefix(context)).backstory
        return evaluate
    def refinement(self,question:str,evaluate_data:str):
        """
        根据feedback之后的建议,来对运行任务
        """
        predict_refinement = dspy.Predict(init_multiple_inputs_signature(role=self.refinement_prompt, backstory=evaluate_data),**self.no_cache)
        refinement = predict_refinement(question=self.replace_prefix(question),context=self.replace_prefix(evaluate_data)).answer
        return refinement

    def stop_condition(self,question:str,context:str):
        """
        查看任务是否符合我们的期望和要求
        """
        predict_stop_condition = dspy.Predict(init_base_signature(role=self.stop_condition_prompt,backstory='只回答 “是”或“否”。'),**self.no_cache)
        stop_condition = predict_stop_condition(question=self.replace_prefix(question),context=self.replace_prefix(context)).backstory
        return stop_condition
    def forward(self, question:str):
        answer = self.predict(question=question,**self.no_cache).answer
        for num in range(0,self.max_iterations):
            feedback_answer = self.feedback(question=question,context=answer)
            print(f'在第{num}次迭代后 , evaluate_answer :   {feedback_answer}')
            refinement_answer = self.refinement(question=answer,evaluate_data=feedback_answer)
            print(f'在第{num}次迭代后 , refinement_answer :   {refinement_answer}')
            stop_condition_status = self.stop_condition(question=question,context=refinement_answer)
            if '是' in stop_condition_status:
                return refinement_answer
            else:
                answer = refinement_answer
        return answer

from experiment_project.utils.initial.util import init_sys_env
from experiment_project.utils.files.read import read_yaml
import dspy

init_sys_env()
secret_env_file = '/mnt/d/project/zzbc/env_secret_config.yaml'

api_configs = read_yaml(secret_env_file)

model_config = api_configs.get('openai')
turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=2048,api_key=model_config.get('api_key'))
dspy.settings.configure(lm=turbo)

base_signature = init_base_signature(role='我希望你担任影评人。您将撰写一篇引人入胜且富有创意的电影评论。你可以涵盖情节、主题和基调、表演和角色、导演、配乐、摄影、制作设计、特效、编辑、节奏、对话等主题。但最重要的方面是强调这部电影给你带来的感受。什么真正引起了你的共鸣。您也可以批评这部电影。')
refine_module = SelfRefineModule(self_refine_signature=base_signature)
result = refine_module.forward(question='openai中的temperature设置多少合适? 我需要在写作助手设置它')

