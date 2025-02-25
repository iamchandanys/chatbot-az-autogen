import asyncio
import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from dotenv import load_dotenv
from system_prompts import claim_agent_system_message, product_agent_system_message, policy_agent_system_message, summary_agent_system_message
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_core.tools import FunctionTool
from typing import Any, Mapping
from system_tools import validate_policy_number, get_info, get_policy_details, get_claim_details, get_policy_documents

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
    """
    reflect_on_tool_use
    - When reflect_on_tool_use is set to True: After the agent calls an external tool and receives its result, it performs an additional inference.
    - This means the agent re-evaluates the tool's output in the context of the original query to generate a more coherent and contextually integrated response.
    - When reflect_on_tool_use is set to False: The agent directly returns the tool's result as the final response without further processing or integration.
    
    memory
    - In Microsoft's AutoGen 0.4, the memory parameter in the AssistantAgent allows the agent to access and utilize external memory stores.
    - This enables the agent to retrieve relevant information based on the current context or user input, enhancing its responses with pertinent data.
    - For instance, when a user asks a question, the agent can query its memory to find related information and incorporate it into its reply. 
    - This functionality is particularly useful for tasks requiring context-aware responses or when implementing retrieval-augmented generation (RAG) workflows.
    """
    
    # Create a memory store for the user
    user_memory = ListMemory()
    # Add user preferences to memory
    await user_memory.add(MemoryContent(content="The user name is chandan.", mime_type=MemoryMimeType.TEXT))
    
    product_agent_tool = FunctionTool(
        get_info,
        name="get_any_info",
        description="To get any information. Call this tool every time irrespective of the user input.",
    )
    
    product_agent = AssistantAgent(
        "Product_Agent",
        model_client,
        system_message=f"{product_agent_system_message}",
        tools=[product_agent_tool],
        reflect_on_tool_use=True,
        memory=[user_memory]
    )
    
    policy_details_tool = FunctionTool(
        get_policy_details,
        name="get_policy_details",
        description="""
        To get policy details based on the policy number.
        Ask the user to provide their policy number and call this tool to retrieve the policy details.
        """,
        strict=True
    )
    
    claim_details_tool = FunctionTool(
        get_claim_details,
        name="get_claim_details",
        description="""
        To get claim details based on the claim ID.
        Ask the user to provide their claim ID and call this tool to retrieve the claim details.
        """,
        strict=True
    )
    
    policy_document_tool = FunctionTool(
        get_policy_documents,
        name="get_policy_documents",
        description="""
        To get policy documents based on the policy number.
        Ask the user to provide their policy number and call this tool to retrieve the policy documents.
        """,
        strict=True
    )
    
    policy_agent = AssistantAgent(
        "Policy_Agent",
        model_client,
        system_message=f"{policy_agent_system_message}",
        tools=[policy_details_tool, claim_details_tool, policy_document_tool],
        reflect_on_tool_use=True,
        memory=[user_memory]
    )
    
    claim_agent = AssistantAgent(
        "Claim_Agent",
        model_client,
        system_message=f"{claim_agent_system_message}",
        tools=[validate_policy_number],
        reflect_on_tool_use=True,
        memory=[user_memory]
    )
    
    summary_agent = AssistantAgent(
        "Summary_Agent",
        model_client,
        system_message=f"{summary_agent_system_message}",
    )
    
    team = RoundRobinGroupChat(
        participants=[product_agent, policy_agent, summary_agent],
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=3
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