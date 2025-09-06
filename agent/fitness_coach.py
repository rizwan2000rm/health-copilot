"""
AI Fitness Coach module.

Core AI coaching logic with MCP tools and knowledge base integration.
"""

import asyncio
from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from knowledge import KnowledgeBase
from mcp_integration import MCPIntegration


class FitnessCoach:
    """AI Fitness Coach with MCP tools and knowledge base integration."""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        """Initialize the AI Fitness Coach."""
        self.model_name = model_name
        self.model = ChatOllama(model=model_name, temperature=0.7)
        self.knowledge_base = KnowledgeBase()
        self.mcp = MCPIntegration()
        self.agent = None
        
        # Initialize the prompt template
        self._setup_prompt_template()
    
    def _setup_prompt_template(self) -> None:
        """Set up the prompt template for the AI coach."""
        self.template = """
You are a minimalist fitness coach expert focused on evidence-based, time-efficient workout planning. 

RESEARCH CONTEXT: {context}

USER REQUEST: {input}

Provide helpful, evidence-based fitness advice and workout recommendations.
"""
        self.prompt = ChatPromptTemplate.from_template(self.template)
    
    def setup_knowledge_base(self, context_dir: str) -> bool:
        """Set up the knowledge base from context directory."""
        return self.knowledge_base.setup_knowledge_base(context_dir)
    
    async def setup_agent(self) -> bool:
        """Set up the LangGraph agent with MCP tools."""
        try:
            # Test MCP connection first
            connection_ok = await self.mcp.test_connection()
            if not connection_ok:
                print("⚠️ MCP connection failed, agent will use knowledge base only")
                return False
            
            # Load tools and create agent
            tools = await self.mcp.load_tools()
            if tools:
                self.agent = self.mcp.create_agent(self.model)
                if self.agent:
                    print("✅ Agent successfully created with MCP tools")
                    return True
            
            print("⚠️ Failed to create agent with MCP tools")
            return False
        except Exception as e:
            print(f"⚠️ Error setting up agent: {e}")
            return False
    
    async def get_response(self, user_input: str) -> str:
        """Get a response from the AI coach."""
        if self.agent:
            try:
                # Use agent with MCP tools
                response = await self.agent.ainvoke({"messages": [("user", user_input)]})
                if isinstance(response, dict) and "messages" in response:
                    messages = response["messages"]
                    if messages and hasattr(messages[-1], 'content'):
                        return messages[-1].content
                return str(response)
            except Exception as e:
                print(f"⚠️ Agent error: {e}, falling back to knowledge base")
                # Fall through to fallback
        
        # Fallback to basic chain with knowledge base
        retriever = self.knowledge_base.get_retriever()
        if retriever:
            chain = (
                {"context": retriever | self.knowledge_base.format_docs, "input": RunnablePassthrough()}
                | self.prompt
                | self.model
                | StrOutputParser()
            )
            return chain.invoke(user_input)
        else:
            chain = self.prompt | self.model | StrOutputParser()
            return chain.invoke({"input": user_input})
    
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        mcp_stats = self.mcp.get_stats()
        return {
            "model_name": self.model_name,
            "has_retriever": self.knowledge_base.has_knowledge_base(),
            "has_agent": self.agent is not None,
            **mcp_stats
        }