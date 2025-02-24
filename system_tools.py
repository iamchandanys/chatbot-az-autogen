import requests
from typing import Any

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
    
# Fake database for user policy details
fake_policy_db = {
    "12345": {"name": "John Doe", "policy_type": "Health", "status": "Active"},
    "67890": {"name": "Jane Smith", "policy_type": "Auto", "status": "Expired"},
    "54321": {"name": "Alice Johnson", "policy_type": "Home", "status": "Active"},
}

def get_policy_details(policy_number: str) -> dict[str, Any] | None:
    """
    Retrieve policy details by policy number from the fake database.
    
    Args:
        policy_number (str): The policy number to search for.
        
    Returns:
        dict[str, Any] | None: The policy details if found, otherwise None.
    """
    return fake_policy_db.get(policy_number)
        
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
    
def search_product_details(user_message: str) -> str:
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
    result = search_product_details("9bdc7ece-763c-4c54-ba77-6360bee93c5b", "I want to know about the health insurance policy.")
    print(result)
