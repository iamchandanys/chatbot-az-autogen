import requests

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