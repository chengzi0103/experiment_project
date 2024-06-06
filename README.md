# 1, 文档代码说明

所有的代码和文档,全部都在 experiment_project/delivery


## 2, 项目安装使用教程
- git clone 此项目
- 切换你的环境,保证你的环境是python3.10.12的版本
    - 如果出现环境版本不对称,请使用conda重新安装此环境  
  ```shell
     conda create -n  py310 python=3.10.12 -y 
- 安装依赖
```shell
pip3 install -r requirements.txt && pip3 install -e . 
```


## 3, Text文件使用大语言模型入库到Neo4j中

### 3.1 项目配置
**配置地址**： experiment_project/configs

### 3.2 项目配置说明
大语言模型配置说明：/configs/model/openai.yaml
- **model_api_key**: openai模型api密钥
- **model_name**: openai模型名称
- **model_max_tokens**: 模型最大值


neo4j配置说明：/configs/neo4j/default.yaml
- **neo4j_uri**: neo4j的url 例如 (bolt://localhost:7687)
- **neo4j_user_name**: neo4j用户名
- **neo4j_password**: neo4j密码

text_to_kg配置说明：/configs/project/text_to_kg.yaml
- **file_path**: 要读取的文本文件路径(暂时只支持txt文件)
- **entitie_optimized_file_path**: dspy的ntitie_optimized的文件路径,如果没有,填为null(空)
- **proxy_url**: 是否使用vpn代理链接
- **encoding**: 使用那种encoding方式读取text文件
- **chunk_size**: text文件拆分的块大小,推荐不要过大,否则

### 3.3 启动任务 
python3 text_to_kg.py


### 3.4 当前还有哪些Bug没有修复
- [ ] : 当前只支持openai的模型,后续会支持其他模型的使用
- [ ] : 目前只支持txt文件的读取,后续会支持其他文件的读取
- [ ] : 目前只支持单个文件读取,后续会支持多个文件的读取
- [ ] ： 目前不支持使用dspy来训练prompt,后续会支持
- [ ] ： 目前单文件到知识图谱过慢,后面会支持到多文件