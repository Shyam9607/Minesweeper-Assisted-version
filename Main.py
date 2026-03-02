"""
Main entry point for the Minesweeper game application.

This file initializes the App class and starts the game loop.
Separating the entry point helps maintain modularity and clarity.
"""

from app import App

if __name__ == "__main__":
    # Create the main application instance
    app = App()
    
    # Start the game loop
    app.run()