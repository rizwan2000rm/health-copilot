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
    
    def __init__(self, model_name: str = "qwen2.5:3b"):
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

INSTRUCTIONS:
- Provide helpful, evidence-based fitness advice and workout recommendations
- When creating workout plans, use the available MCP tools to fetch workout history, create routines, and manage workout data
- Always analyze user's training patterns before making recommendations
- Focus on progressive overload, proper recovery, and balanced muscle group development
- Use exercise templates and create structured routines when appropriate
- Present plans clearly with rationale for exercise selection and programming decisions

Available tools:
- get_workouts: Fetch user's workout history
- create_routine: Create new workout routines
- create_routine_folder: Organize routines into folders
- get_exercise_templates: Access exercise database
- And other workout management tools

Provide comprehensive, actionable fitness guidance.
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
    
    
    async def generate_weekly_plan(self) -> str:
        """Generate a comprehensive weekly workout plan."""
        # Get research context from knowledge base
        research_context = ""
        retriever = self.knowledge_base.get_retriever()
        if retriever:
            try:
                # Get relevant documents for weekly planning and minimalist training
                docs = retriever.invoke("minimalist training weekly workout plan training volume frequency compound movements")
                if docs:
                    research_context = self.knowledge_base.format_docs(docs)
            except Exception as e:
                print(f"⚠️ Error retrieving research context: {e}")
        
        weekly_plan_prompt = f"""
Create a weekly workout plan for me. Follow these steps:

1. Get available exercises: get_exercise_templates(page=1, pageSize=100)

2. Fetch my last 10 workouts: get_workouts(pageSize=10)

3. Analyze the workouts to find:
   - Which muscle groups I train most/least
   - Any weak points or imbalances
   - Training patterns and frequency

4. Create a minimalist weekly plan that:
   - Uses compound movements (squats, rdls, bench press etc)
   - Balances all muscle groups
   - Includes progressive overload
   - Uses exercise templates from step 1

5. Create the routine folder: create_routine_folder(payload={{"routine_folder": {{"title": "Week xx"}}}})

6. Create workout routines for each day using this complete payload format:
create_routine(payload={{"routine": {{
  "title": "Push Day Workout",
  "folder_id": folder_id_from_step_5,
  "notes": "Minimalist push workout",
  "exercises": [
    {{
      "exercise_template_id": "05293BCA",
      "notes": "Focus on form",
      "rest_seconds": 120,
      "sets": [
        {{"reps": 5, "weight": 100}},
        {{"reps": 5, "weight": 105}},
        {{"reps": 5, "weight": 110}}
      ]
    }},
    {{
      "exercise_template_id": "12345ABC",
      "notes": "Progressive overload",
      "rest_seconds": 90,
      "sets": [
        {{"reps": 8, "weight": 50}},
        {{"reps": 8, "weight": 55}},
        {{"reps": 8, "weight": 60}}
      ]
    }}
  ]
}}}})

RESEARCH CONTEXT:
{research_context if research_context else "Use general evidence-based principles"}
"""
        return await self.get_response(weekly_plan_prompt)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        mcp_stats = self.mcp.get_stats()
        return {
            "model_name": self.model_name,
            "has_retriever": self.knowledge_base.has_knowledge_base(),
            "has_agent": self.agent is not None,
            **mcp_stats
        }