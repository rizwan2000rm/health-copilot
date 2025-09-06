"""
AI Fitness Coach - Main Application Entry Point

This is the main entry point for the AI Fitness Coach application.
It orchestrates the modular components to provide a complete fitness coaching experience.
"""

import os
from fitness_coach import FitnessCoach
from console_ui import ConsoleUI

def main():
    """Main application entry point."""
    # Initialize the AI Fitness Coach
    coach = FitnessCoach(model_name="llama3.2:3b")
    
    # Set up knowledge base from context directory
    context_dir = os.path.join(os.path.dirname(__file__), "context")
    coach.setup_knowledge_base(context_dir)
    
    # Initialize and run the console UI
    ui = ConsoleUI(coach)
    ui.run()

if __name__ == "__main__":
    main()