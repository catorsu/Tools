from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, TypeVar, Generic

T = TypeVar('T')  # For the GUI frame type

class BaseTool(ABC, Generic[T]):
    def __init__(self):
        self.name: str = self.get_tool_name()
        self.description: str = self.get_tool_description()
        
    @abstractmethod
    def get_tool_name(self) -> str:
        """Return the name of the tool"""
        pass
        
    @abstractmethod
    def get_tool_description(self) -> str:
        """Return a description of what the tool does"""
        pass
        
    @abstractmethod
    def get_tool_options(self) -> Dict[str, Any]:
        """Return a dictionary of configurable options for the tool"""
        pass
        
    @abstractmethod
    def create_tool_gui(self, parent) -> T:
        """Create and return the tool's GUI frame"""
        pass