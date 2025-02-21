import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("api_key")
deployment_name = os.getenv("deployment_name")
Model_Name = os.getenv("model_name")
Api_Version = os.getenv("api_version")
Azure_Endpoint = os.getenv("azure_endpoint")

az_model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=deployment_name,
        model=Model_Name,
        api_version=Api_Version,
        azure_endpoint=Azure_Endpoint,
        api_key=API_KEY
    )

# A simpl agent that uses the Azure OpenAI client to answer a question

async def simple_agent() -> None:
    agent = AssistantAgent("assistant", az_model_client)
    print(await agent.run(task="Who is virat kohli"))

# A team of agents that includes an assistant agent and a web surfer agent

async def team_of_agents() -> None:
    # Create an assistant agent using the Azure OpenAI client
    assistant = AssistantAgent("assistant", az_model_client)  
    # Create a web surfer agent using the Azure OpenAI client
    web_surfer = MultimodalWebSurfer("web_surfer", az_model_client)  
    # Create a user proxy agent
    user_proxy = UserProxyAgent("user_proxy")
    # Define a termination condition that ends the conversation when 'exit' is mentioned  
    termination = TextMentionTermination("exit") 
    # Create a round-robin group chat with the agents and the termination condition 
    team = RoundRobinGroupChat([web_surfer, assistant, user_proxy], termination_condition=termination)  
    # Run the team of agents with the specified task and display the conversation in the console
    await Console(team.run_stream(task="Explain moratorium period in health insurance. Give the result WRT india."))  

asyncio.run(team_of_agents())