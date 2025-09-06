"""
MCP Integration Module for AI Fitness Coach.

This module handles all MCP (Model Context Protocol) related functionality,
including tool loading, agent creation, and workout tracking operations.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
from langchain_core.tools import Tool

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from {env_file}")
except ImportError:
    # dotenv not available, continue without it
    pass

# MCP integration imports
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langgraph.prebuilt import create_react_agent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ langchain-mcp-adapters not available. Install with: pip install langchain-mcp-adapters")


class MCPIntegration:
    """Handles MCP integration for the fitness coach."""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize MCP integration.
        
        Args:
            base_dir: Base directory path for finding MCP server
        """
        self.base_dir = base_dir or os.path.dirname(__file__)
        self.mcp_client: Optional[MultiServerMCPClient] = None
        self.mcp_tools: List[Tool] = []
        self.agent = None
        
        # Initialize MCP connection if available
        if MCP_AVAILABLE:
            self._setup_mcp_connection()
    
    def _setup_mcp_connection(self) -> None:
        """Set up MCP connection to Hevy server."""
        try:
            # Configure MCP server (assuming your Hevy MCP server is running locally)
            hevy_mcp_path = os.path.join(self.base_dir, "..", "hevy-mcp", "app.py")
            
            server_config = {
                "hevy": {
                    "command": "python",
                    "args": [hevy_mcp_path],
                    "transport": "stdio"
                }
            }
            
            self.mcp_client = MultiServerMCPClient(server_config)
            print("✅ MCP client initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize MCP client: {e}")
            self.mcp_client = None
    
    async def load_tools(self) -> List[Tool]:
        """Load tools from MCP server."""
        if not self.mcp_client:
            return []
        
        try:
            tools = await self.mcp_client.get_tools()
            self.mcp_tools = tools
            print(f"✅ Loaded {len(tools)} MCP tools")
            return tools
        except Exception as e:
            print(f"⚠️ Failed to load MCP tools: {e}")
            self.mcp_tools = []
            return []
    
    def create_agent(self, model):
        """Create LangGraph agent with MCP tools."""
        if not self.mcp_tools:
            print("⚠️ No MCP tools available, cannot create agent")
            return None
        
        try:
            self.agent = create_react_agent(model, self.mcp_tools)
            print(f"✅ Agent created with {len(self.mcp_tools)} tools")
            return self.agent
        except Exception as e:
            print(f"⚠️ Failed to create agent: {e}")
            return None
    
    async def get_workout_history(self, page: int = 1, page_size: int = 5) -> str:
        """Get user's workout history using MCP tools."""
        if not self.mcp_tools:
            return "Workout tracking tools are not available."
        
        # Find the get_workouts tool
        workouts_tool = None
        for tool in self.mcp_tools:
            if tool.name == "get_workouts":
                workouts_tool = tool
                break
        
        if not workouts_tool:
            return "Workout history tool not found."
        
        try:
            result = await workouts_tool.ainvoke({"page": page, "pageSize": page_size})
            return result
        except Exception as e:
            return f"Error retrieving workout history: {e}"
    
    async def create_workout(self, workout_data: Dict[str, Any]) -> str:
        """Create a new workout using MCP tools."""
        if not self.mcp_tools:
            return "Workout tracking tools are not available."
        
        # Find the create_workout tool
        create_tool = None
        for tool in self.mcp_tools:
            if tool.name == "create_workout":
                create_tool = tool
                break
        
        if not create_tool:
            return "Workout creation tool not found."
        
        try:
            result = await create_tool.ainvoke({"payload": workout_data})
            return result
        except Exception as e:
            return f"Error creating workout: {e}"
    
    async def update_workout(self, workout_id: str, workout_data: Dict[str, Any]) -> str:
        """Update an existing workout using MCP tools."""
        if not self.mcp_tools:
            return "Workout tracking tools are not available."
        
        # Find the update_workout tool
        update_tool = None
        for tool in self.mcp_tools:
            if tool.name == "update_workout":
                update_tool = tool
                break
        
        if not update_tool:
            return "Workout update tool not found."
        
        try:
            result = await update_tool.ainvoke({"workoutId": workout_id, "payload": workout_data})
            return result
        except Exception as e:
            return f"Error updating workout: {e}"
    
    async def get_workout(self, workout_id: str) -> str:
        """Get a specific workout by ID using MCP tools."""
        if not self.mcp_tools:
            return "Workout tracking tools are not available."
        
        # Find the get_workout tool
        get_tool = None
        for tool in self.mcp_tools:
            if tool.name == "get_workout":
                get_tool = tool
                break
        
        if not get_tool:
            return "Workout retrieval tool not found."
        
        try:
            result = await get_tool.ainvoke({"workoutId": workout_id})
            return result
        except Exception as e:
            return f"Error retrieving workout: {e}"
    
    async def get_workouts_count(self) -> str:
        """Get the total number of workouts using MCP tools."""
        if not self.mcp_tools:
            return "Workout tracking tools are not available."
        
        # Find the get_workouts_count tool
        count_tool = None
        for tool in self.mcp_tools:
            if tool.name == "get_workouts_count":
                count_tool = tool
                break
        
        if not count_tool:
            return "Workout count tool not found."
        
        try:
            result = await count_tool.ainvoke({})
            return result
        except Exception as e:
            return f"Error retrieving workout count: {e}"
    
    def get_tool_names(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.mcp_tools]
    
    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get dictionary of tool names and descriptions."""
        return {tool.name: tool.description for tool in self.mcp_tools}
    
    def is_available(self) -> bool:
        """Check if MCP integration is available."""
        return MCP_AVAILABLE and self.mcp_client is not None
    
    def has_tools(self) -> bool:
        """Check if MCP tools are loaded."""
        return len(self.mcp_tools) > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MCP integration statistics."""
        return {
            "mcp_available": MCP_AVAILABLE,
            "client_initialized": self.mcp_client is not None,
            "tools_loaded": len(self.mcp_tools),
            "agent_created": self.agent is not None,
            "tool_names": self.get_tool_names()
        }


class MCPWorkoutManager:
    """High-level workout management using MCP tools."""
    
    def __init__(self, mcp_integration: MCPIntegration):
        """
        Initialize workout manager.
        
        Args:
            mcp_integration: MCP integration instance
        """
        self.mcp = mcp_integration
    
    async def get_recent_workouts(self, count: int = 5) -> str:
        """Get recent workouts."""
        return await self.mcp.get_workout_history(page=1, page_size=count)
    
    async def create_simple_workout(self, name: str, notes: str = None) -> str:
        """Create a simple workout with just name and notes."""
        workout_data = {
            "workout": {
                "name": name,
                "notes": notes
            }
        }
        return await self.mcp.create_workout(workout_data)
    
    async def get_workout_summary(self) -> str:
        """Get a summary of workout statistics."""
        count_result = await self.mcp.get_workouts_count()
        recent_result = await self.mcp.get_workout_history(page=1, page_size=3)
        
        summary = f"Workout Summary:\n\n"
        summary += f"Total Workouts: {count_result}\n\n"
        summary += f"Recent Workouts:\n{recent_result}"
        
        return summary
