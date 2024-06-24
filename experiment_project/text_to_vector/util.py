import huggingface_hub
import torch.nn.functional as F
from torch import Tensor
import torch
from transformers import AutoTokenizer, AutoModel
import os

def load_model_and_tokenizer(model_path: str, device: str = "cuda:0"):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path, device_map='auto')
    model.to(device)
    return tokenizer,model



def tokenize_text(text: str,model, tokenizer: AutoTokenizer,max_lengt:int=2048,device:str='cuda:0') -> Tensor:
    batch_dict = tokenizer(text, max_length=max_lengt, padding=True, truncation=True, return_tensors='pt')
    batch_dict = {k: v.to(device) for k, v in batch_dict.items()}

    outputs = model(**batch_dict)
    embeddings = outputs.last_hidden_state[:, 0]
    return embeddings