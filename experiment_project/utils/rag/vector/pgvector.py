from typing import List, Union
import time
from langchain_postgres import PGVector

from experiment_project.utils.rag.split.util import split_files


def create_pgvector(embedding, collection_name: str = 'doc', pg_connection: str = None)->PGVector:
    """
    创建一个 PGVector 向量存储实例。

    参数:
    embedding: 用于存储向量的嵌入模型。
    collection_name (str, 可选): 存储向量的集合名称，默认为 'doc'。
    pg_connection (str, 可选): PostgreSQL 数据库的连接字符串，默认为 'postgresql+psycopg://langchain:langchain@localhost:6024/langchain'。

    返回:
    vectorstore: 创建的 PGVector 向量存储实例。
    """
    if pg_connection is None:
        pg_connection = 'postgresql+psycopg://langchain:langchain@localhost:6024/langchain'
    vectorstore = PGVector(
        embeddings=embedding,
        collection_name=collection_name,
        connection=pg_connection,
        use_jsonb=True,
    )
    return vectorstore



def delete_vector_collection(vectorstore:PGVector):
    """
    删除指定的向量存储集合。

    参数:
    vectorstore: 要删除集合的 PGVector 向量存储实例。

    返回:
    无。
    """
    vectorstore.drop_tables()

def upload_files_to_vector(vectorstore:PGVector, files_path: List[str], chunk_size: int = 256, encoding: str = 'utf-8'):
    """
    将文件上传到向量存储库。

    参数:
    vectorstore: PGVector 向量存储实例。
    files_path (List[str]): 要上传的文件路径列表。
    chunk_size (int, 可选): 文件分块大小，默认为 256。
    encoding (str, 可选): 文件编码格式，默认为 'utf-8'。

    返回:
    无。
    """
    t1 = time.time()
    docs = split_files(files_path=files_path, chunk_size=chunk_size, encoding=encoding)
    if len(docs) >=1:
        vectorstore.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])
    print('当前数据入库完毕 : ', time.time() - t1)

def search_vector(vectorstore:PGVector, keywords: Union[List[str],str], k: int = 4):

    """
    在向量存储库中搜索相似文档。

    参数:
    vectorstore: PGVector 向量存储实例。
    keywords (str): 查询字符串。
    k (int, 可选): 返回相似文档的数量，默认为 4。

    返回:
    similar_docs: 相似文档列表。
    """
    data = []
    if isinstance(keywords, str):
        results = vectorstore.similarity_search(keywords, k=k)

        for result in results:
            data.append(result.page_content)
        data = {keywords: list(set(data))}
    elif isinstance(keywords, list):
        data = []
        for keyword in keywords:
            results = vectorstore.similarity_search(keyword, k=k)
            data_values =  [item for d in data for sublist in d.values() for item in sublist]
            results = [item for item in results if item not in data_values]
            data.append({keyword: list(set([i.page_content for i in results]))})

    return data