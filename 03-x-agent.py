import asyncio
import os
from typing import Sequence
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat, RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.ui import Console
from dotenv import load_dotenv
from system_prompts import claim_agent_system_message
from typing import Any, Mapping
from system_tools import validate_policy_number

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
    primary_agent = AssistantAgent(
        "Primary_Agent",
        model_client,
        description="Helps users to get insurance product details, policy details, and claim details.",
        system_message="""
        You are the primary agent.
        Based on the users input, you will be responsible for delegating the task to the appropriate agent.
        Your team members are:
            Product_Agent: Helps users to get insurance product details.
            Policy_Agent: Helps users to get their policy details.
            Claim_Agent: Helps users to get their claim details.
        
        When assigning tasks, use this format:
        1. <agent> : <task>
        
        After all tasks are complete, summarize the findings and end with "TERMINATE".
        """
    )
    
    product_agent = AssistantAgent(
        "Product_Agent",
        model_client,
        system_message="You are a product agent. You help users to get insurance product details."
    )
    
    policy_agent = AssistantAgent(
        "Policy_Agent",
        model_client,
        system_message="You are a policy agent. You help users to get their policy details."
    )
    
    claim_agent = AssistantAgent(
        "Claim_Agent",
        model_client,
        tools=[validate_policy_number],
        system_message=f"{claim_agent_system_message}"
    )
    
    def selector_func(messages: Sequence[AgentEvent | ChatMessage]) -> str | None:
        user_input = messages[-1].content
        if "product" in user_input:
            return "Product_Agent"
        elif "policy" in user_input:
            return "Policy_Agent"
        elif "claim" in user_input:
            return "Claim_Agent"
    
    # Create a team of agents
    # team = SelectorGroupChat(
    #     [claim_agent, product_agent, policy_agent],
    #     model_client=model_client,
    #     selector_func=None,
    #     termination_condition=TextMentionTermination("TERMINATE"),
    #     max_turns=1
    # )
    
    team = RoundRobinGroupChat(
        participants=[primary_agent, claim_agent, product_agent, policy_agent],
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=10
    )
    
    # Load the agent state
    if agent_state_disk is not None:
        await team.load_state(agent_state_disk)
    
    # Run the team
    result  = await Console(team.run_stream(task=user_message))
    
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