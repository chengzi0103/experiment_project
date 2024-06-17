from experiment_project.agents.crewai_module.base_module import create_agent, create_task, setup_crew
from experiment_project.agents.crewai_module.util import set_api_keys, make_crewai_tool
from experiment_project.agents.tools.tool_mapping import tool_mapping, agent_tools
from experiment_project.utils.files.read import read_yaml
from experiment_project.utils.initial.util import init_sys_env

# config = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/moxin/crewai/agent_config.yml')
def run_crewai(crewai_config:dict):
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
    )
    result = crew.kickoff()
    return result