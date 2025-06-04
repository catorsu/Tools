"""
Main entry point for the Tools application
"""

import sys
import os
import customtkinter as ctk

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.gui import ToolboxLauncher
from src.tools.crawler import CrawlerTool
from src.tools.mdblock import MarkdownBlockTool
from src.tools.git_diff import GitDiffTool

def main():
    """Main function"""
    try:
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create and setup launcher
        launcher = ToolboxLauncher()
        
        # Register tools
        launcher.add_tool(CrawlerTool)
        launcher.add_tool(MarkdownBlockTool)
        launcher.add_tool(GitDiffTool)
        
        # Run application
        launcher.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()