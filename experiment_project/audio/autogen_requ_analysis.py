import pandas as pd
from autogen.agentchat import UserProxyAgent, AssistantAgent, register_function

from experiment_project.utils.initial.util import init_sys_env


init_sys_env(is_proxy=True,proxy_url='http://192.168.31.215:10890')
def read_excel(file_path:str, sheet_names:list[str]=None)->list[dict]:
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
        sheets_data.append({sheet_name: sheet_df.to_dict(orient='records')})

    return sheets_data
user_proxy = UserProxyAgent(name='user', system_message='用户',
                            code_execution_config={"work_dir": "。",
                                                   "use_docker": False},llm_config=None,)
task_proxy = AssistantAgent(name='音箱系统任务需求分析师', system_message="""
C — 上下文（Context）
        目标概述：深入分析用户需求，匹配和推荐合适的产品方案。
        背景资料：分析ezCloud.xlsx和配单练习.xlsx中的数据和案例。符合xlsx中的方案,产品要齐全
        任务分析逻辑：
          - 当你拿到任务的时候,可以先分析任务里面的内容,先产看任务的房间数量.如果没有房间数量,则可以对用户进行询问,房间数量是多少个？
          - 再查看任务描述中的房间类型.如果没给到房间类型,则可以根据人数以及ezCloud.xlsx中的sheet的'配置方案建议'的内容去推断房间类型是什么？如果还是不能推断出来,则应该询问用户
          - 获取到房间数量以及类型之后,你可以根据任务的需求，例如是否需要预约等条件。根据ezCloud.xlsx中的sheet的'模板说明'，找到最相近的一个方案。
          - 如果没有找到最相近的方案，你可以去配置方案建议里面,根据房间类型和房间大小找到一个房间需要的产品.然后再结合不同类型的方案中需要的不同产品,生成一个完整的需求方案
          - 当你生成这个方案的之后,你需要去'配单练习.xlsx'去对比,看看你生成的方案和案例方案差距大不大？如果方案差距产品很大,你就需要按照之前的逻辑重新思考一遍,再重新生成一个方案。如果差距不大,则完成方案的需求分析
        数据文件参数:
          [{
            'file_path': './data/audio_data/ezCloud.xlsx',
            'sheet_names': None},
          {'file_path': './data/audio_data/配单练习.xlsx', 'sheet_names': None}]
        数据文件的含义:
          ezCloud.xlsx: 
            - '模板说明' 表中的 '方案名称' 表明，根据任务需求和条件,你可以到这个里面的找到一个与任务最相近的配置方案.如果其他列的条件（如 '适配房间数' 或 'ezCloud版本'）符合，那么对应的方案名称就是表的名称。
            - '配置方案建议'：它是单个房间的根据不同的房间类型/大小等对单个房间的产品的推荐.根据条件选择对应的产品，并检查是否可以推荐。如果条件符合，可以去 '硬件分控（1间）' 表中找到对应的物料编码和设备名称。
            - '硬件分控（1间）'：它是单个房间需要的产品,包括名称,型号等.可以作为一个最小房间的参考
          配单练习.xlsx:
            - '配单练习'：真实的任务需求和根据任务需求得到的产品。
            - '配置检查表'：分析任务需求后进行的检查。

      O — 输出格式（Output Format）
        
      T — 任务示例（Task Example）
        项目示例：
          项目需求：预约+集控+中控（16间）5个楼层需要会议指引功能，控制屏甲供，有电子桌牌需求，定制开发项包含：OA流程审批对接、用户及组织架构自动同步、企业级统一用户认证登录、第三方消息通知集成、会议室/会议信息自动同步、人脸库集成、工卡卡号集成、群组同。
          项目结果： 
          1. **中控控制屏**：
             - 4寸墙面智慧语音触摸控制屏（型号CTS-401NVW）：8台
             - 10.1寸桌面控制触摸屏（型号CTS1050NWP）：12台
          2. **分布式控制器软件V2.0**（品牌ezCloud）：16套
          3. **分布式控制器现场实施**（定制服务）：8套
          4. **8路大电流继电器**（型号CS B-REL0820）：13个
          5. **4路导轨式调光模块**（型号CS B-DIM0420）：13个
          6. **导轨式级联模块**（型号CS B-NETCOM-EZ-DIN）：13个
          7. **串转网服务器**（型号N668）：0台（具体数量根据会议室情况而定）
          8. **网口转换端子**（公头和母头，品牌纬诺希尔）：0个（具体数量根据会议室情况而定）
          9. **控制交换机**（品牌HUAWEI，型号S5720-28P-PWR-LI-AC）：12台
          10. **智能物联控制系统V2.0**（品牌ezCloud）：13套
          11. **会议集控专用服务主机**（品牌IPS，型号MT100）：1台
          12. **虚拟智能分布式控制器**（品牌IPS，型号DP120E）：1台
          13. **网络交换机**（品牌HUAWEI，型号S5720-28P-PWR-LI-AC）：1台
          14. **水墨屏电子桌牌**（品牌IPS，型号CTS753M）：20套
          15. **RS232转红外模块**（品牌浩博，型号HB_STR-RFK（存储型））：12个
          16. **红外线发射棒**：12个
          17. **CS传感器系列**：12个（具体型号未提供，可能与红外设备相关）
          18. **光照度感应器**（品牌IPS，型号CS B-LUM-SEN）：12个
          19. **10.1寸智慧信息屏（双目款）**（型号CTS-1003NWCP）：12台
          20. **人脸识别SDK应用**（品牌ezCloud，型号SWA90001）：12套
          21. **15.6寸智慧信息屏（智慧款）**（型号CTS1501NWCP）：5台
          22. **智慧会议指引屏软件**（品牌ezCloud，型号V2.0）：5套
          请注意，某些项目的数量可能需要根据实际的会议室布局和具体需求进行调整。例如，串转网服务器和网口转换端子的数量在文档中提到是“0”，并注明具体数量根据会议室情况而定，这意味着它们可能需要根据实际的安装和配置需求来确定。
      A — 附加信息（Additional Information）
        用户偏好：用户的特定偏好或品牌要求。

      R — 限制（Restriction）
        时间限制：方案设计和实施需在用户要求的时间内完成。
        技术限制：方案需满足用户的技术规范和兼容性要求
""",llm_config=llm_config, human_input_mode='NEVER',)
# task_proxy.register_for_llm(name='read_excel',
#                            description=" Read all sheets or specified sheets from an Excel file and generate a list containing dictionaries.Parameters:file_path (str): The path to the Excel file. sheet_names (list, optional): A list of the names of the sheets to be read. If not provided, all sheets will be read. Returns: list: A list of dictionaries containing the data of each sheet, where each dictionary's key is the name of the sheet and the value is the content of that sheet (DataFrame).")(read_excel)
# user_proxy.register_for_execution(name='read_excel')(read_excel)
register_function(
    read_excel,
    caller=task_proxy,  # The assistant agent can suggest calls to the calculator.
    executor=user_proxy,  # The user proxy agent can execute the calculator calls.
    name="read_excel",  # By default, the function name is used as the tool name.
    description="Read all sheets or specified sheets from an Excel file and generate a list containing dictionaries.Parameters:file_path (str): The path to the Excel file. sheet_names (list, optional): A list of the names of the sheets to be read. If not provided, all sheets will be read. Returns: list: A list of dictionaries containing the data of each sheet, where each dictionary's key is the name of the sheet and the value is the content of that sheet (DataFrame).",  # A description of the tool.
)


user_proxy.initiate_chat(task_proxy,message='任务需求: 项目需求：仅集控+虚拟中控，18间会议室,大会议室10间,小会议室8间.中控需求：电动窗帘、灯光回路、投影机、投影幕可监控 无需人体感应及环境数据监测',summary_method="reflection_with_llm",max_turns=20,clear_history=False)