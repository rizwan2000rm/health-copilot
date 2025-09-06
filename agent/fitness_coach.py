"""
AI Fitness Coach module.

This module contains the core AI coaching logic, including model initialization,
prompt templates, and response generation with document retrieval.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever
from document_processor import DocumentProcessor
from cache import ResponseCache
from mcp_integration import MCPIntegration, MCPWorkoutManager


class FitnessCoach:
    """AI Fitness Coach that provides workout advice and guidance."""
    
    def __init__(self, model_name: str = "llama3.2:3b", cache_file: str = "response_cache.json"):
        """
        Initialize the AI Fitness Coach.
        
        Args:
            model_name: Name of the Ollama model to use
            cache_file: Path to the cache file for response caching
        """
        self.model_name = model_name
        self.model = ChatOllama(model=model_name, temperature=0.7)
        self.cache = ResponseCache(cache_file)
        self.doc_processor = DocumentProcessor()
        self.retriever: Optional[VectorStoreRetriever] = None
        self.chain = None
        self.agent = None
        
        # Initialize MCP integration
        self.mcp = MCPIntegration()
        self.workout_manager = MCPWorkoutManager(self.mcp)
        
        # Initialize the prompt template
        self._setup_prompt_template()
    
    
    def _setup_prompt_template(self) -> None:
        """Set up the prompt template for the AI coach."""
        self.template = """You are a minimalist fitness coach with access to workout tracking tools. 
Focus on evidence-based, time-efficient workouts (45-60 min, 2-3x/week).

PRINCIPLES: Compound movements, progressive overload, safety-first, sustainability.

RESEARCH CONTEXT: {context}

USER REQUEST: {input}

You have access to workout tracking tools. When appropriate, you can:
- Retrieve user's workout history
- Create new workouts
- Update existing workouts
- Get workout statistics

