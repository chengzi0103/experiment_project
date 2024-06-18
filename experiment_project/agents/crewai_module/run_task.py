import os

from experiment_project.agents.crewai_module.base_module import create_agent, create_task, setup_crew
from experiment_project.agents.crewai_module.util import set_api_keys, make_crewai_tool
from experiment_project.agents.tools.tool_mapping import tool_mapping, agent_tools
from experiment_project.utils.initial.util import init_sys_env

# config = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/moxin/crewai/agent_config.yml')
def run_crewai(crewai_config:dict):
    print(crewai_config)
    if crewai_config.get('env',None) is not None:
        for env_name,env_value in crewai_config['env'].items():
            os.environ[env_name] = env_value
    model_config,agents_config,tasks_config,other_config = crewai_config.get('model'),crewai_config.get('agents'),crewai_config.get('tasks'),crewai_config.get('other')
    proxy_url=other_config.get('proxy_url',None)
    if proxy_url is not None:
        init_sys_env(is_proxy=True,proxy_url=proxy_url)
    set_api_keys(**model_config)
    agents = {}
    for agent_config in crewai_config['agents']:
        tool_names = agent_config.get('tools',None)
        tools = agent_tools(tool_names=tool_names)
        agent = create_agent(
                    role=agent_config['role'],
                    goal=agent_config['goal'],
                    backstory=agent_config['backstory'],
                    verbose=agent_config['verbose'],
                    allow_delegation=agent_config['allow_delegation'],
                    tools=[make_crewai_tool(func)  for func in tools],
                )
        agents[agent_config['name']] = agent

    tasks = []
    for task_config in crewai_config['tasks']:
        task = create_task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent= agents.get(task_config.get('agent')),
        max_inter=task_config['max_inter'],
        )
        tasks.append(task)

    crew = setup_crew(
        agents=list(agents.values()),
        tasks=tasks,
        memory=crewai_config.get('crewai_config').get('memory',None)
    )
    result = crew.kickoff()
    return result
# result = run_crewai({'agents': [{'name': 'stock_data_collector', 'role': 'Stock Data Collector', 'goal': 'Collect and organize stock data for specified companies', 'backstory': 'You are an experienced data collector specializing in extracting valuable stock data from various online sources.\n', 'verbose': True, 'allow_delegation': False, 'tools': ['DuckDuckGoSearchRun', 'now_time','stock_data']}, {'name': 'stock_analyst', 'role': 'Stock Analyst', 'goal': 'Analyze collected stock data and provide insights', 'backstory': 'You are a seasoned stock analyst skilled in interpreting stock market data, identifying market trends, and providing investment advice.\n', 'verbose': True, 'allow_delegation': False, 'tools': ['DuckDuckGoSearchRun', 'now_time','stock_data']}, {'name': 'investment_advisor', 'role': 'Investment Advisor', 'goal': 'Provide clear investment recommendations based on analysis', 'backstory': 'You are an experienced investment advisor focused on offering investment strategies and advice to clients.\n', 'verbose': True, 'allow_delegation': True, 'tools': ['DuckDuckGoSearchRun', 'now_time','stock_data']}], 'tasks': [{'description': 'First get the current time, Collect the latest stock data for NVIDIA and Tesla from the beginning of this year to the present, including prices, volumes, and market trends.', 'expected_output': 'Report containing all relevant collected data', 'agent': 'stock_data_collector', 'max_inter': None}, {'description': 'Analyze the collected stock data for NVIDIA and Tesla. Evaluate market trends, financial performance, and potential risks.\n', 'expected_output': 'Detailed analysis report', 'agent': 'stock_analyst', 'max_inter': None}, {'description': 'Based on the analysis reports, provide clear recommendations on whether to invest in NVIDIA and Tesla.\n', 'expected_output': 'Investment recommendation report', 'agent': 'investment_advisor', 'max_inter': None}], 'model': {'model_api_key': '', 'model_name': 'gpt-4', 'model_max_tokens': 2048, 'module_api_url': None}, 'other': {'proxy_url': 'http://192.168.0.75:10809'}, 'env': {'SERPER_API_KEY': '2e4d9ef16c251219c58cb2b04509d626e43b09c1'}, 'crewai_config': {'memory': True}})
# print(result)