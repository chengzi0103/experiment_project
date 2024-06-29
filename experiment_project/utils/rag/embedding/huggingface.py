from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_openai import OpenAIEmbeddings
def load_embedding_model(module_path:str=None,model_name:str=None,multi_process:bool=False,model_kwargs:dict={'device':0}):
    """
        加载嵌入模型，根据提供的路径或模型名称选择不同的嵌入实现。
        参数:
        module_path (str, 可选): HuggingFace模型的路径。
        model_name (str, 可选): OpenAI模型的名称。
        multi_process (bool, 可选): 是否启用多进程，默认为False。
        model_kwargs (dict, 可选): 模型初始化的其他参数，默认为{'device': 0}，指定设备。
        返回:
        embedding: 加载的嵌入模型实例，基于提供的参数选择HuggingFace或OpenAI的实现。
    """
    embedding = None
    if module_path is not None:
        embedding = HuggingFaceEmbeddings(model_name=module_path, model_kwargs=model_kwargs, show_progress=True,multi_process=multi_process)
    # elif model_name is not None and module_path is None:
    #     embedding = OpenAIEmbeddings(model_name=model_name)
    return embedding

