"""
AI Fitness Coach - Main Application Entry Point with MCP Integration

This is the main entry point for the AI Fitness Coach application.
It orchestrates the modular components to provide a complete fitness coaching experience
with MCP tool integration for workout tracking.
"""

import os
import asyncio
from fitness_coach import FitnessCoach
from ui import AsyncConsoleUI


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