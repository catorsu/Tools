from typing import Dict, Any
from ...core import BaseTool
from .block_extractor import BlockExtractor
from .gui import BlockExtractorFrame

class MarkdownBlockTool(BaseTool[BlockExtractorFrame]):
    def __init__(self):
        self.extractor = BlockExtractor()
        super().__init__()
        
    def get_tool_name(self) -> str:
        return "Markdown Block Extractor"
        
    def get_tool_description(self) -> str:
        return "Extract content from nested Markdown code blocks"
        
    def get_tool_options(self) -> Dict[str, Any]:
        return {
            "block_type": "text",
            "target_layer": 1,
            "custom_start": "",
            "custom_end": ""
        }
        
    def create_tool_gui(self, parent) -> BlockExtractorFrame:
        return BlockExtractorFrame(parent, extractor=self.extractor)