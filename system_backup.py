async def lookup_hotel(location: str) -> str:
    return f"Here are some hotels in {location}: hotel1, hotel2, hotel3."

async def lookup_flight(origin: str, destination: str) -> str:
    return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3."

async def book_trip() -> str:
    return "Your trip is booked!"

# primary_agent = AssistantAgent(
    #     "Primary_Agent",
    #     model_client,
    #     description="Helps users to get insurance product details, policy details, and claim details.",
    #     system_message="""
    #     You are the primary agent.
        
    #     You only delegate tasks - you do not execute them yourself. Engage with team members to get the correct information to the users.
        
    #     Your team members are:
    #         Product_Agent: Helps users to get MLCP insurance product details.
    #         Policy_Agent: Helps users to get their policy details.
    #         Claim_Agent: Helps users to log a claim.
        
    #     After all tasks are completed, give the correct related information to the user and end with "TERMINATE".
    #     """
    # )