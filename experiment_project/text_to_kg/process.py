from typing import Union
import dspy
import time
from experiment_project.text_to_kg.module import EntitieCoTModule, TextToKGModule
from experiment_project.utils.ai.util import json_output_openai_result
from experiment_project.utils.files.split import split_txt_by_langchain
from experiment_project.utils.initial.util import init_sys_env
import os
from experiment_project.utils.knowledge_graph.conn import execute_cypher_statements
from experiment_project.utils.knowledge_graph.util import generate_cypher_statements





def text_to_kg(file_path:str,model_api_key:str,model_name:str='gpt-4o',model_max_tokens:int=4096,encoding:str='gbk',chunk_size:int=520,entitie_optimized_file_path:Union[str,None]=None,proxy_url:Union[None,str]=None,neo4j_uri:str='bolt://localhost:7687',neo4j_user_name:str='cc',neo4j_password:str='Tt66668888..'):
    if proxy_url is not None:
        init_sys_env(proxy_url=proxy_url)
    os.environ['NEO4J_URI'] = neo4j_uri
    os.environ['NEO4J_USERNAME'] = neo4j_user_name
    os.environ['NEO4J_PASSWORD'] = neo4j_password
    text_data = split_txt_by_langchain(file_path=file_path, chuck_size=chunk_size, encoding=encoding)
    turbo = dspy.OpenAI(model=model_name, max_tokens=model_max_tokens, api_key=model_api_key)
    dspy.settings.configure(lm=turbo)
    entitie_optimized_cot = EntitieCoTModule()
    if entitie_optimized_file_path is not None:
        entitie_optimized_cot.load(entitie_optimized_file_path)
    text_to_kg_cot = TextToKGModule(entitie_optimized_cot=entitie_optimized_cot)
    ero_data = []
    for num, data in enumerate(text_data):
        t1 = time.time()
        kg_data = text_to_kg_cot.forward(context=data)
        print(f'当前模型处理数据时间是   {time.time() - t1}  ', )
        try:

            cypher_data = generate_cypher_statements(json_output_openai_result(kg_data.return_json))
            execute_cypher_statements(uri=neo4j_uri, user=neo4j_user_name, password=neo4j_password, cypher=cypher_data)
        except Exception as e:
            ero_data.append(kg_data)
            if len(ero_data) >2:
                raise RuntimeError(f'在进行dspy中的预测时，结果出现错误  在第 {num} 块的时候出现问题 ')
        print(f'当前片段用时  {time.time() - t1} , 当前片段索引  {num} , 总数据量  {len(text_data)}')