import customtkinter as ctk
from typing import Dict, Type, Optional
from ..core import BaseTool, PluginManager

class ToolboxLauncher:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Tools")
        self.root.geometry("1000x700")
        
        self.plugin_manager = PluginManager()
        self.current_tool: Optional[BaseTool] = None
        self.current_tool_frame = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tools sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10), pady=0)
        
        # Sidebar title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Available Tools",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20, padx=10)
        
        # Tool buttons container
        self.tools_container = ctk.CTkFrame(self.sidebar)
        self.tools_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Content area
        self.content_area = ctk.CTkFrame(self.main_container)
        self.content_area.pack(side="left", fill="both", expand=True)
        
        # Welcome message
        self.show_welcome()
        
    def show_welcome(self):
        if self.current_tool_frame:
            self.current_tool_frame.destroy()
            
        welcome_frame = ctk.CTkFrame(self.content_area)
        welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="Welcome to Tools",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        welcome_label.pack(pady=(50, 20))
        
        desc_label = ctk.CTkLabel(
            welcome_frame,
            text="Select a tool from the sidebar to begin",
            font=ctk.CTkFont(size=16)
        )
        desc_label.pack()
        
        self.current_tool_frame = welcome_frame
        
    def add_tool(self, tool_class: Type[BaseTool]):
        tool = tool_class()
        self.plugin_manager.register_tool(tool_class)
        
        def tool_button_clicked():
            self.load_tool(tool.name)
            
        button = ctk.CTkButton(
            self.tools_container,
            text=tool.name,
            command=tool_button_clicked
        )
        button.pack(padx=5, pady=5, fill="x")
        
    def load_tool(self, tool_name: str):
        if self.current_tool_frame:
            self.current_tool_frame.destroy()
            
        tool_class = self.plugin_manager.get_tool(tool_name)
        if tool_class:
            self.current_tool = tool_class()
            self.current_tool_frame = self.current_tool.create_tool_gui(self.content_area)
            self.current_tool_frame.pack(fill="both", expand=True)
            
    def run(self):
        self.root.mainloop()