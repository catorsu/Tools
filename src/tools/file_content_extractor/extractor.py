import os
import re
from typing import List, Tuple


class FileContentExtractor:
    def _get_language_from_extension(self, file_path: str) -> str:
        """Determines the language for a markdown code block from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".json": "json",
            ".xml": "xml",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".md": "markdown",
            ".sh": "bash",
            ".sql": "sql",
        }
        _, ext = os.path.splitext(file_path)
        return ext_map.get(ext.lower(), "")

    def extract_from_text(self, text: str, root_path: str) -> Tuple[str, List[str]]:
        """
        Extracts file paths from a <relevant_files> tag, reads their content,
        and returns the formatted content along with any files that were not found.

        Returns:
            A tuple containing:
            - The formatted string with all found file contents.
            - A list of file paths that were not found.
        """
        content_parts = []
        not_found_files = []

        match = re.search(r"<relevant_files>(.*?)</relevant_files>", text, re.DOTALL)
        if not match:
            return "", []

        content_str = match.group(1)
        paths = [p.strip() for p in content_str.split("\n") if p.strip()]

        if not paths:
            return "", []

        for rel_path in paths:
            # Sanitize path to prevent directory traversal attacks
            if ".." in rel_path.split(os.path.sep):
                not_found_files.append(f"{rel_path} (Invalid path)")
                continue

            full_path = os.path.join(root_path, rel_path)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                language = self._get_language_from_extension(rel_path)
                file_block = f"File: {rel_path}\n```{language}\n{content.rstrip()}\n```"
                content_parts.append(file_block)
            except FileNotFoundError:
                not_found_files.append(rel_path)
            except Exception as e:
                not_found_files.append(f"{rel_path} (Error reading: {e})")

        all_files_content = "\n\n".join(content_parts)

        if not all_files_content:
            return "", not_found_files

        final_output = f"<file_contents>\n{all_files_content}\n</file_contents>"

        return final_output, not_found_files
