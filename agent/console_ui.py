"""
Console UI module for the AI Fitness Coach.

This module handles all user interface interactions, including input/output,
loading animations, and the main interaction loop.
"""

import threading
import time
from typing import Optional
from fitness_coach import FitnessCoach


class ConsoleUI:
    """Console-based user interface for the AI Fitness Coach."""
    
    def __init__(self, coach: FitnessCoach):
        """
        Initialize the console UI.
        
        Args:
            coach: The FitnessCoach instance to use for responses
        """
        self.coach = coach
        self.loading_thread: Optional[threading.Thread] = None
        self._stop_loading = False
    
    def show_loading(self) -> None:
        """Show a simple loading animation."""
        loading_chars = "|/-\\"
        i = 0
        while not self._stop_loading:
            print(f"\r🤖 AI Coach: Thinking {loading_chars[i % len(loading_chars)]}", end="", flush=True)
            time.sleep(0.1)
            i += 1
    
    def start_loading(self) -> None:
        """Start the loading animation."""
        self._stop_loading = False
        self.loading_thread = threading.Thread(target=self.show_loading)
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def stop_loading(self) -> None:
        """Stop the loading animation."""
        self._stop_loading = True
        if self.loading_thread:
            self.loading_thread.join()
        print("\r🤖 AI Coach: ", end="", flush=True)
    
    def display_welcome(self) -> None:
        """Display the welcome message."""
        print("🏋️ Welcome to your AI Fitness Coach!")
        print("Ask me about workouts, exercises, or fitness advice. Type 'quit' to exit.\n")
    
    def display_goodbye(self) -> None:
        """Display the goodbye message."""
        print("Thanks for using the AI Fitness Coach! Stay strong! 💪")
    
    def display_error(self, error: str) -> None:
        """
        Display an error message.
        
        Args:
            error: The error message to display
        """
        print(f"\n❌ Error: {error}")
        print("Please try again or type 'quit' to exit.\n")
    
    def display_response(self, response: str, is_cached: bool = False) -> None:
        """
        Display the AI coach's response.
        
        Args:
            response: The response to display
            is_cached: Whether this response was cached
        """
        prefix = "⚡" if is_cached else ""
        print(f"{prefix} AI Coach: {response}")
        print("\n" + "="*50 + "\n")
    
    def get_user_input(self) -> str:
        """
        Get input from the user.
        
        Returns:
            The user's input string
        """
        return input("You: ").strip()
    
    def is_exit_command(self, user_input: str) -> bool:
        """
        Check if the user input is an exit command.
        
        Args:
            user_input: The user's input
            
        Returns:
            True if it's an exit command, False otherwise
        """
        return user_input.lower() in ['quit', 'exit', 'bye']
    
    def is_empty_input(self, user_input: str) -> bool:
        """
        Check if the user input is empty.
        
        Args:
            user_input: The user's input
            
        Returns:
            True if input is empty, False otherwise
        """
        return not user_input
    
    def run(self) -> None:
        """Run the main interaction loop."""
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                # Check for exit command
                if self.is_exit_command(user_input):
                    self.display_goodbye()
                    break
                
                # Skip empty inputs
                if self.is_empty_input(user_input):
                    continue
                
                # Check cache first for faster response
                cached_response = self.coach.get_cached_response(user_input)
                if cached_response:
                    self.display_response(cached_response, is_cached=True)
                    continue
                
                # Start loading animation
                self.start_loading()
                
                try:
                    # Get response from the coach
                    response = self.coach.get_response(user_input)
                finally:
                    # Stop loading animation
                    self.stop_loading()
                
                # Display the response
                self.display_response(response)
                
            except KeyboardInterrupt:
                print("\n")
                self.display_goodbye()
                break
            except Exception as e:
                self.display_error(str(e))
