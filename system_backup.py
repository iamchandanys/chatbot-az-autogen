async def lookup_hotel(location: str) -> str:
    return f"Here are some hotels in {location}: hotel1, hotel2, hotel3."

async def lookup_flight(origin: str, destination: str) -> str:
    return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3."

async def book_trip() -> str:
    return "Your trip is booked!"