import huggingface_hub
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
import os
input_texts = [
    "中国的首都是哪里",
    "你喜欢去哪里旅游",
    "北京",
    "今天中午吃什么"
]

from huggingface_hub import snapshot_download
import os

# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 设置为hf的国内镜像网站
# huggingface_hub.login('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')
# snapshot_download(repo_id='maidalun1020/bce-embedding-base_v1',
#                   repo_type='model',
#                   local_dir='/home/cc/Work/Model',
#                   local_dir_use_symlinks=False,  # 在local-dir指定的目录中都是一些“链接文件”
#                   resume_download=True,
#                   proxies={"http": "http://198.168.31.10:10809","https": "http://198.168.31.10:10809"}
#                   )



tokenizer = AutoTokenizer.from_pretrained("/home/cc/Work/WorkSpace/model/bce-embedding-base_v1")
model = AutoModel.from_pretrained("/home/cc/Work/WorkSpace/model/bce-embedding-base_v1",device_map='auto')
device = 'cuda:0'  # if no GPU, set "cpu"
model.to(device)
# Tokenize the input texts
batch_dict = tokenizer(input_texts, max_length=2048, padding=True, truncation=True, return_tensors='pt')

outputs = model(**batch_dict)
embeddings = outputs.last_hidden_state[:, 0]

# (Optionally) normalize embeddings
embeddings = F.normalize(embeddings, p=2, dim=1)
scores = (embeddings[:1] @ embeddings[1:].T) * 100
print(scores.tolist())
