import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from typing import List

def create_agent(role: str, goal: str, backstory: str, verbose: bool=True, allow_delegation: bool=False, tools: List = None,) -> Agent:
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        verbose=verbose,
        allow_delegation=allow_delegation,
        tools=tools,
    )

def create_task(description: str, expected_output: str, agent: Agent,max_inter:int=1) -> Task:
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        human_input=False,
    max_inter=max_inter

    )

def setup_crew(agents: List[Agent], tasks: List[Task], verbose: int=2) -> Crew:
    return Crew(
        agents=agents,
        tasks=tasks,
        verbose=verbose
    )

def kickoff_crew(crew: Crew):
    return crew.kickoff()