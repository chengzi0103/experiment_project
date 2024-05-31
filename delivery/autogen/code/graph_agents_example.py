from autogen.graph_utils import visualize_speaker_transitions_dict
from autogen import ConversableAgent
#
# agents = [ConversableAgent(name=f"Agent{i}", llm_config=False) for i in range(5)]
# allowed_speaker_transitions_dict = {
#     agents[0]: [agents[1], agents[2], agents[3], agents[4]],
#     agents[1]: [agents[0]],
#     agents[2]: [agents[0]],
#     agents[3]: [agents[0]],
#     agents[4]: [agents[0]],
# }
#
# visualize_speaker_transitions_dict(allowed_speaker_transitions_dict, agents)



speaker_transitions_dict = {}
teams = ["A", "B", "C"]
team_size = 5


def get_agent_of_name(agents, name) -> ConversableAgent:
    for agent in agents:
        if agent.name == name:
            return agent


# Create a list of 15 agents 3 teams x 5 agents
agents = [ConversableAgent(name=f"{team}{i}", llm_config=False) for team in teams for i in range(team_size)]

# Loop through each team and add members and their connections
for team in teams:
    for i in range(team_size):
        member = f"{team}{i}"
        # Connect each member to other members of the same team
        speaker_transitions_dict[get_agent_of_name(agents, member)] = [
            get_agent_of_name(agents, name=f"{team}{j}") for j in range(team_size) if j != i
        ]

# Team leaders connection
print(get_agent_of_name(agents, name="B0"))
speaker_transitions_dict[get_agent_of_name(agents, "A0")].append(get_agent_of_name(agents, name="B0"))
speaker_transitions_dict[get_agent_of_name(agents, "B0")].append(get_agent_of_name(agents, name="C0"))

visualize_speaker_transitions_dict(speaker_transitions_dict, agents)