import random
from typing import Union, List
import dspy
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

from experiment_project.agents.dspy_module.base_module import TaskAnalysisModule
from experiment_project.utils.files.split import split_txt_by_langchain


class BaseRag(dspy.Module):
    def __init__(self,module_path:str,pg_connection:str=None,collection_name:str='my_docs',is_upload_file:bool=False,file_paths:List[str]=None,model_kwargs:dict={'device':0},chunk_size:int=256,encoding:str='utf-8'):
        super().__init__()
        self.embedding = HuggingFaceEmbeddings(model_name=module_path,model_kwargs=model_kwargs,multi_process=True,show_progress=True)
        if pg_connection is None:
            pg_connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!
        self.vectorstore = PGVector(
            embeddings=self.embedding,
            collection_name=collection_name,
            connection=pg_connection,
            use_jsonb=True,
        )
        if is_upload_file is True and file_paths is not None:
            self.upload_file_to_vector(file_paths=file_paths,chunk_size=chunk_size,encoding=encoding)
    def delete_collection(self):
        self.vectorstore.drop_tables()

    def upload_file_to_vector(self, file_paths: List[str],chunk_size:int=256,encoding:str='utf-8'):
        id_num = 0
        for file_path_num,file_path in enumerate(file_paths):
            data = split_txt_by_langchain(chuck_size=chunk_size,
                                          file_path=file_path,encoding=encoding)
            docs = []
            for num, text in enumerate(data):
                id_num +=1
                doc = Document(page_content=text, metadata={"id": id_num, 'chunk_index': num, 'chunk_size': len(text)})
                docs.append(doc)
            self.vectorstore.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])

    def search(self, question: str, k: int = 5):
        self.vectorstore.similarity_search(question, k=k)

class ReasonerRagModule(BaseRag):
    def __init__(self,reasoning_signature: dspy.Signature,module_path:str,pg_connection:str=None,collection_name:str='my_docs',is_upload_file:bool=False,file_paths:List[str]=None):
        super().__init__(module_path=module_path,pg_connection=pg_connection,collection_name=collection_name,is_upload_file=is_upload_file,file_paths=file_paths)

        self.reasoner = dspy.Predict(reasoning_signature)
        self.task_evaluation = TaskAnalysisModule()



    def forward(self, question:str,search):
        return self.prog(question=question)

