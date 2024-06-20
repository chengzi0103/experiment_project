import os

from experiment_project.agents.crewai_module.base_module import create_agent, create_task, setup_crew
from experiment_project.agents.crewai_module.util import set_api_keys, make_crewai_tool
from experiment_project.agents.tools.tool_mapping import  agent_tools
from experiment_project.utils.files.read import read_yaml
from experiment_project.utils.initial.util import init_sys_env
import agentops

def run_crewai(crewai_config:dict):


    if crewai_config.get('env',None) is not None:
        for env_name,env_value in crewai_config['env'].items():
            os.environ[env_name] = env_value

    agentops.init()
    model_config,agents_config,tasks_config,other_config = crewai_config.get('model'),crewai_config.get('agents'),crewai_config.get('tasks'),crewai_config.get('other')
    proxy_url=other_config.get('proxy_url',None)
    if proxy_url is not None:
        init_sys_env(is_proxy=True,proxy_url=proxy_url)
    set_api_keys(**model_config)
    agents = {}
    for agent_config in crewai_config['agents']:
        tool_names = agent_config.get('tools',None)
        tools = agent_tools(tool_names=tool_names)
        all_tools = []
        for func in tools:
            try:
                all_tools.append(make_crewai_tool(func))
            except Exception as e :
                all_tools.append(func)
        agent = create_agent(
                    role=agent_config['role'],
                    goal=agent_config['goal'],
                    backstory=agent_config['backstory'],
                    verbose=agent_config['verbose'],
                    allow_delegation=agent_config['allow_delegation'],

                    tools=all_tools,
                )
        agents[agent_config['name']] = agent

    tasks = []
    for task_config in crewai_config['tasks']:

        task = create_task(
            description=task_config['description'],
            expected_output=task_config['expected_output'],
            agent= agents.get(task_config.get('agent')),
            max_inter=task_config['max_inter'],
            human_input = task_config['human_input'],
        )
        tasks.append(task)

    crew = setup_crew(
        agents=list(agents.values()),
        tasks=tasks,
        memory=crewai_config.get('crewai_config').get('memory',None),
        process = crewai_config.get('crewai_config').get('process',None),
        manager_agent= agents.get(crewai_config.get('crewai_config').get('manager_agent',None))
    )
    result = crew.kickoff()
    return result

config = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/audio/ecommerce_agent.yml')
result = run_crewai(crewai_config=config)