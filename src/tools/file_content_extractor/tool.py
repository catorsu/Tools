import os
import re
from typing import Dict, Any, List

from ...core import BaseTool
from .gui import FileContentExtractorFrame


class FileContentExtractorTool(BaseTool[FileContentExtractorFrame]):
    def get_tool_name(self) -> str:
        return "File Content Extractor"

    def get_tool_description(self) -> str:
        return "Extracts contents of files listed in a <relevant_files> tag."

    def get_tool_options(self) -> Dict[str, Any]:
        return {"base_path": "", "input_text": ""}

    def create_tool_gui(self, parent) -> FileContentExtractorFrame:
        return FileContentExtractorFrame(parent, tool_logic=self)

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

    def extract_and_read_files(self, text: str, base_path: str) -> Dict[str, Any]:
        """
        Parses text to find file paths within a <relevant_files> tag, reads them,
        and returns the concatenated content along with a report.
        """
        pattern = re.compile(r"<relevant_files>(.*?)</relevant_files>", re.DOTALL)
        match = pattern.search(text)

        if not match:
            return {
                "concatenated": "No <relevant_files> tag found in input.",
                "total": 0,
                "found": 0,
                "not_found": [],
            }

        file_list_str = match.group(1).strip()
        file_paths = [
            line.strip() for line in file_list_str.splitlines() if line.strip()
        ]

        if not file_paths:
            return {
                "concatenated": "The <relevant_files> tag is empty.",
                "total": 0,
                "found": 0,
                "not_found": [],
            }

        total_files = len(file_paths)
        found_files_count = 0
        not_found_files: List[str] = []
        content_parts: List[str] = []

        norm_base_path = os.path.normpath(base_path)

        for file_path in file_paths:
            # Prevent path traversal attacks
            if ".." in file_path.split(os.path.sep):
                not_found_files.append(f"{file_path} (Invalid path)")
                continue

            full_path = os.path.normpath(os.path.join(norm_base_path, file_path))

            # Ensure the path is within the base_path
            if not full_path.startswith(norm_base_path):
                not_found_files.append(f"{file_path} (Path is outside base directory)")
                continue

            if os.path.isfile(full_path):
                found_files_count += 1
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    language = self._get_language_from_extension(file_path)
                    file_block = (
                        f"File: {file_path}\n```{language}\n{content.rstrip()}\n```"
                    )
                    content_parts.append(file_block)
                except Exception as e:
                    not_found_files.append(f"{file_path} (Error reading: {e})")
            else:
                not_found_files.append(file_path)

        all_files_content = "\n\n".join(content_parts)

        if all_files_content:
            concatenated_content = (
                f"<file_contents>\n{all_files_content}\n</file_contents>"
            )
        else:
            concatenated_content = "No files were found or read."

        return {
            "concatenated": concatenated_content,
            "total": total_files,
            "found": found_files_count,
            "not_found": not_found_files,
        }
