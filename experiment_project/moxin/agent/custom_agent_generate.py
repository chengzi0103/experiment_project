from experiment_project.utils.files.read import read_yaml

custom_agent_config = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/moxin/agent/custom_agent_config.yml')

agent_task,agent_config,agent_list = custom_agent_config.get('CUSTOM-AGENT').get('TASK'),custom_agent_config.get('MODEL'),custom_agent_config.get('CUSTOM-AGENT').get('AGENT_LIST')


loader_cofnig = read_yaml('/mnt/d/project/zzbc/experiment_project/experiment_project/moxin/agent/loader_config.yml')
