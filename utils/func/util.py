import importlib
import inspect
import os


def load_functions_from_directory(directory_path):
    functions_dict = {}

    # 遍历指定目录下的所有文件
    for file in os.listdir(directory_path):
        if file.endswith('.py') and not file.startswith('__'):
            # 构建模块名和文件路径
            module_name = file[:-3]  # 移除.py后缀
            file_path = os.path.join(directory_path, file)

            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 获取模块中的所有函数
            functions_list = inspect.getmembers(module, inspect.isfunction)

            # 将函数添加到字典中
            for func_name, func in functions_list:
                key = f"{module_name}_{func_name}"
                functions_dict[key] = func

    return functions_dict
