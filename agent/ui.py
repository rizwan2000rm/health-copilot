"""
Console UI module for the AI Fitness Coach application.

This module contains the AsyncConsoleUI class that handles user interaction
and provides a command-line interface for the fitness coaching application.
"""

import os
from fitness_coach import FitnessCoach


class AsyncConsoleUI:
    """Async console UI for MCP integration."""
    
    def __init__(self, model_name: str = "qwen2.5:3b"):
        """
        Initialize the console UI.
        
        Args:
            model_name: The model name to use for the fitness coach
        """
        self.coach = FitnessCoach(model_name=model_name)
    
    def _setup_api_key(self):
        """Set up Hevy API key if not already configured."""
        if not os.getenv("HEVY_API_KEY"):
            print("⚠️  HEVY_API_KEY not found in environment variables.")
            print("   To enable workout tracking features, you need to set your Hevy API key.")
            print("   You can:")
            print("   1. Set it: export HEVY_API_KEY=your_key_here")
            print("   2. Run with: HEVY_API_KEY=your_key_here python3 main.py")
            print("   3. Or enter it now (will be used for this session only):")
            
            api_key = input("Enter your Hevy API key (or press Enter to skip): ").strip()
            if api_key:
                os.environ["HEVY_API_KEY"] = api_key
                print("✅ API key set for this session")
            else:
                print("❌ No API key provided. Workout tracking features will be limited.")
    
    async def run_async(self):
        """Run the console UI asynchronously."""
        print("🏋️‍♂️ AI Fitness Coach")
        print("=" * 40)
        
        # Set up API key if needed
        self._setup_api_key()
        
        # Initialize the fitness coach
        print("🤖 Initializing AI Fitness Coach...")
        
        # Set up knowledge base if context directory exists
        context_dir = os.path.join(os.path.dirname(__file__), "context")
        if os.path.exists(context_dir):
            print("📚 Setting up knowledge base...")
            knowledge_files = os.listdir(context_dir)
            print(f"📁 Available knowledge files: {knowledge_files}")
            self.coach.setup_knowledge_base(context_dir)
            print("✅ Knowledge base initialized")
        else:
            print(f"⚠️ Knowledge directory not found: {context_dir}")
        
        # Set up MCP agent with tools
        print("🔧 Setting up MCP agent with tools...")
        agent_setup_success = await self.coach.setup_agent()
        
        if agent_setup_success:
            print("✅ MCP agent successfully initialized with tools")
        else:
            print("⚠️ MCP agent setup failed, using knowledge base only")
        
        # Print system stats
        stats = self.coach.get_stats()
        print(f"\n📊 System Status:")
        print(f"   Model: {stats['model_name']}")
        print(f"   Knowledge Base: {'✅' if stats['has_retriever'] else '❌'}")
        print(f"   MCP Agent: {'✅' if stats['has_agent'] else '❌'}")
        print(f"   MCP Tools: {stats['tools_loaded']} tools loaded")
        print(f"   MCP Available: {'✅' if stats['mcp_available'] else '❌'}")
        
        print("\n💡 Features: AI coaching, workout tracking")
        print("\n" + "=" * 40)
        print("Type 'help' for commands, 'quit' to exit")
        print("=" * 40)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Keep up the great work!")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() in ['weekly plan', 'plan', 'create plan']:
                    await self._generate_weekly_plan()
                elif user_input:
                    print("🤖 Coach: ", end="", flush=True)
                    response = await self.coach.get_response(user_input)
                    print(response)
                else:
                    print("Please enter a question or command.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Keep up the great work!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def _generate_weekly_plan(self):
        """Generate a comprehensive weekly workout plan."""
        print("🏋️‍♂️ Generating your personalized weekly workout plan...")
        print("=" * 50)
        
        print("🤖 Coach: ", end="", flush=True)
        response = await self.coach.generate_weekly_plan()
        print(response)
    
    def _show_help(self):
        """Show available commands."""
        print("\n📋 Available Commands:")
        print("  help           - Show available commands")
        print("  weekly plan    - Generate personalized weekly plan")
        print("  quit/exit/q    - Exit the application")
        print("\n💡 You can also ask fitness questions directly!")
    
