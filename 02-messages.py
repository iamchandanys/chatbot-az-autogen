import asyncio
import requests
import os
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_core import Image as AGImage
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

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

# Using Text Messages example

text_message = TextMessage(content="Who is virat kohli?", source="User")

async def run_agent_txt_msg() -> None:
    agent = AssistantAgent("assistant", az_model_client)
    print(await agent.run(task=text_message))

# Using Multi Modal Messages example

pil_image = Image.open(BytesIO(requests.get("https://picsum.photos/300/200").content))
img = AGImage(pil_image)
multi_modal_message = MultiModalMessage(content=["Can you describe the content of this image?", img], source="User")

async def run_agent_multi_modal_msg() -> None:
    agent = AssistantAgent("assistant", az_model_client)
    print(await agent.run(task=multi_modal_message))

asyncio.run(run_agent_multi_modal_msg())