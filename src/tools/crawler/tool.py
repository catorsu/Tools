from typing import Dict, Any
from ...core import BaseTool
from .sublink_crawler import SublinkCrawler
from .gui import CrawlerToolFrame


class CrawlerTool(BaseTool[CrawlerToolFrame]):
    def __init__(self):
        self.crawler = SublinkCrawler()
        super().__init__()

    def get_tool_name(self) -> str:
        return "Sublink Crawler"

    def get_tool_description(self) -> str:
        return "Extract and analyze links from web pages"

    def get_tool_options(self) -> Dict[str, Any]:
        return {
            "start_url": "",
            "url_prefix": None,
            "max_depth": 2,
            "max_pages": 100,
            "request_delay": 1.0,
            "user_agent": None,
        }

    def create_tool_gui(self, parent) -> CrawlerToolFrame:
        return CrawlerToolFrame(parent, crawler=self.crawler)
