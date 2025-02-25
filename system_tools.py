import requests
from system_fake_db import user_insurance_details
from system_helper import process_and_upload_policy, process_and_upload_invoice

def get_policy_details(policy_number: str) -> None | str:
    for policy in user_insurance_details:
        if policy.get("policy_number") == policy_number:
            return f"Policy found in the database and here's the details: {policy}"
    return "Policy not found in the database. Please provide a valid policy number."

def get_policy_documents(policy_number: str) -> None | str:
    for policy in user_insurance_details:
        if policy.get("policy_number") == policy_number:
            pdf_url = process_and_upload_policy(policy)
            if pdf_url:
                return f"Policy documents uploaded successfully. You can download the documents from the following URL: {pdf_url}"
            else:
                return "Failed to upload policy documents. Please try again later."
    return "Policy not found in the database. Please provide a valid policy number."

def get_invoice_documents(policy_number: str) -> None | str:
    for policy in user_insurance_details:
        if policy.get("policy_number") == policy_number:
            pdf_url = process_and_upload_invoice(policy)
            if pdf_url:
                return f"Invoice documents uploaded successfully. You can download the documents from the following URL: {pdf_url}"
            else:
                return "Failed to upload invoice documents. Please try again later."
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
