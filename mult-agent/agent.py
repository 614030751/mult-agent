from google.adk.agents import LlmAgent,BaseAgent, SequentialAgent,ParallelAgent,LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator

gretter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
task_doer=BaseAgent(name="TaskExcutor")

root_agent = LlmAgent(
    name="Coordinator",
    model="gemini-2.5-flash",
    description="你是瞿志豪的讲解代码的助手",
    sub_agents=[
        gretter,
        task_doer
    ]
)
