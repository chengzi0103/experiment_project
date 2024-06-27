import random
from typing import Union

import dspy

from experiment_project.agents.dspy.base_signature import init_costar_signature


class SelfRefineModule(dspy.Module):
    def __init__(self, role:str=None,backstory:str=None,self_refine_signature: dspy.Signature=None, max_iterations:int=3, feedback_prompt:Union[str,None]=None, refinement_prompt:Union[str,None]=None, stop_condition_prompt:Union[str,None]=None, temperature:float=0.7):

        super().__init__()
        self.max_iterations = max_iterations
        self.temperature = temperature
        if feedback_prompt is None:
            # self.feedback_prompt = f'你是一个内容评估助手.根据问题和答案评估内容在完整性、准确性、相关性、清晰度和用户满意度方面的表现。 给出自己的建议 (建议要简单、明了、指明方向). 回答只包含建议就可以了 {feedback_backstory}'
            self.feedback_prompt = f'You are a content evaluation assistant. Evaluate the content based on completeness, accuracy, relevance, clarity, and user satisfaction. Provide your own suggestions (keep suggestions simple, clear, and directional). Only include the suggestions in your response. '
        else:
            self.feedback_prompt = feedback_prompt
            # self.evaluation = init_base_signature(role=feedback_prompt,backstory=evaluation_backstory)
        if refinement_prompt is None:
            # self.refinement_prompt = '你是一个内容改进助手. 结合建议,对内容进行改进'
            self.refinement_prompt = '"You are a content improvement assistant. Improve the content based on the suggestions."'
        else: self.refinement_prompt= refinement_prompt
        if stop_condition_prompt is None:
            # self.stop_condition_prompt = '你是一个任务检查判断助手. 根据问题和答案检查否达到任务预期的完整性、准确性、相关性、清晰度和用户满意度标准？'
            self.stop_condition_prompt = 'You are a task evaluation assistant. Based on the question and answer, check if the task meets the standards of completeness, accuracy, relevance, clarity, and user satisfaction.'
        else:
            self.stop_condition_prompt = stop_condition_prompt
        # self.predict = dspy.Predict(self_refine_signature)
        if role is not  None: self.predict = dspy.Predict(init_costar_signature(role=role,backstory=backstory))
        else:  self.predict = dspy.ChainOfThought("question -> answer")

    @property
    def no_cache(self):
        return dict(temperature=self.temperature + 0.0001 * random.uniform(-1, 1))

    def get_result(self,result_module):
        answer = ''
        if result_module.answer == '':
            answer = result_module.objective
        else:
            answer = result_module.answer
        return answer

    def replace_prefix(self,data:str):
        return data.replace('Question:','').replace('Answer: ','')
    def feedback(self,question:str,context:str):
        """
        对任务和内容进行反馈 通过prompt的定义查看任务结果是否需要优化
        """
        # predict_evaluation = dspy.Predict(init_multiple_inputs_signature(role=self.feedback_prompt,backstory='说明对内容的建议是什么?'),**self.no_cache)
        predict_evaluation = dspy.Predict(init_costar_signature(role=self.feedback_prompt,backstory='Explain what the suggestions for the content are.?',input_fields={'context':"The content that needs suggestions"}))
        evaluate = predict_evaluation(question=self.replace_prefix(question),context=self.replace_prefix(context),**self.no_cache)
        answer = self.get_result(evaluate)
        return answer
    def refinement(self,question:str,evaluate_data:str):
        """
        根据feedback之后的建议,来对运行任务
        """
        # predict_refinement = dspy.Predict(init_multiple_inputs_signature(role=self.refinement_prompt, backstory=evaluate_data),**self.no_cache)
        predict_refinement = dspy.Predict(init_costar_signature(role=self.refinement_prompt,input_fields={'context':"The content that needs suggestions"}))
        refinement = predict_refinement(question=f"Your suggestion is:  {self.replace_prefix(evaluate_data)}",context=f"The content that needs to be modified is:  {self.replace_prefix(question)}",example='',**self.no_cache)
        answer = self.get_result(refinement)
        return answer

    def stop_condition(self,question:str,context:str):
        """
        查看任务是否符合我们的期望和要求
        """
        predict_stop_condition = dspy.Predict(init_costar_signature(role=self.stop_condition_prompt,backstory='只回答 “是”或“否”。',input_fields={'context':"The content that needs suggestions"}))
        stop_condition = predict_stop_condition(question=self.replace_prefix(question),context=self.replace_prefix(context),example='是',**self.no_cache)
        answer = self.get_result(stop_condition)
        return answer
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

init_sys_env(proxy_url= 'http://192.168.31.215:10890')
secret_env_file = '/mnt/c/Users/chenzi/Desktop/project/env_secret_config.yaml'

api_configs = read_yaml(secret_env_file)

model_config = api_configs.get('openai')
turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=4096,api_key=model_config.get('api_key'))
dspy.settings.configure(lm=turbo)
# module_path = '/mnt/d/models/embeddings/bce-embedding-base_v1'

self_refine_module = SelfRefineModule(role='I want you to act as an IT Expert. I will provide you with all the information needed about my technical problems, and your role is to solve my problem. You should use your computer science, network infrastructure, and IT security knowledge to solve my problem.',backstory='Using intelligent, simple, and understandable language for people of all levels in your answers will be helpful. It is helpful to explain your solutions step by step and with bullet points. Try to avoid too many technical details, but use them when necessary.')
# result = refine_module.forward(question="Provide a detailed summary of the theme and explanation of the paper 'Text-Animator Controllable Visual Text Video Generation'. Additionally, explain which papers it cites, what achievements it has made, when it was written, and who the authors are.")
result = self_refine_module.forward(question="udp和tcp的区别")
print(result)
SelfRefineModule()