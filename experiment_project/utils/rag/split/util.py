from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader

from experiment_project.utils.files.split import split_txt_by_langchain

from langchain_core.documents import Document
def split_files(files_path: List[str], chunk_size: int = 256, encoding: str = 'utf-8'):
    """
    将给定文件路径列表中的文件按块大小分割，并返回包含分割文本的文档列表。

    参数:
    files_path (List[str]): 文件路径的列表。
    chunk_size (int, 可选): 每个文本块的大小，默认为 256。
    encoding (str, 可选): 文件的编码格式，默认为 'utf-8'。

    返回:
    all_data (List[Document]): 包含分割后文本块的文档列表，每个文档包括文本内容和元数据。
    """
    all_data = []
    id_num = 0
    for num, file_path in enumerate(files_path):
        file_path = Path(file_path)
        if file_path.is_file():
            file_extension = file_path.suffix
            if file_extension == '.txt':
                data = split_txt_by_langchain(chunk_size=chunk_size, file_path=str(file_path), encoding=encoding)
                if len(data) > 0:
                    for num, text in enumerate(data):
                        id_num += 1
                        doc = Document(page_content=text,
                                       metadata={"id": id_num, 'chunk_index': num, 'chunk_size': len(text),
                                                 'source': file_path})
                        all_data.append(doc)
            elif file_extension == '.pdf':
                loader = PyPDFLoader(str(file_path))
                pages = loader.load_and_split()
                for doc in pages:
                    id_num += 1
                    doc.metadata['id'] = id_num
                    all_data.append(doc)
    return all_data
