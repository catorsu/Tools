from typing import Dict, Any

from ...core import BaseTool
from .reducer import RedditReducer
from .gui import RedditReducerFrame


class RedditReducerTool(BaseTool[RedditReducerFrame]):
    def __init__(self):
        super().__init__()
        self.reducer_logic = RedditReducer()

    def get_tool_name(self) -> str:
        return "Reddit JSON Reducer"

    def get_tool_description(self) -> str:
        return "Simplifies and filters raw JSON from Reddit threads."

    def get_tool_options(self) -> Dict[str, Any]:
        return {}  # No configurable options for this tool

    def create_tool_gui(self, parent) -> RedditReducerFrame:
        return RedditReducerFrame(parent, tool_logic=self)
