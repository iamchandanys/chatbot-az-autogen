import asyncio
import os
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from dotenv import load_dotenv
from system_prompts import product_agent_system_message, policy_agent_system_message, summary_agent_system_message, assigner_agent_system_message
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_core.tools import FunctionTool
from typing import Any, Mapping, Sequence
from autogen_agentchat.messages import  ChatMessage, AgentEvent
from system_tools import get_info, get_policy_details, get_claim_details, get_policy_documents, get_invoice_documents
from autogen_core.model_context import BufferedChatCompletionContext
import time

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
    - When reflect_on_tool_use is set to True: After the agent calls an external tool/function and receives its result, it performs an additional inference.
    - This means the agent re-evaluates the tool's output in the context of the original query to generate a more coherent and contextually integrated response.
    - When reflect_on_tool_use is set to False: The agent directly returns the tool's result as the final response without further processing or integration.
    
    memory
    - In Microsoft's AutoGen 0.4, the memory parameter in the AssistantAgent allows the agent to access and utilize external memory stores.
    - For instance, when a user asks a question, the agent can query its memory to find related information and incorporate it into its reply. 
    - This functionality is particularly useful for tasks requiring context-aware responses or when implementing retrieval-augmented generation (RAG) workflows.
    """
    
    # Create a memory store for the user
    user_memory = ListMemory()
    # Add user preferences to memory
    await user_memory.add(MemoryContent(content="The user name is chandan.", mime_type=MemoryMimeType.TEXT))
    await user_memory.add(MemoryContent(content="Chandan's policy number is POLICY008.", mime_type=MemoryMimeType.TEXT))
    await user_memory.add(MemoryContent(content="Chandan's claim ID is CLAIM1005.", mime_type=MemoryMimeType.TEXT))
    
    # Create a model context that only keeps the last 2 messages (2 user + 2 assistant).
    model_context = BufferedChatCompletionContext(buffer_size=4)
    
    product_agent_tool = FunctionTool(
        get_info,
        name="get_any_info",
        description="To get any information. Call this tool every time irrespective of the user input.",
    )
    
    product_agent = AssistantAgent(
        "Product_Agent",
        model_client,
        model_context=model_context,
        system_message=f"{product_agent_system_message}",
        tools=[product_agent_tool],
        reflect_on_tool_use=False,
        memory=[user_memory]
    )
    
    policy_details_tool = FunctionTool(
        get_policy_details,
        name="get_policy_details",
        description="""
        To get policy details based on the policy number.
        Ask the user to provide their policy number.
        Use this tool to retrieve the policy details.
        """,
        strict=True
    )
    
    policy_document_tool = FunctionTool(
        get_policy_documents,
        name="get_policy_documents",
        description="""
        To get policy documents based on the policy number.
        Ask the user to provide their policy number.
        Use this tool to retrieve the policy documents.
        """,
        strict=True
    )
    
    policy_invoice_tool = FunctionTool(
        get_invoice_documents,
        name="get_invoice_documents",
        description="""
        To get invoice documents based on the policy number.
        Ask the user to provide their policy number.
        Use this tool to retrieve the invoice documents.
        """,
        strict=True
    )
    
    claim_details_tool = FunctionTool(
        get_claim_details,
        name="get_claim_details",
        description="""
        To get claim details based on the claim ID.
        Ask the user to provide their claim ID.
        Use this tool to retrieve the claim details.
        """,
        strict=True
    )
    
    policy_agent = AssistantAgent(
        "Policy_Agent",
        model_client,
        model_context=model_context,
        system_message=f"{policy_agent_system_message}",
        tools=[policy_details_tool, policy_document_tool, policy_invoice_tool, claim_details_tool],
        reflect_on_tool_use=True,
        memory=[user_memory]
    )
    
    # summary_agent = AssistantAgent(
    #     "Summary_Agent",
    #     model_client,
    #     model_context=model_context,
    #     system_message=f"{summary_agent_system_message}",
    #     memory=[user_memory]
    # )
    
    assigner_agent = AssistantAgent(
        "Assigner_Agent",
        model_client,
        model_context=model_context,
        system_message=f"{assigner_agent_system_message}",
        memory=[user_memory]
    )
    
    # team = RoundRobinGroupChat(
    #     participants=[product_agent, policy_agent, summary_agent],
    #     termination_condition=TextMentionTermination("TERMINATE"),
    #     max_turns=3
    # )
    
    def selector_func(messages: Sequence[AgentEvent | ChatMessage]) -> str | None:
        if messages[-1].source != assigner_agent.name:
            return assigner_agent.name
        return None

    selector_prompt = """
    You are a selector agent responsible for selecting the most relevant information from the Product_Agent and Policy_Agent's responses.
    """
    
    team = SelectorGroupChat(
        participants=[product_agent, policy_agent, assigner_agent],
        model_client=model_client,
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=2,
        allow_repeated_speaker=True,
        selector_prompt=selector_prompt,
        selector_func=selector_func
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
    
    while True:
        user_input = input("User: ")
        if "stop" in user_input: break
        start_time = time.time()
        result = await main(user_input, agent_state_disk)
        end_time = time.time()
        agent_state_disk = result["agent_state"]
        print(f"Agent: {result['response']}")
        print(f"Time taken: {end_time - start_time} seconds")
        print("-" * 50)
    
asyncio.run(chat())