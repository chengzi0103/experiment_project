import agentops


def init_agentops(agentops_api_key:str=None):
    if agentops_api_key is not None:
        agentops.init(agentops_api_key)
    else:
        agentops.init()