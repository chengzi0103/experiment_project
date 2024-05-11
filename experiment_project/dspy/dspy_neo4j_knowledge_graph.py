"""
Text -> Knowledge Graph
1. text -> cypher

Constraints:
- Use the existing schema before creating new nodes and relationships.
"""
import os
from dotenv import find_dotenv, load_dotenv
import dspy
from langchain_text_splitters import RecursiveCharacterTextSplitter

def read_text(file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt') -> str:
    content = ""
    with open(file_path, 'r', encoding='gbk') as f:
        content = f.read()
    return content
def split_txt_by_langchain(chuck_size: int = 1024, chuck_overlap: int = 0,
                           file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt') -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chuck_size,
        chunk_overlap=chuck_overlap,
        length_function=len,
    )

    texts = text_splitter.split_text(read_text(file_path=file_path))
    return texts
# ollama_model = dspy.OpenAI(api_base='http://127.0.0.1:11434/v1',model="qwen:32b", max_tokens=5012,api_key='ollama' )
ollama_model = dspy.OllamaLocal(model="qwen:32b", max_tokens=5012 )
ollama_model('你好?')
# dspy.OllamaLocal
# # set up Neo4j using NEO4J_URI
# neo4j = Neo4j(uri=os.getenv("NEO4J_URI"), user=os.getenv("NEO4J_USER"), password=os.getenv("NEO4J_PASSWORD"))
#
# lm = dspy.OpenAI(
#     model="gpt-4",
#     max_tokens=1024,
# )
# dspy.configure(lm=lm)
#
#
# class CypherFromText(dspy.Signature):
#     """Instructions:
#     Create a Cypher MERGE statement to model all entities and relationships found in the text following these guidelines:
#     - Refer to the provided schema and use existing or similar nodes, properties or relationships before creating new ones.
#     - Use generic categories for node and relationship labels."""
#
#     text = dspy.InputField(desc="Text to model using nodes, properties and relationships.")
#     neo4j_schema = dspy.InputField(desc="Current graph schema in Neo4j as a list of NODES and RELATIONSHIPS.")
#     statement = dspy.OutputField(desc="Cypher statement to merge nodes and relationships found in the text.")
#
#
# generate_cypher = dspy.ChainOfThought(CypherFromText)
#
# if __name__ == "__main__":
#     from pathlib import Path
#
#     # import json
#
#     # examples_path = Path(__file__).parent / "examples" / "wikipedia-abstracts-v0_0_1.ndjson"
#     # with open(examples_path, "r") as f:
#     #     # process line by line
#     #     for line in f:
#     #         data = json.loads(line)
#     #         text = data["text"]
#     #         print(text[:50])
#     #         cypher = generate_cypher(text=text, neo4j_schema=neo4j.fmt_schema())
#     #         neo4j.query(cypher.statement.replace('```', ''))
#
#     while True:
#         try:
#             text = input("\nEnter text: ")
#             cypher = generate_cypher(text=text.replace("\n", " "), neo4j_schema=neo4j.fmt_schema())
#             neo4j.query(cypher.statement.replace('```', ''))
#
#         except Exception as e:
#             print(e)
#             print("Please input one paragraph at a time.")
#             continue
#
#         except KeyboardInterrupt:
#             break