"""
Console UI module for the AI Fitness Coach application.

This module contains the AsyncConsoleUI class that handles user interaction
and provides a command-line interface for the fitness coaching application.
"""

import os
from fitness_coach import FitnessCoach


class AsyncConsoleUI:
    """Async console UI for MCP integration."""
    
    def __init__(self, coach: FitnessCoach):
        """
        Initialize the console UI.
        
        Args:
            coach: The FitnessCoach instance to use for responses
        """
        self.coach = coach
    
    async def run_async(self):
        """Run the console UI asynchronously."""
        print("🏋️‍♂️ AI Fitness Coach")
        print("=" * 40)
        
        # Set up knowledge base
        context_dir = os.path.join(os.path.dirname(__file__), "context")
        print(f"📁 Setting up knowledge base from: {context_dir}")
        
        # List available knowledge files
        if os.path.exists(context_dir):
            knowledge_files = os.listdir(context_dir)
            print(f"📚 Available knowledge files: {knowledge_files}")
        else:
            print(f"❌ Knowledge directory not found: {context_dir}")
        
        self.coach.setup_knowledge_base(context_dir)
        
        # Set up agent with MCP tools
        await self.coach.setup_agent()
        
        print("\n💡 Features: AI coaching, workout tracking")
        
        if self.coach.mcp.has_tools():
            tool_count = len(self.coach.mcp.get_tool_names())
            print(f"🔧 {tool_count} MCP tools loaded")
        
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
                    await self._create_weekly_plan()
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
    
    def _show_help(self):
        """Show available commands."""
        print("\n📋 Available Commands:")
        print("  help           - Show available commands")
        print("  weekly plan    - Generate personalized weekly plan")
        print("  quit/exit/q    - Exit the application")
        print("\n💡 You can also ask fitness questions directly!")
    
    async def _create_weekly_plan(self):
        """Create a personalized weekly plan."""
        print("\n🏋️‍♂️ Starting Weekly Planning Process...")
        try:
            plan = await self.coach.create_weekly_plan()
            print(f"\n🎉 Weekly planning completed!")
            print(f"Final plan:\n{plan}")
        except Exception as e:
            print(f"❌ Error creating weekly plan: {e}")
            print("Please make sure MCP tools are properly configured.")
