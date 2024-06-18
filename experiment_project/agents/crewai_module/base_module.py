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

def create_task(description: str, agent: Agent, expected_output: str=None,max_inter:int=None) -> Task:
    if expected_output is None:
        expected_output = ''

    task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        human_input=False, # dora-input is not supported yet
        max_inter=max_inter
    )
    return task

def setup_crew(agents: List[Agent], tasks: List[Task], verbose: int=2,process:str=None,memory:bool=False) -> Crew:
    if process is None:
        process = Process.sequential

    return Crew(
        agents=agents,
        tasks=tasks,
        verbose=verbose,
        process=process,memory=memory
    )

def kickoff_crew(crew: Crew):
    return crew.kickoff()