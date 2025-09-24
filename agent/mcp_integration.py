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
        self.is_initialized = False
        
        # Initialize MCP connection if available
        if MCP_AVAILABLE:
            self._setup_mcp_connection()
    
    def _setup_mcp_connection(self) -> None:
        """Set up MCP connection to Hevy server."""
        try:
            # Get the absolute path to the hevy-mcp directory
            hevy_mcp_dir = os.path.abspath(os.path.join(self.base_dir, "..", "hevy-mcp"))
            
            # Check if the MCP server directory exists
            if not os.path.exists(hevy_mcp_dir):
                print(f"⚠️ Hevy MCP directory not found at: {hevy_mcp_dir}")
                return
            
            # Get environment variables to pass to the MCP server
            env_vars = {}
            hevy_api_key = os.getenv("HEVY_API_KEY")
            if hevy_api_key:
                env_vars["HEVY_API_KEY"] = hevy_api_key
                print(f"✅ Passing HEVY_API_KEY to MCP server: {hevy_api_key[:10]}...")
            else:
                print("⚠️ HEVY_API_KEY not found in environment - MCP server may not work properly")
            
            # Configure MCP server using uv (resolve path dynamically)
            server_config = {
                "hevy": {
                   "command": os.getenv("UV_BIN", "uv"),
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
            print("✅ MCP client initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize MCP client: {e}")
            self.mcp_client = None
    
    async def load_tools(self) -> List[Tool]:
        """Load tools from MCP server."""
        if not self.mcp_client:
            print("⚠️ No MCP client available")
            return []
        
        try:
            tools = await self.mcp_client.get_tools()
            self.mcp_tools = tools
            self.is_initialized = True
            print(f"✅ Loaded {len(tools)} MCP tools")
            
            # Print tool names for debugging
            tool_names = [tool.name for tool in tools]
            print(f"📋 Available tools: {', '.join(tool_names)}")
            
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get MCP integration statistics."""
        return {
            "mcp_available": MCP_AVAILABLE,
            "mcp_client_initialized": self.mcp_client is not None,
            "tools_loaded": len(self.mcp_tools),
            "agent_created": self.agent is not None,
            "is_initialized": self.is_initialized
        }
    
    async def test_connection(self) -> bool:
        """Test MCP connection by loading tools."""
        try:
            tools = await self.load_tools()
            return len(tools) > 0
        except Exception as e:
            print(f"⚠️ MCP connection test failed: {e}")
            return False