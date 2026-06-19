"""
Agent entry point for ADK CLI.

This file is required by ADK CLI which looks for 'agent.py' with 'root_agent'.
It imports the actual agent from our modular src/ structure.

Note: Using relative import (.src.main) because when ADK loads this module
as 'smart_city_agent.agent', Python needs to know that 'src' is relative
to the smart_city_agent package, not a top-level module.
"""

from .src.main import root_agent

# ADK CLI expects root_agent to be directly importable from agent.py
__all__ = ["root_agent"]
