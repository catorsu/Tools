"""
Main entry point for the Tools application
"""

import sys
import os
import customtkinter as ctk

# import re  # Added for TagContentExtractorFrame validation - This import is not needed here

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.gui import ToolboxLauncher
from src.tools.crawler import CrawlerTool
from src.tools.mdblock import MarkdownBlockTool
from src.tools.git_diff import GitDiffTool
from src.tools.reddit_reducer import RedditReducerTool
from src.tools.file_content_extractor import FileContentExtractorTool

# from src.tools.tag_content_extractor import TagContentExtractorTool # Removed
# from src.tools.tag_renamer import TagRenamerTool # Removed
from src.tools.tag_tools import TagToolsMainTool  # New consolidated tool


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
        launcher.add_tool(TagToolsMainTool)  # Register the new consolidated tool
        launcher.add_tool(RedditReducerTool)
        launcher.add_tool(FileContentExtractorTool)

        # Run application
        launcher.run()

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
