"""
AI Fitness Coach - Main Application Entry Point

This is the main entry point for the AI Fitness Coach application.
It creates and runs the console UI which handles all initialization.
"""

import asyncio
from ui import AsyncConsoleUI


async def main():
    """Main application entry point."""
    # Create and run the console UI
    ui = AsyncConsoleUI()
    await ui.run_async()


if __name__ == "__main__":
    asyncio.run(main())