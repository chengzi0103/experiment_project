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
            upload_files_to_vector(vectorstore=self.vectorstore,files_path=files_path, chunk_size=chunk_size, encoding=encoding)

    def delete_collection(self):
        delete_vector_collection(vectorstore=self.vectorstore)

    def search(self, keywords: Union[List[str],str], k: int = 6):
        return search_vector(vectorstore=self.vectorstore,keywords=keywords,k=k)

    @property
    def no_cache(self):
        return dict(temperature=0.7 + 0.0001 * random.uniform(-1, 1))



class SelfRefineRagModule(BaseRag):
    def __init__(self,module_path:str=None,model_name:str=None, pg_connection:str=None, collection_name:str='my_docs', is_upload_file:bool=False, files_path:List[str]=None,encoding:str= 'utf-8',chunk_size:int=256,multi_process:bool=False,rag_search_num:int=5,max_iterations:int=3, feedback_prompt:Union[str,None]=None, refinement_prompt:Union[str,None]=None, stop_condition_prompt:Union[str,None]=None, temperature:float=0.7):
        super().__init__(module_path=module_path, pg_connection=pg_connection, collection_name=collection_name,
                         is_upload_file=is_upload_file, files_path=files_path, encoding=encoding, chunk_size=chunk_size,
                         multi_process=multi_process, model_name=model_name)
        self.task_evaluation = FindTaskKeyWordsModule()




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
        self.predict = dspy.Predict(data_merge_signature)
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

    def forward(self, question:str):
        task_result = json_output_openai_result(self.task_evaluation.forward(question=question).answer)
        question = task_result.get('task_description')
        keywords = task_result.get('keywords')
        llm_result = ''
        all_rag_result = self.search(keywords=keywords,k=self.rag_search_num)
        quality_enhancer_result = self.quality_enhancer.forward(question=question,rag_data=json.dumps(all_rag_result),llm_data=llm_result,)
        result = ''
        if quality_enhancer_result.answer == '':
            result = quality_enhancer_result.results
        else:
            result = quality_enhancer_result.answer
        return result



# from experiment_project.utils.initial.util import init_sys_env
# from experiment_project.utils.files.read import read_yaml
# import dspy
#
# init_sys_env()
# # secret_env_file = '/mnt/c/Users/chenzi/Desktop/project/env_secret_config.yaml'
# secret_env_file = '/mnt/d/project/zzbc/env_secret_config.yaml'
#
# api_configs = read_yaml(secret_env_file)
#
# model_config = api_configs.get('openai')
# turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=4096,api_key=model_config.get('api_key'))
# dspy.settings.configure(lm=turbo)
# module_path = '/mnt/d/models/embeddings/bce-embedding-base_v1'
# collection_name = 'pdf'
# files_path =['/mnt/c/Users/cc/Desktop/pic/Text-Animator Controllable Visual Text Video Generation.pdf']
# reasoner_rag = ReasonerRagModule(module_path=module_path,files_path=files_path,collection_name=collection_name,is_upload_file=True)
# result = reasoner_rag.forward(question="Get the author, main achievements, creation time, and summary of the article 'Text-Animator Controllable Visual Text Video Generation'.")
