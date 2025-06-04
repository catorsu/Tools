from typing import Dict, Type, List
from .base_tool import BaseTool

class PluginManager:
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}
        
    def register_tool(self, tool_class: Type[BaseTool]) -> None:
        """Register a new tool class"""
        tool = tool_class()
        self._tools[tool.name] = tool_class
        
    def get_tool(self, name: str) -> Type[BaseTool]:
        """Get a tool class by name"""
        return self._tools.get(name)
        
    def get_all_tools(self) -> List[Type[BaseTool]]:
        """Get all registered tool classes"""
        return list(self._tools.values())
        
    def get_tool_names(self) -> List[str]:
        """Get names of all registered tools"""
        return list(self._tools.keys())