Provide a concise, practical workout solution with form cues and modifications. 
Use research context when relevant. If the user asks about their workout history 
or wants to track workouts, use the available tools."""
        
        self.prompt = ChatPromptTemplate.from_template(self.template)
    
    def setup_knowledge_base(self, context_dir: str) -> bool:
        """
        Set up the knowledge base from context directory.
        
        Args:
            context_dir: Path to the directory containing fitness documents
            
        Returns:
            True if knowledge base was set up successfully, False otherwise
        """
        print(f"📁 Context directory: {context_dir}")
        
        # Check if context directory exists and has files
        if not os.path.exists(context_dir):
            print(f"❌ Context directory not found: {context_dir}")
            return False
        
        files = os.listdir(context_dir)
        print(f"📄 Found {len(files)} files in context directory: {files}")
        
        vectorstore = self.doc_processor.setup_knowledge_base(context_dir)
        
        if vectorstore is None:
            print("❌ Failed to set up knowledge base. Running without context.")
            return False
        
        # Get retriever for document search - reduced k for faster retrieval
        self.retriever = self.doc_processor.get_retriever(vectorstore, k=2)
        
        try:
            chunk_count = vectorstore._collection.count()
            print(f"✅ Knowledge base ready with {chunk_count} chunks")
            
            # If we have 0 chunks, try to force refresh
            if chunk_count == 0:
                print("🔄 Detected empty knowledge base, forcing refresh...")
                self.doc_processor.clear_existing_vectorstore()
                vectorstore = self.doc_processor.setup_knowledge_base(context_dir, force_refresh=True)
                if vectorstore:
                    self.retriever = self.doc_processor.get_retriever(vectorstore, k=2)
                    chunk_count = vectorstore._collection.count()
                    print(f"✅ Refreshed knowledge base ready with {chunk_count} chunks")
        except Exception as e:
            print(f"⚠️ Could not get chunk count: {e}")
            print("✅ Knowledge base loaded (chunk count unavailable)")
        
        return True
    
    async def setup_agent(self) -> None:
        """Set up the LangGraph agent with MCP tools."""
        # Load MCP tools
        await self.mcp.load_tools()
        
        # Create the agent with tools
        self.agent = self.mcp.create_agent(self.model)
    
    def _setup_chain(self) -> None:
        """Set up the processing chain based on whether retrieval is available."""
        if self.retriever:
            # Chain with retrieval
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.chain = (
                {"context": self.retriever | format_docs, "input": RunnablePassthrough()}
                | self.prompt
                | self.model
                | StrOutputParser()
            )
        else:
            # Chain without retrieval
            self.chain = self.prompt | self.model | StrOutputParser()
    
    async def get_response(self, user_input: str) -> str:
        """
        Get a response from the AI coach for the given input.
        
        Args:
            user_input: The user's question or request
            
        Returns:
            The AI coach's response
        """
        # Check cache first for faster response
        cached_response = self.cache.get(user_input)
        if cached_response:
            return cached_response
        
        # Get response from the model
        if self.agent:
            # Use agent with tools
            response = await self.agent.ainvoke({"messages": [("user", user_input)]})
            # Extract the response from the agent output
            if isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
                if messages and hasattr(messages[-1], 'content'):
                    response_text = messages[-1].content
                else:
                    response_text = str(response)
            else:
                response_text = str(response)
        else:
            # Fallback to basic chain without tools
            if self.retriever:
                def format_docs(docs):
                    return "\n\n".join(doc.page_content for doc in docs)
                
                chain = (
                    {"context": self.retriever | format_docs, "input": RunnablePassthrough()}
                    | self.prompt
                    | self.model
                    | StrOutputParser()
                )
                response_text = chain.invoke(user_input)
            else:
                chain = self.prompt | self.model | StrOutputParser()
                response_text = chain.invoke({"input": user_input})
        
        # Cache the response for future use
        self.cache.set(user_input, response_text)
        
        return response_text
    
    def get_response_sync(self, user_input: str) -> str:
        """
        Synchronous wrapper for get_response (for backward compatibility).
        
        Args:
            user_input: The user's question or request
            
        Returns:
            The AI coach's response
        """
        return asyncio.run(self.get_response(user_input))
    
    def get_cached_response(self, user_input: str) -> Optional[str]:
        """
        Get a cached response if available.
        
        Args:
            user_input: The user's question or request
            
        Returns:
            Cached response if available, None otherwise
        """
        return self.cache.get(user_input)
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        mcp_stats = self.mcp.get_stats()
        return {
            "cache_size": self.cache.size(),
            "cache_file": self.cache.cache_file,
            "model_name": self.model_name,
            "has_retriever": self.retriever is not None,
            **mcp_stats
        }
    
    async def create_weekly_plan(self) -> str:
        """
        Main workflow for creating a personalized weekly workout plan.
        
        This method orchestrates the entire process:
        1. Shows user what we're building
        2. Collects optional preferences
        3. Creates initial plan
        4. Allows iterative feedback and updates
        
        Returns:
            Final approved weekly plan
        """
        print("🏋️‍♂️ AI FITNESS COACH - WEEKLY PLANNING SYSTEM")
        print("=" * 50)
        
        # Step 1: Show user what we're building
        await self._show_planning_overview()
        
        # Step 2: Collect optional preferences
        preferences = await self._collect_user_preferences()
        
        # Step 3: Create initial plan
        plan = await self._generate_weekly_plan(preferences)
        
        # Step 4: Iterative feedback loop
        while True:
            print("\n" + "=" * 50)
            print("📋 YOUR WEEKLY PLAN")
            print("=" * 50)
            print(plan)
            
            feedback = input("\n🤔 What do you think? (Enter 'accept' to approve, or provide feedback): ").strip()
            
            if feedback.lower() in ['accept', 'yes', 'y', 'approve', 'good']:
                print("\n✅ Plan approved! Creating routines in your Hevy app...")
                await self._create_routines_in_hevy(plan)
                return plan
            
            elif feedback.lower() in ['skip', 'cancel', 'exit']:
                print("\n❌ Planning cancelled.")
                return "Planning cancelled by user."
            
            else:
                print(f"\n🔄 Updating plan based on your feedback: '{feedback}'")
                plan = await self._update_plan_based_on_feedback(plan, feedback)
    
    async def _show_planning_overview(self) -> None:
        """Show user what we're building and explain the process."""
        print("\n🎯 WHAT WE'RE BUILDING FOR YOU:")
        print("-" * 30)
        print("📊 Analyzing your last 10 days of workouts")
        print("🔍 Identifying muscle group gaps and imbalances")
        print("📚 Applying evidence-based training principles")
        print("📁 Creating a 'Week XX' folder in your routines")
        print("🏋️‍♂️ Designing 2-3 minimalist workouts (45-60 min each)")
        print("⚡ Focusing on compound movements and essential patterns")
        print("📈 Including progression guidelines and form cues")
        
        print("\n🔄 THE PROCESS:")
        print("-" * 15)
        print("1. I'll analyze your workout history")
        print("2. You can share preferences (optional)")
        print("3. I'll create your personalized plan")
        print("4. You can review and provide feedback")
        print("5. I'll update the plan until you're happy")
        print("6. I'll create the routines in your Hevy app")
        
        input("\nPress Enter to continue...")
    
    async def _collect_user_preferences(self) -> Dict[str, Any]:
        """Collect optional user preferences for the weekly plan."""
        print("\n🎯 OPTIONAL PREFERENCES")
        print("-" * 25)
        print("You can skip this step by pressing Enter, or share your preferences:")
        
        preferences = {
            "workout_frequency": None,
            "session_duration": None,
            "focus_areas": [],
            "avoid_exercises": [],
            "equipment_available": [],
            "goals": []
        }
        
        # Workout frequency
        freq = input("\n📅 How many workouts per week? (2-4, default: 3): ").strip()
        if freq and freq.isdigit() and 2 <= int(freq) <= 4:
            preferences["workout_frequency"] = int(freq)
        
        # Session duration
        duration = input("⏱️ Preferred session duration? (30-90 min, default: 60): ").strip()
        if duration and duration.isdigit() and 30 <= int(duration) <= 90:
            preferences["session_duration"] = int(duration)
        
        # Focus areas
        focus = input("🎯 Any specific focus areas? (e.g., 'strength', 'muscle growth', 'conditioning'): ").strip()
        if focus:
            preferences["focus_areas"] = [area.strip() for area in focus.split(',')]
        
        # Equipment
        equipment = input("🏋️‍♂️ Available equipment? (e.g., 'barbell', 'dumbbells', 'bodyweight'): ").strip()
        if equipment:
            preferences["equipment_available"] = [eq.strip() for eq in equipment.split(',')]
        
        # Goals
        goals = input("🎯 Short-term goals? (e.g., 'increase bench press', 'lose weight'): ").strip()
        if goals:
            preferences["goals"] = [goal.strip() for goal in goals.split(',')]
        
        print("\n✅ Preferences collected (or skipped). Moving to plan creation...")
        return preferences
    
    async def _generate_weekly_plan(self, preferences: Dict[str, Any]) -> str:
        """Generate the initial weekly plan using MCP tools and knowledge base."""
        print("\n🔍 ANALYZING YOUR WORKOUT HISTORY...")
        
        # Get recent workouts
        recent_workouts = await self.mcp.get_workout_history(page=1, page_size=10)
        print(f"📊 Retrieved recent workouts")
        
        # Get exercise templates for analysis
        exercise_templates = await self._get_exercise_templates()
        
        # Get scientific context
        scientific_context = ""
        if self.retriever:
            try:
                docs = self.retriever.invoke("minimalist training weekly plan compound movements")
                scientific_context = "\n\n".join([doc.page_content for doc in docs])
            except Exception as e:
                print(f"⚠️ Could not retrieve scientific context: {e}")
        
        # Create the planning prompt
        planning_prompt = f"""
        You are creating a personalized weekly workout plan. Here's the data:

        RECENT WORKOUTS (Last 10 days):
        {recent_workouts}

        EXERCISE TEMPLATES AVAILABLE:
        {exercise_templates}

        USER PREFERENCES:
        {preferences}

        SCIENTIFIC CONTEXT:
        {scientific_context}

        Create a comprehensive weekly plan that:
        1. Analyzes the user's current training patterns
        2. Identifies muscle group gaps and imbalances
        3. Addresses missing essential movement patterns
        4. Follows minimalist principles (2-3 sessions, 45-60 min)
        5. Focuses on compound movements
        6. Includes progression guidelines
        7. Provides form cues and modifications

        Format the response as a detailed weekly plan with:
        - Training analysis summary
        - Weekly structure (days, focus areas)
        - Specific exercises with sets/reps
        - Progression guidelines
        - Form cues and safety notes
        - Rationale based on scientific evidence
        """
        
        # Generate the plan using the AI model
        if self.agent:
            response = await self.agent.ainvoke({"messages": [("user", planning_prompt)]})
            if isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
                if messages and hasattr(messages[-1], 'content'):
                    plan = messages[-1].content
                else:
                    plan = str(response)
            else:
                plan = str(response)
        else:
            # Fallback to basic chain
            if self.retriever:
                def format_docs(docs):
                    return "\n\n".join(doc.page_content for doc in docs)
                
                chain = (
                    {"context": self.retriever | format_docs, "input": RunnablePassthrough()}
                    | self.prompt
                    | self.model
                    | StrOutputParser()
                )
                plan = chain.invoke(planning_prompt)
            else:
                chain = self.prompt | self.model | StrOutputParser()
                plan = chain.invoke({"input": planning_prompt})
        
        return plan
    
    async def _get_exercise_templates(self) -> str:
        """Get exercise templates from Hevy API."""
        try:
            # Use the MCP integration method
            if hasattr(self.mcp, 'mcp_tools') and self.mcp.mcp_tools:
                # Find the get_exercise_templates tool
                templates_tool = None
                for tool in self.mcp.mcp_tools:
                    if tool.name == "get_exercise_templates":
                        templates_tool = tool
                        break
                
                if templates_tool:
                    result = await templates_tool.ainvoke({"page": 1, "pageSize": 20})
                    return result
                else:
                    return "Exercise templates tool not available"
            else:
                return "MCP tools not loaded"
        except Exception as e:
            return f"Error retrieving exercise templates: {e}"
    
    async def _update_plan_based_on_feedback(self, current_plan: str, feedback: str) -> str:
        """Update the plan based on user feedback."""
        update_prompt = f"""
        The user has provided feedback on their weekly workout plan. Please update the plan accordingly.

        CURRENT PLAN:
        {current_plan}

        USER FEEDBACK:
        {feedback}

        Please update the plan to address the feedback while maintaining:
        - Evidence-based principles
        - Minimalist approach
        - Safety and progression
        - Essential movement patterns

        Provide the updated plan in the same detailed format.
        """
        
        # Generate updated plan
        if self.agent:
            response = await self.agent.ainvoke({"messages": [("user", update_prompt)]})
            if isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
                if messages and hasattr(messages[-1], 'content'):
                    updated_plan = messages[-1].content
                else:
                    updated_plan = str(response)
            else:
                updated_plan = str(response)
        else:
            # Fallback to basic chain
            if self.retriever:
                def format_docs(docs):
                    return "\n\n".join(doc.page_content for doc in docs)
                
                chain = (
                    {"context": self.retriever | format_docs, "input": RunnablePassthrough()}
                    | self.prompt
                    | self.model
                    | StrOutputParser()
                )
                updated_plan = chain.invoke(update_prompt)
            else:
                chain = self.prompt | self.model | StrOutputParser()
                updated_plan = chain.invoke({"input": update_prompt})
        
        return updated_plan
    
    async def _create_routines_in_hevy(self, plan: str) -> None:
        """Create the routines in the user's Hevy app."""
        print("\n🏋️‍♂️ CREATING ROUTINES IN HEVY...")
        
        # First, check/create the weekly folder
        await self._ensure_weekly_folder_exists()
        
        # Parse the plan and create individual routines
        # This is a simplified version - you might want to enhance the parsing
        routines = self._parse_plan_into_routines(plan)
        
        for i, routine in enumerate(routines, 1):
            print(f"📝 Creating Routine {i}: {routine['title']}")
            try:
                # Format routine for Hevy API
                routine_payload = {"routine": routine}
                result = await self.mcp.create_routine(routine_payload)
                print(f"✅ Created: {routine['title']}")
            except Exception as e:
                print(f"❌ Failed to create {routine['title']}: {e}")
        
        print("\n🎉 All routines created successfully!")
    
    async def _ensure_weekly_folder_exists(self) -> None:
        """Ensure the weekly folder exists in Hevy."""
        # Get current week number (simplified - you might want to use proper date logic)
        import datetime
        week_num = datetime.datetime.now().isocalendar()[1]
        folder_name = f"Week {week_num}"
        
        # Check if folder exists
        try:
            folders_result = await self._get_routine_folders()
            if folder_name not in folders_result:
                print(f"📁 Creating folder: {folder_name}")
                folder_payload = {"routine_folder": {"title": folder_name}}
                await self.mcp.create_routine_folder(folder_payload)
            else:
                print(f"📁 Folder '{folder_name}' already exists")
        except Exception as e:
            print(f"⚠️ Could not check/create folder: {e}")
    
    async def _get_routine_folders(self) -> str:
        """Get routine folders from Hevy API."""
        try:
            if hasattr(self.mcp, 'mcp_tools') and self.mcp.mcp_tools:
                folders_tool = None
                for tool in self.mcp.mcp_tools:
                    if tool.name == "get_routine_folders":
                        folders_tool = tool
                        break
                
                if folders_tool:
                    result = await folders_tool.ainvoke({"page": 1, "pageSize": 10})
                    return result
                else:
                    return "Routine folders tool not available"
            else:
                return "MCP tools not loaded"
        except Exception as e:
            return f"Error retrieving routine folders: {e}"
    
    def _parse_plan_into_routines(self, plan: str) -> List[Dict[str, Any]]:
        """Parse the plan text into individual routine objects."""
        # This is a simplified parser - you might want to enhance this
        # to better extract workout details from the plan text
        
        routines = []
        lines = plan.split('\n')
        current_routine = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Day') or line.startswith('Workout') or line.startswith('Session'):
                if current_routine:
                    routines.append(current_routine)
                current_routine = {
                    "title": line,
                    "notes": "",
                    "exercises": []
                }
            elif current_routine and line:
                current_routine["notes"] += line + "\n"
        
        if current_routine:
            routines.append(current_routine)
        
        # If no routines were parsed, create a default one
        if not routines:
            routines.append({
                "title": "Weekly Plan",
                "notes": plan,
                "exercises": []
            })
        
        return routines
    
