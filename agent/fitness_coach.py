"""
AI Fitness Coach module.

This module contains the core AI coaching logic, including model initialization,
prompt templates, and response generation with document retrieval.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List, Union
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever
from document_processor import DocumentProcessor
from mcp_integration import MCPIntegration, MCPWorkoutManager


class FitnessCoach:
    """AI Fitness Coach that provides workout advice and guidance."""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        """
        Initialize the AI Fitness Coach.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self.model = ChatOllama(model=model_name, temperature=0.7)
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
        
        # Get response from the model
        referenced_files = []
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
                    # Extract source file information for logging
                    for doc in docs:
                        if 'source' in doc.metadata:
                            source_file = doc.metadata['source']
                            if source_file not in referenced_files:
                                referenced_files.append(source_file)
                    return "\n\n".join(doc.page_content for doc in docs)
                
                chain = (
                    {"context": self.retriever | format_docs, "input": RunnablePassthrough()}
                    | self.prompt
                    | self.model
                    | StrOutputParser()
                )
                response_text = chain.invoke(user_input)
                
                # Log referenced files if any
                if referenced_files:
                    print(f"📚 Referenced knowledge files: {referenced_files}")
            else:
                chain = self.prompt | self.model | StrOutputParser()
                response_text = chain.invoke({"input": user_input})
        
        
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
    
    
    
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dictionary containing system statistics
        """
        mcp_stats = self.mcp.get_stats()
        return {
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
        print("🏋️‍♂️ Weekly Planning System")
        print("=" * 30)
        
        # Step 1: Show user what we're building
        await self._show_planning_overview()
        
        # Step 2: Collect optional preferences
        preferences = await self._collect_user_preferences()
        
        # Step 3: Create initial plan
        plan = await self._generate_weekly_plan(preferences)
        
        # Step 4: Iterative feedback loop
        while True:
            print("\n" + "=" * 30)
            print("📋 YOUR WEEKLY PLAN")
            print("=" * 30)
            print(plan)
            
            feedback = input("\n🤔 What do you think? (Enter 'accept' to approve, or provide feedback): ").strip()
            
            if feedback.lower() in ['accept', 'yes', 'y', 'approve', 'good']:
                print("\n✅ Plan approved! Creating routines...")
                await self._create_routines_in_hevy(plan)
                return plan
            
            elif feedback.lower() in ['skip', 'cancel', 'exit']:
                print("\n❌ Planning cancelled.")
                return "Planning cancelled by user."
            
            else:
                print(f"\n🔄 Updating plan...")
                plan = await self._update_plan_based_on_feedback(plan, feedback)
    
    async def _show_planning_overview(self) -> None:
        """Show user what we're building and explain the process."""
        print("\n🎯 Creating personalized weekly plan...")
        print("📊 Analyzing workout history → 📚 Applying training principles → 🏋️‍♂️ Creating routines")
        
        input("\nPress Enter to continue...")
    
    async def _collect_user_preferences(self) -> Dict[str, Any]:
        """Collect optional user preferences for the weekly plan."""
        print("\n🎯 Optional preferences (press Enter to skip):")
        
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
        
        print("✅ Moving to plan creation...")
        return preferences
    
    async def _generate_weekly_plan(self, preferences: Dict[str, Any]) -> str:
        """Generate the initial weekly plan using MCP tools and knowledge base."""
        print("\n🔍 Analyzing workout history...")
        
        # Get recent workouts with detailed logging
        recent_workouts = await self.mcp.get_workout_history(page=1, page_size=10)
        print(f"📊 Retrieved workout data: {recent_workouts[:200]}..." if len(recent_workouts) > 200 else f"📊 Retrieved workout data: {recent_workouts}")
        
        # Get exercise templates for analysis
        exercise_templates = await self._get_exercise_templates()
        print(f"🏋️‍♂️ Retrieved exercise templates: {exercise_templates[:200]}..." if len(exercise_templates) > 200 else f"🏋️‍♂️ Retrieved exercise templates: {exercise_templates}")
        
        # Get scientific context with detailed logging
        scientific_context = ""
        referenced_files = []
        if self.retriever:
            try:
                docs = self.retriever.invoke("minimalist training weekly plan compound movements")
                scientific_context = "\n\n".join([doc.page_content for doc in docs])
                
                # Extract source file information
                for doc in docs:
                    if 'source' in doc.metadata:
                        source_file = doc.metadata['source']
                        if source_file not in referenced_files:
                            referenced_files.append(source_file)
                
                print(f"📚 Referenced knowledge files: {referenced_files}")
                print(f"📖 Retrieved scientific context: {scientific_context[:200]}..." if len(scientific_context) > 200 else f"📖 Retrieved scientific context: {scientific_context}")
            except Exception as e:
                print(f"⚠️ Error retrieving scientific context: {e}")
        
        # Create the planning prompt
        planning_prompt = f"""
        You are creating a personalized weekly workout plan. Here's the data:

        RECENT WORKOUTS (Last 10 days):
        {recent_workouts}

        EXERCISE TEMPLATES AVAILABLE:
        {exercise_templates}

        USER PREFERENCES:
        {preferences}

        SCIENTIFIC CONTEXT (from knowledge files: {referenced_files}):
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
        - References to knowledge base files used: {referenced_files}
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
                    print("🔍 Fetching exercise templates from API...")
                    result = await templates_tool.ainvoke({"page": 1, "pageSize": 50})
                    print("✅ Exercise templates retrieved")
                    return result
                else:
                    error_msg = "Exercise templates tool not available"
                    return error_msg
            else:
                error_msg = "MCP tools not loaded"
                return error_msg
        except Exception as e:
            error_msg = f"Error retrieving exercise templates: {e}"
            return error_msg
    
    async def _get_exercise_template_mapping(self) -> Dict[str, str]:
        """Get a mapping of exercise names to template IDs."""
        try:
            templates_result = await self._get_exercise_templates()
            if "Error" in templates_result or "not available" in templates_result:
                fallback_mapping = self._get_fallback_exercise_mapping()
                return fallback_mapping
            
            import json
            templates_data = json.loads(templates_result)
            exercise_templates = templates_data.get("exercise_templates", [])
            
            mapping = {}
            for template in exercise_templates:
                title = template.get("title", "").lower()
                template_id = template.get("id", "")
                
                # Create multiple mappings for common variations
                if "bench" in title and "press" in title:
                    mapping["bench press"] = template_id
                    mapping["bench"] = template_id
                elif "squat" in title:
                    mapping["squat"] = template_id
                elif "deadlift" in title:
                    mapping["deadlift"] = template_id
                elif "pull" in title and "up" in title:
                    mapping["pull-up"] = template_id
                    mapping["pullup"] = template_id
                elif "push" in title and "up" in title:
                    mapping["push-up"] = template_id
                    mapping["pushup"] = template_id
                elif "curl" in title and "bicep" in title:
                    mapping["bicep curl"] = template_id
                    mapping["curl"] = template_id
                elif "press" in title and ("shoulder" in title or "military" in title):
                    mapping["shoulder press"] = template_id
                    mapping["military press"] = template_id
                elif "lateral" in title and "raise" in title:
                    mapping["lateral raise"] = template_id
                elif "row" in title:
                    mapping["row"] = template_id
                elif "lunge" in title:
                    mapping["lunge"] = template_id
                elif "plank" in title:
                    mapping["plank"] = template_id
                elif "sit" in title and "up" in title:
                    mapping["sit-up"] = template_id
                    mapping["situp"] = template_id
            
            print("✅ Exercise template mapping created")
            return mapping
        except Exception as e:
            print(f"Error creating exercise mapping: {e}")
            fallback_mapping = self._get_fallback_exercise_mapping()
            return fallback_mapping
    
    def _get_fallback_exercise_mapping(self) -> Dict[str, str]:
        """Fallback exercise mapping when API is not available."""
        return {
            'bench press': '07B38369',  # Incline Bench Press (Dumbbell)
            'squat': '5E1A7777',  # Lunge
            'deadlift': 'D57C2EC7',  # Hip Thrust (Barbell)
            'pull-up': '1B2B1E7C',  # Pull Up
            'push-up': '022DF610',  # Sit Up
            'bicep curl': '3BC06AD3',  # 21s Bicep Curl
            'shoulder press': 'A69FF221',  # Arnold Press (Dumbbell)
            'lateral raise': '422B08F1',  # Lateral Raise (Dumbbell)
            'row': '1B2B1E7C',  # Pull Up
            'lunge': '5E1A7777',  # Lunge
            'plank': '022DF610',  # Sit Up
        }
    
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
        
        # First, check/create the weekly folder and get its ID
        folder_id = await self._ensure_weekly_folder_exists()
        
        if folder_id is None:
            print("⚠️ Could not create or find weekly folder, creating routines without folder assignment")
        
        # Parse the plan and create individual routines with folder assignment
        routines = await self._parse_plan_into_routines(plan, folder_id)
        
        for i, routine in enumerate(routines, 1):
            print(f"📝 Creating Routine {i}: {routine['title']}")
            if folder_id:
                print(f"📁 Assigning to folder ID: {folder_id}")
            else:
                print("⚠️ No folder ID available - routine will be created without folder assignment")
            
            try:
                # Format routine for Hevy API
                routine_payload = {"routine": routine}
                result = await self.mcp.create_routine(routine_payload)
                print(f"✅ Created: {routine['title']}")
                
                # Log the routine payload for debugging
                print(f"🔍 Routine payload: {routine_payload}")
            except Exception as e:
                print(f"❌ Failed to create {routine['title']}: {e}")
                print(f"🔍 Failed routine payload: {routine_payload}")
        
        print("\n🎉 All routines created successfully!")
    
    async def _ensure_weekly_folder_exists(self) -> Optional[int]:
        """Ensure the weekly folder exists in Hevy and return its ID."""
        # Get current week number (simplified - you might want to use proper date logic)
        import datetime
        week_num = datetime.datetime.now().isocalendar()[1]
        folder_name = f"Week {week_num}"
        
        # Check if folder exists
        try:
            folders_result = await self._get_routine_folders()
            
            # Parse the folders result to find existing folder
            folder_id = await self._find_folder_id_by_name(folders_result, folder_name)
            
            if folder_id is None:
                print(f"📁 Creating folder: {folder_name}")
                folder_payload = {"routine_folder": {"title": folder_name}}
                result = await self.mcp.create_routine_folder(folder_payload)
                
                # Try to extract folder ID from creation result
                folder_id = await self._extract_folder_id_from_result(result)
                if folder_id:
                    print(f"✅ Created folder '{folder_name}' with ID: {folder_id}")
                else:
                    print(f"⚠️ Created folder '{folder_name}' but couldn't get ID")
            else:
                print(f"📁 Folder '{folder_name}' already exists with ID: {folder_id}")
            
            return folder_id
        except Exception as e:
            print(f"⚠️ Could not check/create folder: {e}")
            return None
    
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
    
    async def _find_folder_id_by_name(self, folders_result: str, folder_name: str) -> Optional[int]:
        """Find folder ID by name in the folders result."""
        try:
            import json
            folders_data = json.loads(folders_result)
            folders = folders_data.get("routine_folders", [])
            
            for folder in folders:
                if folder.get("title") == folder_name:
                    return folder.get("id")
            return None
        except Exception as e:
            print(f"⚠️ Error parsing folders result: {e}")
            return None
    
    async def _extract_folder_id_from_result(self, result: str) -> Optional[int]:
        """Extract folder ID from creation result."""
        try:
            import json
            result_data = json.loads(result)
            # The result might be in different formats, try common patterns
            if "routine_folder" in result_data:
                return result_data["routine_folder"].get("id")
            elif "id" in result_data:
                return result_data["id"]
            elif "folder" in result_data:
                return result_data["folder"].get("id")
            return None
        except Exception as e:
            print(f"⚠️ Error extracting folder ID from result: {e}")
            return None
    
    async def _parse_plan_into_routines(self, plan: str, folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Parse the plan text into individual routine objects with proper exercises."""
        routines = []
        lines = plan.split('\n')
        current_routine = None
        
        for line in lines:
            line = line.strip()
            # Check for day headers
            if (line.startswith('Day') or line.startswith('Workout') or line.startswith('Session') or 
                line.startswith('Monday') or line.startswith('Tuesday') or line.startswith('Wednesday') or 
                line.startswith('Thursday') or line.startswith('Friday') or line.startswith('Saturday') or 
                line.startswith('Sunday') or '**Monday' in line or '**Tuesday' in line or '**Wednesday' in line or
                '**Thursday' in line or '**Friday' in line or '**Saturday' in line or '**Sunday' in line):
                if current_routine:
                    routines.append(current_routine)
                current_routine = {
                    "title": line.replace('*', '').strip(),
                    "folder_id": folder_id,  # Use the provided folder_id
                    "notes": "",
                    "exercises": []
                }
            elif current_routine and line:
                # Check if this line contains exercise information
                exercise_info = await self._extract_exercise_from_line(line)
                if exercise_info:
                    current_routine["exercises"].append(exercise_info)
                else:
                    current_routine["notes"] += line + "\n"
        
        if current_routine:
            routines.append(current_routine)
        
        # If no routines were parsed, create a default one with a sample exercise
        if not routines:
            routines.append({
                "title": "Weekly Plan",
                "folder_id": folder_id,  # Use the provided folder_id
                "notes": plan,
                "exercises": [self._get_default_exercise()]
            })
        
        # Ensure each routine has at least one exercise
        for routine in routines:
            if not routine["exercises"]:
                routine["exercises"] = [self._get_default_exercise()]
        
        return routines
    
    async def _extract_exercise_from_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract exercise information from a line of text."""
        # Get dynamic exercise mapping
        exercise_patterns = await self._get_exercise_template_mapping()
        
        line_lower = line.lower()
        
        # Skip lines that are clearly not exercises
        if any(skip_word in line_lower for skip_word in ['**', '|', '---', 'day', 'focus area', 'summary', 'analysis']):
            return None
        
        for exercise_name, template_id in exercise_patterns.items():
            if exercise_name in line_lower:
                # Extract sets and reps if mentioned
                sets = 3  # default
                reps = 10  # default
                
                # Look for patterns like "3 sets of 8-12 reps" or "3x8-12"
                import re
                sets_match = re.search(r'(\d+)\s*sets?', line_lower)
                if sets_match:
                    sets = int(sets_match.group(1))
                
                reps_match = re.search(r'(\d+)(?:-(\d+))?\s*reps?', line_lower)
                if reps_match:
                    reps = int(reps_match.group(1))
                
                print(f"🔍 Found exercise: {exercise_name} -> {template_id} ({sets} sets, {reps} reps)")
                
                return {
                    "exercise_template_id": template_id,
                    "sets": [
                        {
                            "type": "normal",
                            "weight_kg": 0,  # Default weight, user can adjust
                            "reps": reps,
                            "distance_meters": 0,
                            "duration_seconds": 0,
                            "custom_metric": 0
                        }
                        for _ in range(sets)
                    ],
                    "rest_seconds": 90  # Default rest
                }
        
        return None
    
    def _get_default_exercise(self) -> Dict[str, Any]:
        """Get a default exercise for routines that don't have any exercises."""
        return {
            "exercise_template_id": "3BC06AD3",  # 21s Bicep Curl
            "sets": [
                {
                    "type": "normal",
                    "weight_kg": 0,
                    "reps": 10,
                    "distance_meters": 0,
                    "duration_seconds": 0,
                    "custom_metric": 0
                }
            ],
            "rest_seconds": 60
        }
    
