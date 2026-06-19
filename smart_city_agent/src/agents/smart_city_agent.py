"""
Smart City Agent definition.

This is the main agent that orchestrates all tools to answer
user queries about cities (weather, time, etc.).
"""

from google.adk.agents import Agent
from google.adk.workflow import RetryConfig

from ..tools.weather import get_weather
from ..tools.time import get_time
from ..config.settings import settings
from ..utils.logging import logger
from ..utils.tracing import observe


@observe(name="create_smart_city_agent")
def create_smart_city_agent() -> Agent:
    """
    Create and configure the Smart City Agent.

    Returns:
        Agent: Configured ADK Agent instance

    Why a factory function?
    - Easier to test (can create multiple agents)
    - Easier to configure (can pass parameters)
    - Follows dependency injection pattern
    - Can add initialization logic here

    Why @observe decorator?
    - Traces agent creation in Langfuse
    - Captures timing, errors, and metadata
    - Helps debug initialization issues
    - Provides visibility into agent lifecycle
    """
    logger.info("Creating Smart City Agent")

    agent = Agent(
        name="smart_city_agent",
        model=settings.model_name,  # From config!
        description=(
            "An intelligent agent that provides real-time information about cities, "
            "including weather conditions, current time, and more. "
            "Currently supports weather and time queries for multiple cities."
        ),
        instruction=(
            "You are a helpful Smart City Assistant. "
            "You can answer questions about:\n"
            "- Weather conditions in cities\n"
            "- Current time in different cities\n\n"
            "When users ask about unsupported cities, politely let them know "
            "which cities are currently supported. "
            "Be friendly, concise, and accurate in your responses."
        ),
        tools=[get_weather, get_time],
        # Groq's llama-3.3-70b-versatile occasionally emits a malformed
        # tool-call (e.g. "<function=...>") that Groq's API rejects with a
        # 400 tool_use_failed. This is non-deterministic model behavior, so
        # retrying the call is the practical mitigation.
        retry_config=RetryConfig(
            max_attempts=3,
            exceptions=["BadRequestError"],
        ),
    )

    logger.info(f"Agent created: {agent.name} with {len(agent.tools)} tools")
    return agent


# Create singleton instance
# Why? Most applications need only one agent instance
root_agent = create_smart_city_agent()
