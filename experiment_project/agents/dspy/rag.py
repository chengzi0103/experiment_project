import json
import random
import time
from pathlib import Path
from typing import Union, List
import dspy
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

from experiment_project.agents.dspy.base_signature import init_costar_signature, init_costar_signature, \
    selfrefine_costar_signature
from experiment_project.utils.ai.util import json_output_openai_result
from experiment_project.utils.files.split import split_txt_by_langchain
from langchain_community.document_loaders import PyPDFLoader

from experiment_project.utils.rag.embedding.huggingface import load_embedding_model
from experiment_project.utils.rag.vector.pgvector import create_pgvector, upload_files_to_vector, \
    delete_vector_collection, search_vector


class BaseRag(dspy.Module):
    def __init__(self, module_path:str=None,model_name:str=None, pg_connection:str=None, collection_name:str='my_docs', is_upload_file:bool=False, files_path:List[str]=None, model_kwargs:dict={'device':0}, chunk_size:int=256, encoding:str= 'utf-8',multi_process:bool=False):
        super().__init__()
        self.embedding = load_embedding_model(module_path=module_path,model_kwargs=model_kwargs,multi_process=multi_process,model_name=model_name)
        self.vectorstore = create_pgvector(embedding=self.embedding, collection_name=collection_name, pg_connection=pg_connection)
        if is_upload_file is True and files_path is not None:
            # self.delete_collection()
            upload_files_to_vector(vectorstore=self.vectorstore,files_path=files_path, chunk_size=chunk_size, encoding=encoding)

    def delete_collection(self):
        delete_vector_collection(vectorstore=self.vectorstore)

    def search(self, keywords: Union[List[str],str], k: int = 6):
        return search_vector(vectorstore=self.vectorstore,keywords=keywords,k=k)

    @property
    def no_cache(self):
        return dict(temperature=0.7 + 0.0001 * random.uniform(-1, 1))

    def get_result(self,result_module):
        answer = ''
        if result_module.answer == '':
            answer = result_module.objective
        else:
            answer = result_module.answer
        return answer

    def replace_prefix(self,data:str):
        return data.replace('Question:','').replace('Answer: ','')



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
        task_analysis_signature = init_costar_signature(role=role, backstory=backstory, output_fields=output_fields, input_fields=input_fields, objective=objective, specifics=specifics, actions=actions, results=results, example=example)
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
            self.results = """The result must be a JSON object, {"task_description":"question","keywords":[""]}, where task_description represents the current task and keywords are the keywords identified from the task."""
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
        task_analysis_signature = init_costar_signature(role=role,
                                                        output_fields=output_fields, input_fields=input_fields,
                                                        objective=objective,  actions=actions,
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

        data_merge_signature = init_costar_signature(role=role, backstory=backstory, output_fields=output_fields,
                                                     input_fields=input_fields, objective=objective,
                                                     specifics=specifics, actions=actions, results=results,
                                                     example=example)
        self.predict = dspy.ChainOfThought(data_merge_signature)
    @property
    def no_cache(self):
        return dict(temperature=0.7 + 0.0001 * random.uniform(-1, 1))

    def forward(self,question:str, rag_data: str, llm_data: str):
        predict = self.predict(question=question,rag_data=rag_data,llm_data=llm_data,role=self.role,backstory=self.backstory,objective=self.objective,actions=self.actions,example=None,**self.no_cache)
        return predict

class ReasonerRagModule(BaseRag):
    def __init__(self, module_path:str=None,model_name:str=None, pg_connection:str=None, collection_name:str='my_docs', is_upload_file:bool=False, files_path:List[str]=None,encoding:str= 'utf-8',chunk_size:int=256,multi_process:bool=False,rag_search_num:int=5):
        super().__init__(module_path=module_path, pg_connection=pg_connection, collection_name=collection_name, is_upload_file=is_upload_file, files_path=files_path,encoding=encoding,chunk_size=chunk_size,multi_process=multi_process,model_name=model_name)

        self.task_evaluation = FindTaskKeyWordsModule()
        self.quality_enhancer = QualityEnhancerModule()
        self.rag_search_num = rag_search_num

    def rag_search(self, question: str, llm_result: str = ''):
        try:
            task_result = json_output_openai_result(self.task_evaluation.forward(question=question).answer)

            question = task_result.get('task_description')
            keywords = task_result.get('keywords')
        except:
            keywords = question
        all_rag_result = self.search(keywords=keywords, k=self.rag_search_num)
        quality_enhancer_result = self.quality_enhancer.forward(question=question, rag_data=json.dumps(all_rag_result),
                                                                llm_data=llm_result, )
        result = ''
        if quality_enhancer_result.answer == '':
            result = quality_enhancer_result.results
        else:
            result = quality_enhancer_result.answer
        return result

    def forward(self, question:str):
        return self.rag_search(question=question)

class SelfRefineRagModule(ReasonerRagModule):
    def __init__(self,module_path:str=None,model_name:str=None, pg_connection:str=None, collection_name:str='my_docs', is_upload_file:bool=False, files_path:List[str]=None,encoding:str= 'utf-8',chunk_size:int=256,multi_process:bool=False,rag_search_num:int=5,max_iterations:int=3, feedback_prompt:Union[str,None]=None, refinement_prompt:Union[str,None]=None, stop_condition_prompt:Union[str,None]=None, temperature:float=0.7):
        super().__init__(module_path=module_path, pg_connection=pg_connection, collection_name=collection_name,
                         is_upload_file=is_upload_file, files_path=files_path, encoding=encoding, chunk_size=chunk_size,
                         multi_process=multi_process, model_name=model_name)
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
        self.max_iterations = max_iterations
        self.rag_search_num = rag_search_num

        # self.predict = dspy.Predict(self_refine_signature)
    def feedback(self,question:str,context:str):
        """
        对任务和内容进行反馈 通过prompt的定义查看任务结果是否需要优化
        """
        # predict_evaluation = dspy.Predict(init_multiple_inputs_signature(role=self.feedback_prompt,backstory='说明对内容的建议是什么?'),**self.no_cache)
        predict_evaluation = dspy.Predict(selfrefine_costar_signature(input_fields={'context':"The content that needs suggestions"}))
        evaluate = predict_evaluation(question=self.replace_prefix(question),context=self.replace_prefix(context),role=self.feedback_prompt,backstory='Explain what the suggestions for the content are.?',**self.no_cache)
        answer = self.get_result(evaluate)
        return answer
    def refinement(self,question:str,feedback_question:str,evaluate_data:str):
        """
        根据feedback之后的建议,来对运行任务
        """
        llm_data = self.rag_search(question=feedback_question)

        quality_enhancer = self.quality_enhancer.forward(question=question, rag_data=evaluate_data,llm_data=llm_data, )
        answer = self.get_result(quality_enhancer)
        return answer

    def stop_condition(self,question:str,context:str):
        """
        查看任务是否符合我们的期望和要求
        """
        predict_stop_condition = dspy.Predict(selfrefine_costar_signature(input_fields={'context':"The content that needs suggestions"}))
        stop_condition = predict_stop_condition(role=self.stop_condition_prompt,backstory='只回答 “是”或“否”。',question=self.replace_prefix(question),context=self.replace_prefix(context),**self.no_cache)
        answer = self.get_result(stop_condition)
        return answer
    def forward(self,question:str) -> str:
        answer = self.rag_search(question=question)
        for num in range(0, self.max_iterations):
            feedback_question = self.feedback(question=question, context=answer)
            print(f'在第{num}次迭代后 , evaluate_answer :   {feedback_question}')
            refinement_answer = self.refinement(question=question, evaluate_data=answer,feedback_question=feedback_question)
            print(f'在第{num}次迭代后 , refinement_answer :   {refinement_answer}')
            stop_condition_status = self.stop_condition(question=question, context=refinement_answer)
            if '是' in stop_condition_status:
                return refinement_answer
            else:
                answer = refinement_answer
        return answer
# from experiment_project.utils.initial.util import init_sys_env
# from experiment_project.utils.files.read import read_yaml
# import dspy
#
# # init_sys_env()
# # secret_env_file = '/mnt/c/Users/chenzi/Desktop/project/env_secret_config.yaml'
# secret_env_file = '/mnt/d/project/zzbc/env_secret_config.yaml'
#
# api_configs = read_yaml(secret_env_file)
#
# # model_config = api_configs.get('openai')
# model_config = api_configs.get('openai')
# turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=4096,api_key=model_config.get('api_key'),api_base=model_config.get('base_url'))
# # turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=4096,api_key=model_config.get('api_key'))
# dspy.settings.configure(lm=turbo)
# module_path = '/mnt/d/models/embeddings/bce-embedding-base_v1'
# collection_name = 'pdf'
# files_path =['/mnt/c/Users/cc/Desktop/pic/Text-Animator Controllable Visual Text Video Generation.pdf','']
# reasoner_rag = ReasonerRagModule(module_path=module_path,files_path=files_path,collection_name=collection_name,is_upload_file=True)
# result = reasoner_rag.forward(question="Get the author, main achievements, creation time, and summary of the article 'Text-Animator Controllable Visual Text Video Generation'.")

# llm_data = 'Answer: To optimize the final result for a given question, integrate the outputs generated by the Retrieval-Augmented Generation (RAG) system with the responses generated by the Large Language Model (LLM). This involves combining the retrieved and generated information based on the question to provide a more accurate and comprehensive answer. Primarily use data from rag_data, with llm_result as a supplement.\n\n**Completeness:** The summary should include all key points from the main achievements to provide a comprehensive overview. For instance, the Text-Animator method is highlighted for its innovative approach to integrating textual elements into generated videos, ensuring semantic understanding and fine-grained textual semantics.\n\n**Accuracy:** Verify the creation time and other factual details to ensure they are correct and up-to-date. For example, the Text-Animator method was compared with other state-of-the-art methods like AnimateLCM, I2VGen-XL, and SVD, and it was found to outperform them in terms of video quality and fidelity of textual representation.\n\n**Relevance:** Focus on the most impactful achievements and contributions of the article to highlight its significance. The Text-Animator method\'s dual control mechanisms—camera and position control—are crucial for synchronizing text animation with video motion, enhancing unity and coordination between textual elements and video scenes.\n\n**Clarity:** Simplify technical jargon where possible to make the content more accessible to a broader audience. For example, instead of using terms like "text embedding injection module," you could say "a module that helps the system understand and generate text accurately."\n\n**User Satisfaction:** Include practical applications or potential implications of the research to engage readers and demonstrate the real-world relevance of the work. The Text-Animator method has significant potential in various domains, including e-commerce, advertising, and the film industry, where integrating text seamlessly into videos is essential.\n\nBy following these suggestions, the final summary will be more comprehensive, accurate, relevant, clear, and engaging for the readers.'
# rag_data = '**Answer:**\n\n**Author:** Lin Liu, Quande Liu, Shengju Qian, Yuan Zhou, Wengang Zhou, Houqiang Li, Lingxi Xie, Qi Tian\n\n**Main Achievements:**\n1. **Text-Animator**: A novel approach for visual text video generation.\n2. **Text Embedding Injection Module**: Enhances the precise understanding and generation capacity for visual text.\n3. **Camera Control Module**: Controls the movement of text to ensure consistency with the scene content.\n4. **Text Refinement Module**: Improves the stability of generated visual text by controlling the camera movement and the motion of visualized text.\n5. **Extensive Experiments**: Demonstrated that Text-Animator outperforms existing T2V and hybrid T2I/I2V methods in terms of video quality and fidelity of textual representation.\n\n**Creation Time:** The paper was submitted on June 25, 2024.\n\n**Summary:** Text-Animator is a pioneering method designed to address the challenge of integrating textual elements effectively into generated videos. It emphasizes both semantic understanding and fine-grained textual semantics, ensuring that visualized text is dynamically integrated into video content while maintaining motion coherence. The approach introduces dual control mechanisms—camera and position control—to synchronize text animation with video motion, thereby enhancing unity and coordination between textual elements and video scenes. Extensive quantitative and qualitative experimental results demonstrate the superiority of Text-Animator in generating accurate visual text over state-of-the-art video generation methods. The method has significant potential in various domains, including e-commerce, advertising, and the film industry, where integrating text seamlessly into videos is essential.'
# question = "Get the author, main achievements, creation time, and summary of the article 'Text-Animator Controllable Visual Text Video Generation'."
# quality_enhancer = QualityEnhancerModule()
# quality_enhancer_result = quality_enhancer.forward(question=question, rag_data=rag_data, llm_data=llm_data, )
# print(quality_enhancer_result)
