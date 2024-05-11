import yaml
def read_yaml(file_path:str):
    with open(file_path, 'r') as file:
        prime_service = yaml.safe_load(file)
    return prime_service