import re
from typing import List


class ContentExtractor:
    def extract_content(self, text: str, tag_name: str) -> List[str]:
        """
        Extracts content from within specified tags.
        Example: <tag_name>content to extract</tag_name>
        This is a simple implementation and does not handle complex XML/HTML
        or nested tags of the same name perfectly. It's best for simple, distinct tags.
        """
        if not tag_name:
            return []

        # Escape tag_name in case it contains regex special characters,
        # though typical tag names are usually safe.
        escaped_tag_name = re.escape(tag_name)

        # Regex to find content: <tag>content</tag>
        # It's non-greedy (.*?) to handle multiple tags on the same line correctly.
        # re.DOTALL allows '.' to match newline characters.
        pattern = re.compile(
            f"<{escaped_tag_name}>(.*?)</{escaped_tag_name}>", re.DOTALL
        )
        matches = pattern.findall(text)
        return matches
