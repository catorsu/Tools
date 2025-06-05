# src/tools/tag_renamer/renamer.py
import re
from typing import List


class TagRenamer:
    def rename_tag(self, text: str, old_tag_name: str, new_tag_name: str) -> str:
        """
        Renames occurrences of <old_tag_name>...</old_tag_name> to <new_tag_name>...</new_tag_name>.
        This function performs a simple regex-based replacement and does not parse complex XML/HTML
        or handle nested tags of the same name perfectly. It's best for simple, distinct tags.
        """
        if not old_tag_name or not new_tag_name:
            raise ValueError("Old and new tag names cannot be empty.")
        if old_tag_name == new_tag_name:
            return text  # No change needed if names are the same

        # Escape tag names for regex safety
        escaped_old_tag = re.escape(old_tag_name)
        escaped_new_tag = re.escape(new_tag_name)

        # Pattern to match opening tag: <old_tag_name>
        # Using word boundaries \b to ensure it matches whole tag names, not partials (e.g., <content> vs <content_type>)
        open_tag_pattern = re.compile(r"<" + escaped_old_tag + r"\b")
        text = open_tag_pattern.sub(f"<{escaped_new_tag}", text)

        # Pattern to match closing tag: </old_tag_name>
        close_tag_pattern = re.compile(r"</" + escaped_old_tag + r"\b")
        text = close_tag_pattern.sub(f"</{escaped_new_tag}", text)

        return text
