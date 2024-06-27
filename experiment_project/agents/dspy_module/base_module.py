import random
from typing import Union, List

import dspy

from experiment_project.agents.dspy_module.base_signature import init_multiple_inputs_signature, init_base_signature, \
    init_consensus_signature, init_costar_signature, init_costar_signature_input


# from experiment_project.dspy_module.agent_signature import init_base_signature, init_multiple_inputs_signature, \
#     init_consensus_signature


class ReasonerModule(dspy.Module):
    def __init__(self,reasoning_signature: dspy.Signature,):
        super().__init__()

        self.prog = dspy.Predict(reasoning_signature)

    def forward(self, question):
        return self.prog(question=question)

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
            self.role = "You're a mission analysis assistant."
        if objective == None:
            self.objective = 'The main goal of the task is to extract and summarize the key information from the submitted task description, clarifying the main points and key requirements.'
        if specifics ==None:
            self.specifics = ('Main elements involved in the task description (e.g., goals, objects, environment).'
                         'Specific requirements and expected outcomes of the task.'
                         'Key points and potential challenges to focus on during task execution.')

        if results == None:
            self.results = "The returned result is a json object No other format or content is required {'task_description':', 'keywords':} task_description is the result of summary and analysis of the task. Keywords is the keyword about this task, which cannot exceed 3 keywords. If keywords cannot be parsed, return []"
        if example == None:
            self.example = """
            问题: "Provide a detailed summary of the theme and explanation of the paper 'Text-Animator Controllable Visual Text Video Generation'. Additionally, explain which papers it cites, what achievements it has made, when it was written, and who the authors are."
            结果: {"task_description": "Provide a detailed summary of the theme and explanation of the paper 'Text-Animator Controllable Visual Text Video Generation'. Additionally, explain which papers it cites, what achievements it has made, when it was written, and who the authors are.","keywords": ["summary", "theme", "Text-Animator Controllable Visual Text Video Generation", "achievements", "authors"]}

        
            问题: 研究《红楼梦》中人物关系的复杂性。
            {"task_description": "研究《红楼梦》中人物关系的复杂性。","keywords": ["红楼梦", "人物关系", "复杂性"]}
            
            问题: 中国的四大名著是什么?
            {"task_description": "中国的四大名著是什么?","keywords": ["四大名著", "中国"]}
            
            """
        task_analysis_signature = init_costar_signature_input(role=role,backstory=backstory,output_fields=output_fields,input_fields=input_fields,objective=objective,specifics=specifics,actions=actions,results=results,example=example)
        self.predict = dspy.Predict(task_analysis_signature)
    def forward(self,question:str):
        predict = self.predict(question=question,role=self.role,example=self.example,specifics=self.specifics,results=self.results,**self.no_cache)
        return predict
    @property
    def no_cache(self):
        return dict(temperature=0.7 + 0.0001 * random.uniform(-1, 1))


class FindTaskKeyWordsModule(dspy.Module):
    def __init__(self, role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None,
                 input_fields: list[str] = None, objective: str = None, specifics: str = None, actions: str = None,
                 results: str = None, example: str = None):
        super().__init__()
        if role == None:
            self.role = "Analyze the task description to extract and list key concepts or keywords."
        if objective == None:
            self.objective = 'Clarify the main goal of the task: Extract and list the keywords from the task description, ensuring the number of keywords does not exceed 5.'
        if actions == None:
            self.actions = ('Read and understand the task description provided by the user.'
                              'Extract 3 to 5 keywords from the task description.'
                              'Ensure the keywords accurately reflect the core content of the task.'
                            'If the keyword cannot be extracted, it returns []')

        if results == None:
            self.results = "Describe the expected results or outcomes: Successfully extract and list the keywords from the task description, with a total not exceeding 5, accurately reflecting the core content of the task."
        if example == None:
            self.example = """
            问题： 你是谁？
            结果： {"task_description": "你是谁？","keywords": []}
            
            问题: "Provide a detailed summary of the theme and explanation of the paper 'Text-Animator Controllable Visual Text Video Generation'. Additionally, explain which papers it cites, what achievements it has made, when it was written, and who the authors are."
            结果: {"task_description": "Provide a detailed summary of the theme and explanation of the paper 'Text-Animator Controllable Visual Text Video Generation'. Additionally, explain which papers it cites, what achievements it has made, when it was written, and who the authors are.","keywords": ["summary", "theme", "Text-Animator Controllable Visual Text Video Generation", "achievements", "authors"]}


            问题: 研究《红楼梦》中人物关系的复杂性。
            {"task_description": "研究《红楼梦》中人物关系的复杂性。","keywords": ["红楼梦", "人物关系", "复杂性"]}

            问题: 中国的四大名著是什么?
            {"task_description": "中国的四大名著是什么?","keywords": ["四大名著", "中国"]}

            """
        task_analysis_signature = init_costar_signature_input(role=role, backstory=backstory,
                                                              output_fields=output_fields, input_fields=input_fields,
                                                              objective=objective, specifics=specifics, actions=actions,
                                                              results=results, example=example)
        self.predict = dspy.Predict(task_analysis_signature)

    def forward(self, question: str):
        predict = self.predict(question=question, role=self.role, example=self.example,actions=self.actions,objective=self.objective,
                               results=self.results, **self.no_cache)
        return predict

    @property
    def no_cache(self):
        return dict(temperature=0.7 + 0.0001 * random.uniform(-1, 1))

class QualityEnhancerModule(dspy.Module):
    def __init__(self, role: Union[str, None] = None, backstory: Union[str, None] = None, output_fields: dict = None,
                 input_fields: list[str] = None, objective: str = None, specifics: str = None, actions: str = None,
                 results: str = None, example: str = None):
        super().__init__()
        if role is None:
            self.role = "Quality Enhancer"
        if backstory is None:
            # backstory = 'Provides the background information for the task. It gives context and helps understand the purpose and the setting of the task.'
            self.backstory = 'This module is designed to enhance the quality of answers by integrating RAG and LLM outputs.Primarily use data from rag_data, with llm_result as a supplement'
        if objective is None:
            # objective = " To optimize the final result for a given question, integrate the outputs generated by the Retrieval-Augmented Generation (RAG) system with the responses generated by the Large Language Model (LLM). This involves combining the retrieved and generated information based on the question to provide a more accurate and comprehensive answer."
            self.objective = """To optimize the final result for a given question, integrate the outputs generated by the "
               "Retrieval-Augmented Generation (RAG) system with the responses generated by the Large Language Model (LLM). "
               "This involves combining the retrieved and generated information based on the question to provide a more accurate and comprehensive answer. Primarily use data from rag_data, with llm_result as a supplement """
        if actions is None:
            self.actions = "Merge and analyze RAG and LLM outputs to generate the final answer.Primarily use data from rag_data, with llm_result as a supplement."
        if input_fields is None:
            input_fields = {'rag_data':'Data after rag query','llm_data':'Data after LLM query'}

        data_merge_signature = init_costar_signature_input(role=role, backstory=backstory, output_fields=output_fields,
                                                     input_fields=input_fields, objective=objective,
                                                     specifics=specifics, actions=actions, results=results,
                                                     example=example)
        self.predict = dspy.Predict(data_merge_signature)
    @property
    def no_cache(self):
        return dict(temperature=0.7 + 0.0001 * random.uniform(-1, 1))

    def forward(self,question:str, rag_data: str, llm_data: str):
        predict = self.predict(question=question,rag_data=rag_data,llm_data=llm_data,role=self.role,backstory=self.backstory,objective=self.objective,actions=self.actions,example=None,**self.no_cache)
        return predict



