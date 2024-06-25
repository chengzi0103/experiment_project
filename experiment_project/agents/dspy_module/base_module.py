import random
from typing import Union, List

import dspy

from experiment_project.agents.dspy_module.base_signature import init_multiple_inputs_signature, init_base_signature, \
    init_consensus_signature, init_costar_signature


# from experiment_project.dspy_module.agent_signature import init_base_signature, init_multiple_inputs_signature, \
#     init_consensus_signature


class ReasonerModule(dspy.Module):
    def __init__(self,reasoning_signature: dspy.Signature,):
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
            # self.feedback_prompt = f'你是一个内容评估助手.根据问题和答案评估内容在完整性、准确性、相关性、清晰度和用户满意度方面的表现。 给出自己的建议 (建议要简单、明了、指明方向). 回答只包含建议就可以了 {feedback_backstory}'
            self.feedback_prompt = f'You are a content evaluation assistant. Evaluate the content based on completeness, accuracy, relevance, clarity, and user satisfaction. Provide your own suggestions (keep suggestions simple, clear, and directional). Only include the suggestions in your response. {feedback_backstory}'
        else:
            self.feedback_prompt = feedback_prompt
            # self.evaluation = init_base_signature(role=feedback_prompt,backstory=evaluation_backstory)
        if refinement_prompt is None:
            # self.refinement_prompt = '你是一个内容改进助手. 结合建议,对内容进行改进'
            self.refinement_prompt = 'You are a content improvement assistant. Combine suggestions to improve the content.'
        else: self.refinement_prompt= refinement_prompt
        if stop_condition_prompt is None:
            # self.stop_condition_prompt = '你是一个任务检查判断助手. 根据问题和答案检查否达到任务预期的完整性、准确性、相关性、清晰度和用户满意度标准？'
            self.stop_condition_prompt = 'You are a task evaluation assistant. Based on the question and answer, check if the task meets the standards of completeness, accuracy, relevance, clarity, and user satisfaction.'
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

class TaskAnalysisModule(dspy.Module):
    def __init__(self,role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None, input_fields: list[str] = None,objective:str=None,specifics:str=None,actions:str=None,results:str=None,example:str=None):
        super().__init__()
        if role == None:
            role = "You're a mission analysis assistant."
        if objective == None:
            objective = 'The main goal of the task is to extract and summarize the key information from the submitted task description, clarifying the main points and key requirements.'
        if specifics ==None:
            specifics = ('Main elements involved in the task description (e.g., goals, objects, environment).'
                         'Specific requirements and expected outcomes of the task.'
                         'Key points and potential challenges to focus on during task execution.')

        if results == None:
            results = "The returned result is a json object {'task_description':', 'keywords':} task_description is the result of summary and analysis of the task. Keywords is the keyword about this task, which cannot exceed 3 keywords. If keywords cannot be parsed, return []"
        if example == None:
            example = """
            问题: 分析《笑傲江湖》说明了什么？
            结果: 
            {"task_description": "分析《笑傲江湖》的核心思想和主题，包括分析主要人物及其行为动机，探讨主要事件及其影响，关注权力斗争、人性刻画和自由与束缚。","keywords": ["笑傲江湖", "金庸", "令狐冲"]}
        
            问题: 研究《红楼梦》中人物关系的复杂性。
            {"task_description": "研究《红楼梦》中人物关系的复杂性，包括分析主要人物及其关系网络，探讨人物之间的冲突和合作，关注人物关系、社会背景和情感纠葛。","keywords": ["红楼梦", "曹雪芹", "贾宝玉"]}
            
            问题: 中国的四大名著是什么?
            {"task_description": "识别并列出中国四大名著，提供每本书的简要描述，包括其主要主题和意义。","keywords": ["四大名著", "中国文学"]}
            
            """
        task_analysis_signature = init_costar_signature(role=role,backstory=backstory,output_fields=output_fields,input_fields=input_fields,objective=objective,specifics=specifics,actions=actions,results=results,example=example)
        self.predict = dspy.Predict(task_analysis_signature)
    def forward(self,question:str):
        predict = self.predict(question=question)
        return predict


class DataMergeModule(dspy.Module):
    def __init__(self, role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None,
                 input_fields: list[str] = None, objective: str = None, specifics: str = None, actions: str = None,
                 results: str = None, example: str = None):
        super().__init__()
        if role is None:
            role = "You are a data merge and analysis assistant."
        if objective is None:
            objective = "The main goal of the task is to merge and filter the data obtained from the RAG database and LLM query, and produce the best result."
        if specifics is None:
            specifics = ('Main elements involved in the data merge process (e.g., sources, data types, relevance).'
                         'Specific requirements and expected outcomes of the data merge task.'
                         'Key points and potential challenges to focus on during data merge and analysis.')
        if results is None:
            results = "Return different data structures according to the problem."
        if example is None:
            example = """
            
            """
        data_merge_signature = init_costar_signature(role=role, backstory=backstory, output_fields=output_fields,
                                                     input_fields=input_fields, objective=objective,
                                                     specifics=specifics, actions=actions, results=results,
                                                     example=example)
        self.predict = dspy.Predict(data_merge_signature)

    def forward(self, rag_data: str, llm_data: str):
        question = f"Combine and filter the following data obtained from the RAG database and LLM query:\nRAG Data: {rag_data}\nLLM Data: {llm_data}"
        predict = self.predict(question=question)
        return predict


from experiment_project.utils.initial.util import init_sys_env
from experiment_project.utils.files.read import read_yaml
import dspy

init_sys_env()
secret_env_file = '/mnt/d/project/zzbc/env_secret_config.yaml'

api_configs = read_yaml(secret_env_file)

model_config = api_configs.get('openai')
turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=2048,api_key=model_config.get('api_key'))
dspy.settings.configure(lm=turbo)


refine_module = TaskAnalysisModule()

result = refine_module.forward(question='中国的四大名著是什么?')
print(result)

