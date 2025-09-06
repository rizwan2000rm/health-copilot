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
            # Configure MCP server using uv as specified in the config
            hevy_mcp_dir = os.path.join(self.base_dir, "..", "hevy-mcp")
            
            # Get environment variables to pass to the MCP server
            env_vars = {}
            hevy_api_key = os.getenv("HEVY_API_KEY")
            if hevy_api_key:
                env_vars["HEVY_API_KEY"] = hevy_api_key
                print(f"✅ Passing HEVY_API_KEY to MCP server: {hevy_api_key[:10]}...")
            else:
                print("⚠️ HEVY_API_KEY not found in environment - MCP server may not work properly")
            
            # Use uv to run the MCP server as specified in the config
            server_config = {
                "hevy": {
                    "command": "/Users/rizwan/.local/bin/uv",
                    "args": [
                        "--directory",
                        hevy_mcp_dir,
                        "run",
                        "app.py"
                    ],
                    "transport": "stdio",
                    "env": env_vars
                }
            }
            
            self.mcp_client = MultiServerMCPClient(server_config)
            print("✅ MCP client initialized with environment variables")
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
    
class MCPRoutineManager:
    """High-level routine management using MCP tools."""
    
    def __init__(self, mcp_integration: MCPIntegration):
        """
        Initialize routine manager.
        
        Args:
            mcp_integration: MCP integration instance
        """
        self.mcp = mcp_integration
    
    async def create_folder(self, title: str) -> str:
        """Create a new routine folder with the given title."""
        folder_data = {
            "routine_folder": {
                "title": title
            }
        }
        return await self.mcp.create_routine_folder(folder_data)
    
    async def create_simple_routine(self, title: str, folder_id: int = None, notes: str = None) -> str:
        """Create a simple routine with just title, optional folder, and notes."""
        routine_data = {
            "routine": {
                "title": title,
                "folder_id": folder_id,
                "notes": notes
            }
        }
        return await self.mcp.create_routine(routine_data)
    
    async def get_all_folders(self) -> str:
        """Get all routine folders."""
        return await self.mcp.get_routine_folders()
    
    async def get_all_routines(self) -> str:
        """Get all routines."""
        return await self.mcp.get_routines()


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
        print("📊 Generating workout summary...")
        
        count_result = await self.mcp.get_workouts_count()
        recent_result = await self.mcp.get_workout_history(page=1, page_size=3)
        
        print(f"📈 Total workout count: {count_result}")
        print(f"📋 Recent workouts retrieved: {recent_result[:200]}..." if len(recent_result) > 200 else f"📋 Recent workouts retrieved: {recent_result}")
        
        summary = f"Workout Summary:\n\n"
        summary += f"Total Workouts: {count_result}\n\n"
        summary += f"Recent Workouts:\n{recent_result}"
        
        return summary
