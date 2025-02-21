from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("api_key")
deployment_name = os.getenv("deployment_name")
Model_Name = os.getenv("model_name")
Api_Version = os.getenv("api_version")
Azure_Endpoint = os.getenv("azure_endpoint")

az_openai_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=deployment_name,
    model=Model_Name,
    api_version=Api_Version,
    azure_endpoint=Azure_Endpoint,
    api_key=API_KEY
)

assistant_agent_guider = AssistantAgent(
    name="assistant_agent_guider",
    description="An agent for guiding other agents based on user's input. This agent should be the first to engage when given a new task.",
    model_client=az_openai_model_client,
    system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
        Story_writer: Writes story and make corrections.
        Story_reviewer: Checks if the story is for kids and Provides constructive feedback on Kids stories to add a positive impactful ending. It doesn't write the story, only provide feedback and improvements.
        Story_moral: Finally, adds the moral to the story.

    You only plan and delegate tasks - you do not execute them yourself. You can engage team members multiple times so that a perfect story is provided.

    When assigning tasks, use this format:
    1. <agent> : <task>

    After all tasks are complete, summarize the findings and end with "TERMINATE".
    """,
)