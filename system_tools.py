import requests
from typing import Any
from system_fake_db import user_insurance_details

def validate_policy_number(policy_number: str) -> str:
    api_url = f"https://emc-b2b-api.azurewebsites.net/api/XAgents/ClaimAgentValidatePolicy/{policy_number}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("exists"):
                return "The policy number exists in DB. Proceed next."
            else:
                return "The policy number not found. Ask the user to provide correct policy number."
        else:
            return f"Failed to validate policy number. API returned status code {response.status_code}."
    except Exception as e:
        return f"An error occurred while validating the policy number: {str(e)}"

def get_policy_details(policy_number: str) -> None | str:
    for policy in user_insurance_details:
        if policy.get("policy_number") == policy_number:
            return f"Policy found in the database and here's the details: {policy}"
    return "Policy not found in the database. Please provide a valid policy number."

def get_claim_details(claim_id: str) -> None | str:
    for policy in user_insurance_details:
        for claim in policy.get("claims_history"):
            if claim.get("claim_id") == claim_id:
                return f"Claim found in the database and here's the details: {claim}"
            else:
                return "Claim not found in the database. Please provide a valid claim ID."
    
def init_chat() -> str:
    api_url = "https://emc-b2b-api.azurewebsites.net/api/XChatBot/InitChat/cd0fa1ea-d376-42b9-9a08-734414a862df/a41cd3d1-b093-4664-96d3-82f30f1aee0e"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json().get("id")
        else:
            return f"Failed to retrieve policy details. API returned status code {response.status_code}."
    except Exception as e:
        return f"An error occurred while retrieving policy details: {str(e)}"
    
def get_info(user_message: str) -> str:
    """
    Search for MLCP insurance product details based on the user message.
    
    Args:
        user_message (str): The user message to search for.
        
    Returns:
        str: The response from the API
    """
    chat_id = init_chat()
    
    # Validate the chat ID
    if not isinstance(chat_id, str) or len(chat_id) != 36:
        raise ValueError("Chat is not initialized.")
    
    api_url = "https://emc-b2b-api.azurewebsites.net/api/XChatBot/ChatCompletion"
    payload = {
        "chatId": chat_id,
        "message": user_message,
        "clientId": "cd0fa1ea-d376-42b9-9a08-734414a862df",
        "productId": "a41cd3d1-b093-4664-96d3-82f30f1aee0e"
    }
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            return response.json().get("messageContent")
        else:
            return f"Failed to send message. API returned status code {response.status_code}."
    except Exception as e:
        return f"An error occurred while sending the message: {str(e)}"
    
if __name__ == "__main__":
    result = get_claim_details("CLAIM1001x")
    print(result)
