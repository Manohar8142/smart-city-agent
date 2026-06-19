"""
Main entry point for Smart City Agent.

This file is discovered by the ADK CLI when running:
    adk run
    adk web
    adk api_server

It exports the root_agent that ADK expects.
"""

from src.agents.smart_city_agent import root_agent
from src.utils.logging import logger
from src.config.settings import settings


# Log startup information
logger.info("=" * 60)
logger.info("Smart City Agent Starting")
logger.info("=" * 60)
logger.info(f"Environment: {settings.environment}")
logger.info(f"Model: {settings.model_name}")
logger.info(f"Log Level: {settings.log_level}")
logger.info(f"Langfuse Enabled: {settings.enable_langfuse}")
logger.info("=" * 60)


# Export for ADK
# ADK looks for "root_agent" or "agent" in main.py or agent.py
__all__ = ["root_agent"]


if __name__ == "__main__":
    # This runs if you execute: python src/main.py
    # Useful for debugging
    print("Smart City Agent")
    print(f"Agent Name: {root_agent.name}")
    print(f"Model: {root_agent.model}")
    print(f"Tools: {[tool.__name__ for tool in root_agent.tools]}")
    print("\nTo run the agent, use: adk run")
