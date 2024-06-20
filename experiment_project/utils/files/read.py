import pandas as pd
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




def read_excel(file_path:str, sheet_names:list[str]=None):
    """
    读取Excel文件中的所有sheet或者指定的sheet，并生成一个包含字典的列表。

    参数:
    file_path (str): Excel文件的路径。
    sheet_names (list, optional): 要读取的sheet名称列表。如果未提供，将读取所有sheet。

    返回:
    list: 包含每个sheet数据的字典的列表，每个字典的key是sheet的名称，value是该sheet的内容(DataFrame)。
    """
    # 读取所有的sheet名称
    xls = pd.ExcelFile(file_path)
    all_sheet_names = xls.sheet_names

    # 如果未提供sheet_names，则读取所有sheet
    if sheet_names is None:
        sheet_names = all_sheet_names

    # 检查提供的sheet_names是否在文件中存在
    invalid_sheets = [sheet for sheet in sheet_names if sheet not in all_sheet_names]
    if invalid_sheets:
        raise ValueError(f"The following sheets are not found in the Excel file: {', '.join(invalid_sheets)}")

    # 初始化结果列表
    sheets_data = []

    # 读取每个指定的sheet并存入字典
    for sheet_name in sheet_names:
        sheet_df = pd.read_excel(file_path, sheet_name=sheet_name)
        sheets_data.append({sheet_name: sheet_df})

    return sheets_data