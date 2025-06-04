import os
import json
from typing import Dict, Any, Optional

from core.base_tool import BaseTool
from .gui import GitDiffFrame

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

class GitDiffTool(BaseTool[GitDiffFrame]):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        
    def get_tool_name(self) -> str:
        return "Git Diff Tool"
        
    def get_tool_description(self) -> str:
        return "Get git diff output with custom XML-like wrapping"
        
    def get_tool_options(self) -> Dict[str, Any]:
        return {
            "repo_path": self.config.get("default_repo_path", ""),
            "wrapper_tag": "code_changes"
        }
        
    def create_tool_gui(self, parent) -> GitDiffFrame:
        return GitDiffFrame(parent, self.config, tool=self)
        
    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    if 'custom_tags' not in config:
                        config['custom_tags'] = ["code_changes"]
                    return config
            except:
                pass
        return {"default_repo_path": "", "custom_tags": ["code_changes"]}
        
    def save_config(self) -> None:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)