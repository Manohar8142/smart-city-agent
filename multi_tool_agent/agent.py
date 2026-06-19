from datetime import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

def get_weather(city:str) -> str:
    if city.lower() == "new york":
        return{
            "status":"success",
            "report":{
                "temperature": "25°C",
                "humidity": "60%",
                "condition": "Sunny"
            },
        }
    else:
        return{
            "status":"error",
            "error_message":f"Weather information for this '{city}' is not available",
        }

def get_time(city:str) -> dict:
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return{
            "status":"error",
            "error_message": f"Sorry I dont have timezone information for '{city}'",
        }
    tz = ZoneInfo(tz_identifier)
    now = datetime.now(tz)
    report = f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
    return {"status":"success","report":report}

root_agent = Agent(
    name="weather_and_time_agent",
    model = 'groq/llama-3.3-70b-versatile',
    description = (
        "Agent to answer questions about the time and weather in a city"
    ),
    instruction = (
        "You are a helpful agent who can answer user questions about the time and weather in a city"
    ),
    tools = [get_weather, get_time]
)
