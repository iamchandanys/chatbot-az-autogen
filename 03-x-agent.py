import asyncio
import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from dotenv import load_dotenv
from system_prompts import claim_agent_system_message, product_agent_system_message, policy_agent_system_message, summary_agent_system_message
from typing import Any, Mapping
from system_tools import validate_policy_number, search_product_details, get_policy_details

load_dotenv()

API_KEY = os.getenv("api_key")
deployment_name = os.getenv("deployment_name")
Model_Name = os.getenv("model_name")
Api_Version = os.getenv("api_version")
Azure_Endpoint = os.getenv("azure_endpoint")

model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=deployment_name,
        model=Model_Name,
        api_version=Api_Version,
        azure_endpoint=Azure_Endpoint,
        api_key=API_KEY
    )

async def main(user_message: str, agent_state_disk: Mapping[str, Any] | None) -> dict[str, Any]:
    product_agent = AssistantAgent(
        "Product_Agent",
        model_client,
        system_message=f"{product_agent_system_message}",
        tools=[search_product_details]
    )
    
    policy_agent = AssistantAgent(
        "Policy_Agent",
        model_client,
        system_message=f"{policy_agent_system_message}",
        tools=[get_policy_details]
    )
    
    claim_agent = AssistantAgent(
        "Claim_Agent",
        model_client,
        system_message=f"{claim_agent_system_message}",
        tools=[validate_policy_number]
    )
    
    summary_agent = AssistantAgent(
        "Summary_Agent",
        model_client,
        system_message=f"{summary_agent_system_message}",
    )
    
    team = RoundRobinGroupChat(
        participants=[product_agent, policy_agent, claim_agent, summary_agent],
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=4
    )
    
    # Load the agent state
    if agent_state_disk is not None:
        await team.load_state(agent_state_disk)
    
    # Run the team
    result  = await Console(team.run_stream(task=user_message))
    # result  = await team.run(task=user_message)
    
    # Agent state
    agent_state = await team.save_state()
    
    # Return the agent state and the response
    return {
        "agent_state": agent_state,
        "response": result.messages[-1].content
    }

async def chat():
    agent_state_disk = None
    
    for _ in range(100):
        user_input = input("User: ")
        if "stop" in user_input: break
        result = await main(user_input, agent_state_disk)
        agent_state_disk = result["agent_state"]
        print(f"Agent: {result['response']}")
    
asyncio.run(chat())