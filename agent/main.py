"""
AI Fitness Coach - Main Application Entry Point with MCP Integration

This is the main entry point for the AI Fitness Coach application.
It orchestrates the modular components to provide a complete fitness coaching experience
with MCP tool integration for workout tracking.
"""

import os
import asyncio
from fitness_coach import FitnessCoach


class AsyncConsoleUI:
    """Async console UI for MCP integration."""
    
    def __init__(self, coach):
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
                elif user_input.lower() == 'stats':
                    self._show_stats()
                elif user_input.lower() == 'workouts':
                    await self._show_workout_history()
                elif user_input.lower() == 'summary':
                    await self._show_workout_summary()
                elif user_input.lower().startswith('create workout'):
                    await self._create_workout_interactive()
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
        print("  help           - Show this help message")
        print("  stats          - Show system statistics")
        print("  workouts       - Show workout history")
        print("  summary        - Show workout summary")
        print("  create workout - Create a new workout")
        print("  weekly plan    - Create personalized weekly plan")
        print("  quit/exit/q    - Exit the application")
        print("\n💡 You can also ask fitness questions directly!")
    
    def _show_stats(self):
        """Show system statistics."""
        stats = self.coach.get_stats()
        print(f"\n📊 System Statistics:")
        print(f"  Model: {stats['model_name']}")
        print(f"  Knowledge base: {'✅' if stats['has_retriever'] else '❌'}")
        print(f"  MCP tools: {'✅' if stats['tools_loaded'] > 0 else '❌'}")
        print(f"  MCP available: {'✅' if stats['mcp_available'] else '❌'}")
        
        # Show available knowledge files
        context_dir = os.path.join(os.path.dirname(__file__), "context")
        if os.path.exists(context_dir):
            knowledge_files = os.listdir(context_dir)
            print(f"  Knowledge files: {len(knowledge_files)} files")
            for file in knowledge_files:
                print(f"    - {file}")
        
        # Show MCP tool names if available
        if stats['tools_loaded'] > 0:
            print(f"  Available MCP tools:")
            for tool_name in stats['tool_names']:
                print(f"    - {tool_name}")
    
    async def _show_workout_history(self):
        """Show workout history using MCP tools."""
        print("📋 Fetching workout history...")
        history = await self.coach.mcp.get_workout_history()
        print(f"\n{history}")
    
    async def _show_workout_summary(self):
        """Show workout summary using MCP tools."""
        print("📊 Fetching workout summary...")
        summary = await self.coach.workout_manager.get_workout_summary()
        print(f"\n{summary}")
    
    async def _create_workout_interactive(self):
        """Interactive workout creation."""
        print("\n🏋️‍♂️ Create New Workout")
        print("=" * 30)
        
        name = input("Workout name: ").strip()
        if not name:
            print("❌ Workout name is required")
            return
        
        notes = input("Notes (optional): ").strip()
        
        print("📝 Creating workout...")
        result = await self.coach.workout_manager.create_simple_workout(name, notes)
        print(f"\n{result}")
    
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


async def main():
    """Main application entry point."""
    # Check for Hevy API key
    import os
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
    
    # Initialize the AI Fitness Coach
    coach = FitnessCoach(model_name="llama3.2:3b")
    
    # Initialize and run the async console UI
    ui = AsyncConsoleUI(coach)
    await ui.run_async()


if __name__ == "__main__":
    asyncio.run(main())