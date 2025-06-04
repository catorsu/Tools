import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseToolFrame(ctk.CTkFrame, ABC):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tool_options: Dict[str, Any] = {}
        self.setup_ui()
        
    @abstractmethod
    def setup_ui(self) -> None:
        """Set up the tool's user interface"""
        pass
        
    @abstractmethod
    def get_options(self) -> Dict[str, Any]:
        """Get the current tool options from UI"""
        pass
        
    @abstractmethod
    def set_options(self, options: Dict[str, Any]) -> None:
        """Set tool options in UI"""
        pass
        
    @abstractmethod
    def clear(self) -> None:
        """Clear all inputs and results"""
        pass
        
    def show_error(self, message: str) -> None:
        """Show error message"""
        pass
        
    def show_success(self, message: str) -> None:
        """Show success message"""
        pass