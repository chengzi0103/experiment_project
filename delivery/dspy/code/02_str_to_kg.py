# pip3 install spacy[transformers]
import json
import time
from typing import Union
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.output_parsers import CommaSeparatedListOutputParser,ListOutputParser,JsonOutputParser
from openai import OpenAI
from dyaichat.chat.chat import message_chat
from dyaichat.data_class.openai import OpenAiConfigPydantic
from extra.neo4j.conn import Neo4jDatabase


def read_text(file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt') -> str:
    content = ""
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    return content


def create_openai_client(api_url: str, api_key: str, model_name: str):
    openai_client = OpenAI(api_key=api_key, base_url=api_url)
    openai_config = OpenAiConfigPydantic(api_url=api_url, api_key=api_key,
                                         max_tokens=5012, model_name=model_name)
    return openai_client, openai_config


def split_doc_by_langchain(chuck_size: int = 1024, chuck_overlap: int = 0,
                           file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt'):
    loader = TextLoader(file_path, encoding='gbk')
    docs = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=chuck_size, chunk_overlap=chuck_overlap)
    texts = text_splitter.split_documents(docs)
    return texts


def split_txt_by_langchain(chuck_size: int = 1024, chuck_overlap: int = 0,
                           file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt') -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chuck_size,
        chunk_overlap=chuck_overlap,
        length_function=len,
    )

    texts = text_splitter.split_text(read_text(file_path=file_path))
    return texts

def load_named_entity_with_llm(openai_clinent, openai_config, texts:str,named_entity_prompt_template:Union[None,str]=None):
    if named_entity_prompt_template is None:
        named_entity_prompt_template = """
        [要求]
        - 阅读提供的文本。
        - 识别并列出所有重要的实体。实体可以是人名、地名、组织名、日期、事件等。
        - 对于每个实体，请指定其类型（例如人名、地点、组织等）。
        - 不能有重复的相同的内容
        ['奖励']
        - 如果你好好回答问题,我将向动物保护组织捐助100美元
    """
    named_entity_prompt_result_template = """
        [返回结果示例]
        - 实体列表: 每个实体应包括实体名称和实体类型。
        - 严格按照我定义的返回结果的模板来返回. 返回结果的模板案例: [{'entity_name':'','entity_rtype':''}]
"""
    named_entity_messages = [
        {"role": "system",
         "content": named_entity_prompt_template},
        {"role": "user", "content": f"这里是需要进行实体总结的段落: {texts}"},
        {"role": "system", "content": f"这里是需要返回的结果格式定义 : {named_entity_prompt_result_template}"},
    ]
    named_entity_result = message_chat(messages=named_entity_messages, openai_config=openai_config,
                                       openai_client=openai_clinent)
    return named_entity_result

def generate_knowledge_graph_data(openai_clinent, openai_config, texts:str, named_entity:str, knowledge_graph_prompt_template:Union[None,str]=None, result_prompt_template:Union[None,str]=None):
    if knowledge_graph_prompt_template is None:
        knowledge_graph_prompt_template = f"""
    你是一个专门从文本资料中抽取信息以构建知识图谱的助理。从文本中精确抽取相关信息。组装成一个知识图谱需要的数据,如果你遇到无法回答的情况，请回答null。
    [内容]
    {texts}
    
    [实体类型]
    {named_entity}
    [要求]
    - 请你根据我传递过来的每一个entity_name和entity_type,根据构建知识图谱的原理,构建出一个完整的数据体系
    - 如果某个实体没有在文本中明确定义，你应该根据上下文推断其可能的属性和与其他实体的关联关系，并尽可能提供详细信息。
    - 以当前案例作为例子,输出格式和案例的输出格式保持一致,果请直接生成为python中list[dict]的类型,并且每个key标注清楚内容,你返回的结果可以直接被python中的json.loads()的方法解析,结果不包含\n的字符和其他特殊字符,并且返回结果全部变成双引号

    ['奖励']
    - 如果你好好回答问题,我将向动物保护组织捐助100美元
    """
    if result_prompt_template is None:
        result_prompt_template = """
    [输出结果案例]:
    - 请你大概按照这个下面的案例,将结果输出
    - 输出结果的key值不能包含中文,只能是英文
    - 返回结果变成json返回
    [
        {
            "entity_name": "",
            "entity_type": "",
            "description": "",
            "relationships": [
                {"related_entity": "", "relation_type": ""},
                {"related_entity": "", "relation_type": ""}
            ]
        },

    """
    messages = [
        {"role": "system",
         "content": f"请你按照要求构建知识图谱模型: {knowledge_graph_prompt_template}"},
        # {"role": "user", "content": f"这里是需要总结的文本: {texts}"},
        # {"role": "user", "content": f"这里是需要进行总结的实体词和类型 : {named_entity}"},
        {"role": "system", "content": f"请你按照下面的输出格式,将结果输出 : {result_prompt_template}"},

    ]
    result = message_chat(messages=messages, openai_config=openai_config, openai_client=openai_clinent)
    return result

def json_output_openai_result(data:str):
    output_parser = JsonOutputParser()
    return output_parser.parse(data)

def init_neo4j():
    return Neo4jDatabase(ip='192.168.0.131',port=7687,user_name='cc',password='123456')


def clean_entity_name(name):
    # 清理名称中的不允许字符，例如空格和引号
    return name.replace('《', '').replace('》', '').replace("'", "")


def generate_cypher(entities):
    cypher_commands = []
    created_entities = set()

    for entity in entities:
        entity_name = clean_entity_name(entity['entity_name'])
        entity_type = entity['entity_type'].lower()  # 将实体类型转为小写以用作标签
        description = entity.get('description', '')

        # 创建节点命令，如果节点描述存在，则设置描述属性
        if entity_name not in created_entities:
            create_command = f"MERGE ({entity_name}:{entity_type.capitalize()} {{name: '{entity_name}'}})"
            if description:
                create_command += f"\nON CREATE SET {entity_name}.description = '{description}'"
            cypher_commands.append(create_command)
            created_entities.add(entity_name)

        # 创建关系命令
        if 'relationships' in entity:
            for relationship in entity['relationships']:
                related_entity = clean_entity_name(relationship['related_entity'])
                relation_type = relationship['relation_type'].replace("'", "")  # 清理关系类型中的引号

                # 确保关联实体也被创建
                if related_entity not in created_entities:
                    cypher_commands.append(
                        f"MERGE ({related_entity}:Entity {{name: '{related_entity}'}})")  # 默认为Entity类型
                    created_entities.add(related_entity)

                # 添加关系
                cypher_commands.append(f"MERGE ({entity_name})-[:{relation_type.upper()}]->({related_entity})")

    return "\n".join(cypher_commands)

qwen32b_api_url, qwen32b_key, qwen32b_model_name = 'http://127.0.0.1:11434/v1', 'EMPTY', 'qwen:32b'
qwen14b_api_url, qwen14b_key, qwen14b_model_name = 'http://192.168.0.11:11434/v1', 'EMPTY', 'qwen:14b'
# llama3_api_url, llama3_api_key, llama3_model_name = 'http://192.168.0.11:11434/v1', 'EMPTY', 'wangshenzhi/llama3-8b-chinese-chat-ollama-fp16:latest'
# llama3_client, llama3_config = create_openai_client(llama3_api_url, llama3_api_key, llama3_model_name)
qwen32b_client, qwen32b_config = create_openai_client(qwen32b_api_url, qwen32b_key, qwen32b_model_name)
qwen14b_client, qwen14b_config = create_openai_client(qwen14b_api_url, qwen14b_key, qwen14b_model_name)
qwen32b_config.temperature = 0.6
texts = split_txt_by_langchain()
neo4j = init_neo4j()
for idx_num,split_text in enumerate(texts[1:]):

    t1 = time.time()
    if idx_num == 0:
        knowledge_graph_data = texts[0] + texts[1] + texts[2]
    elif idx_num == len(texts)-2:
        knowledge_graph_data = texts[-3] + texts[-2] + texts[-1]
    else:
        knowledge_graph_data = texts[idx_num-1] + texts[idx_num] + texts[idx_num+1]
    print('---------------------------------------------------------------------------')
    named_entity = load_named_entity_with_llm(openai_config=qwen32b_config,openai_clinent=qwen32b_client,texts=split_text)
    print(f'这是当前段落的实体词和类型:  {named_entity}')
    result = generate_knowledge_graph_data(texts=knowledge_graph_data, named_entity=named_entity, openai_config=qwen32b_config, openai_clinent=qwen32b_client)
    result = json_output_openai_result(result)
    cypher_text = neo4j.build_cypher_by_llm_result(data=result)
    cypher_text = generate_cypher(result)
    neo4j.execute_cypher(cypher_text)
    print(f'花费时间 : {time.time() - t1}    当前段落：{idx_num}  剩余段落：{len(texts)-idx_num-1}' )
    print(f'当前分析后的结果是: {result}')
    if idx_num == 5:
        break