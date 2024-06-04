import json

from experiment_project.utils.initial.util import init_sys_env
from experiment_project.utils.files.read import read_yaml
from experiment_project.utils.knowledge_graph.conn import execute_cypher_statements
from experiment_project.utils.files.split import split_txt_by_langchain
import dspy
from experiment_project.utils.knowledge_graph.util import generate_cypher_statements
import os
from dspy.teleprompt import BootstrapFewShot
from dspy.retrieve.neo4j_rm import Neo4jRM
import time
from experiment_project.utils.knowledge_graph.neo4j_index import create_index_by_entities
init_sys_env(proxy_url='http://192.168.31.215:10890')
secret_env_file = '/mnt/c/Users/chenzi/Desktop/project/experiment_project/env_secret_config.yaml'
api_configs = read_yaml(secret_env_file)
model_config = api_configs.get('openai')
turbo = dspy.OpenAI(model=model_config.get('model'), max_tokens=4096,api_key=model_config.get('api_key'))
# turbo = dspy.OllamaLocal(model='qwen:32b-text-v1.5-q4_0',base_url='http://192.168.0.75:11434')
dspy.settings.configure(lm=turbo)

uri = 'bolt://localhost:7687'
user = 'cc'
password = 'Tt66668888..'
os.environ['NEO4J_URI'] = uri
os.environ['NEO4J_USERNAME'] = user
os.environ['NEO4J_PASSWORD'] = password
index_name='test_index'
create_index_by_entities(uri=uri, user=user, password=password, index_name=index_name,property_name='entity_name')
