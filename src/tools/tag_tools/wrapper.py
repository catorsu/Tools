# File: /home/cator/project/Tools/src/tools/tag_tools/wrapper.py
import re
from typing import List


class TagWrapper:
    def wrap_text(self, text: str, tag_name: str) -> str:
        """
        Wraps the entire input text within the specified tag.
        """
        if not tag_name:
            raise ValueError("Tag name cannot be empty.")

        # Basic validation for tag name
        if not re.match(r"^[a-zA-Z0-9_-]+$", tag_name):
            raise ValueError(
                "Tag name should be alphanumeric (can include '-' or '_') and have no spaces."
            )

        return f"<{tag_name}>\n{text.strip()}\n</{tag_name}>"
