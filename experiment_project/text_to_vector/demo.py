# import huggingface_hub
# import torch.nn.functional as F
# from torch import Tensor
# import torch
# from transformers import AutoTokenizer, AutoModel
# import os
#
# from experiment_project.utils.files.split import split_txt_by_langchain
#
# input_texts = [
#     "中国的首都是哪里",
#     "你喜欢去哪里旅游",
#     "北京",
#     "我爱北京天安门"
# ]
#
# from huggingface_hub import snapshot_download
# import os
#
# # os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 设置为hf的国内镜像网站
# # huggingface_hub.login('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')
# # snapshot_download(repo_id='maidalun1020/bce-embedding-base_v1',
# #                   repo_type='model',
# #                   local_dir='/home/cc/Work/Model',
# #                   local_dir_use_symlinks=False,  # 在local-dir指定的目录中都是一些“链接文件”
# #                   resume_download=True,
# #                   proxies={"http": "http://198.168.31.10:10809","https": "http://198.168.31.10:10809"}
# #                   )
#
#
# #
# # tokenizer = AutoTokenizer.from_pretrained("/mnt/d/models/embeddings/bce-embedding-base_v1")
# # model = AutoModel.from_pretrained("/mnt/d/models/embeddings/bce-embedding-base_v1",device_map='auto')
# # device = 'cuda:0'  # if no GPU, set "cpu"
# # model.to(device)
# # # Tokenize the input texts
# # batch_dict = tokenizer(input_texts, max_length=2048, padding=True, truncation=True, return_tensors='pt')
# # batch_dict = {k: v.to(device) for k, v in batch_dict.items()}
# #
# # outputs = model(**batch_dict)
# # embeddings = outputs.last_hidden_state[:, 0]
# #
# # # (Optionally) normalize embeddings
# # embeddings = F.normalize(embeddings, p=2, dim=1)
# # scores = (embeddings[:1] @ embeddings[1:].T) * 100
# # print(scores.tolist())
# #
# #
# #
# #
# #
# # embeddings = F.normalize(embeddings, p=2, dim=1)
# #
# # # Get the index of "北京"
# # beijing_index = input_texts.index("北京")
# #
# # # Calculate similarity scores between "北京" and other texts
# # beijing_embedding = embeddings[beijing_index].unsqueeze(0)
# # other_embeddings = torch.cat([embeddings[:beijing_index], embeddings[beijing_index+1:]], dim=0)
# #
# # # Calculate similarity scores
# # scores = (beijing_embedding @ other_embeddings.T) * 100
# # scores_list = scores.tolist()[0]  # Convert to a list
# #
# # # Display results
# # for i, score in enumerate(scores_list):
# #     if i < beijing_index:
# #         compared_text = input_texts[i]
# #     else:
# #         compared_text = input_texts[i + 1]
# #     print(f"北京与'{compared_text}'的相似度得分: {score:.2f}")
# #
# #
#
#
#
#
# from langchain.embeddings import HuggingFaceEmbeddings
#
# # Path to your local model
# local_model_path = "/mnt/d/models/embeddings/bce-embedding-base_v1"
#
# # Instantiate the HuggingFaceEmbeddings class
# embedding = HuggingFaceEmbeddings(model_name=local_model_path,model_kwargs={'device':0},multi_process=True,show_progress=True)
#
# # Use the embedding instance
# # output = embedding.embed_documents(input_texts)
# # embedded_query = embedding.embed_query("我喜欢哪里?")
#
# from langchain_cohere import CohereEmbeddings
# from langchain_core.documents import Document
# from langchain_postgres import PGVector
# from langchain_postgres.vectorstores import PGVector
# connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!
# collection_name = "my_docs"
#
# vectorstore = PGVector(
#     embeddings=embedding,
#     collection_name=collection_name,
#     connection=connection,
#     use_jsonb=True,
# )
# data = split_txt_by_langchain(chuck_size=256,file_path='/mnt/d/project/zzbc/experiment_project/experiment_project/text_to_vector/xiaoaojianghu_jinyong.txt')
# docs_data = [Document(page_content=text,metadata={"id": num+1,'chunk_index':num,'chunk_size':len(text)}) for num,text in enumerate(data)]
# # vectorstore.drop_tables()
#
#
# vectorstore.add_documents(docs_data, ids=[doc.metadata["id"] for doc in docs_data])
# vectorstore.similarity_search("笑傲江湖讲的是的什么?",k=8)