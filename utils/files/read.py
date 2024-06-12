import yaml
def read_yaml(file_path:str):
    with open(file_path, 'r') as file:
        prime_service = yaml.safe_load(file)
    return prime_service

def read_text(file_path: str = '/mnt/d/project/dy/extra/nlp/uie/三体1疯狂年代.txt',encoding:str='utf-8') -> str:
    content = ""
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    return content
