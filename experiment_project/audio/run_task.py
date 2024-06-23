from experiment_project.agents.crewai_module.run_task import run_crewai
from experiment_project.utils.files.read import read_yaml

config = read_yaml('ecommerce_agent_new.yml')
result = run_crewai(crewai_config=config)
print(result)