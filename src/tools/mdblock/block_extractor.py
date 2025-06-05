"""
Markdown Block Extractor - Core string processing functionality
"""

from typing import List, Optional, Tuple
import re


class BlockExtractor:
    def __init__(self):
        self.block_types = {
            "markdown": ("```markdown", "```"),
            "python": ("```python", "```"),
            "text": ("```text", "```"),
            "custom": None,  # Will be set by set_custom_delimiters
        }

    def set_custom_delimiters(self, start: str, end: str) -> None:
        """Set custom block delimiters"""
        self.block_types["custom"] = (start, end)

    def find_blocks(
        self, text: str, block_type: str = "text", target_layer: int = 1
    ) -> List[str]:
        """
        Find all blocks of specified type at the target nesting layer.
        A block's content includes everything between its start and end delimiters,
        including any inner block structures.

        Args:
            text: The input text to process
            block_type: Type of block to extract ("markdown", "python", "text", or "custom")
            target_layer: Which layer (absolute nesting depth) to extract (1 = outermost)

        Returns:
            List of extracted block contents (excluding the primary start/end delimiters of the target block)
        """
        if block_type not in self.block_types:
            raise ValueError(f"Unknown block type: {block_type}")

        if block_type == "custom" and self.block_types["custom"] is None:
            raise ValueError("Custom delimiters not set for 'custom' block type.")

        extracted_blocks: List[str] = []
        current_target_block_content: Optional[List[str]] = None
        # Stack: (absolute_depth, type_of_this_block, start_delimiter_str, end_delimiter_str)
        active_blocks_stack: List[Tuple[int, str, str, str]] = []

        lines = text.splitlines(True)  # Keep line endings
        i = 0
        while i < len(lines):
            line_text = lines[i]
            stripped_line_text = line_text.strip()
            processed_as_delimiter = False

            # 1. Check for an END delimiter of the INNEMOST active block
            if active_blocks_stack:
                (
                    innermost_depth,
                    innermost_type,
                    innermost_start_delim,
                    innermost_end_delim,
                ) = active_blocks_stack[-1]

                is_closing_delimiter = False
                # Standard ``` delimiter for ```-based blocks (e.g. ```python, ```markdown, ```text)
                if (
                    innermost_start_delim.startswith("```")
                    and stripped_line_text == "```"
                ):
                    is_closing_delimiter = True
                # Custom end delimiter (that is not "```" itself)
                elif (
                    not innermost_start_delim.startswith("```")
                    and stripped_line_text == innermost_end_delim
                ):
                    is_closing_delimiter = True

                if is_closing_delimiter:
                    processed_as_delimiter = True
                    active_blocks_stack.pop()  # This block is now closed

                    # If this was the end of the specific target block we were collecting:
                    if (
                        current_target_block_content is not None
                        and innermost_depth == target_layer
                        and innermost_type == block_type
                    ):
                        extracted_blocks.append(
                            "".join(current_target_block_content).rstrip("\n")
                        )
                        current_target_block_content = (
                            None  # Reset for next potential target block
                        )
                    elif current_target_block_content is not None:
                        # This closing delimiter belongs to an inner block (or non-target block),
                        # so it's part of the target block's content.
                        current_target_block_content.append(line_text)

            if processed_as_delimiter:
                i += 1
                continue

            # 2. Check for a START delimiter of ANY block type by finding the longest match
            current_absolute_depth = len(active_blocks_stack) + 1

            best_match_btype = None
            best_match_start_delim_str = None
            best_match_end_delim_str = None
            longest_start_delim_len = 0

            for btype_candidate, delims_candidate in self.block_types.items():
                if delims_candidate is None:  # Custom type might not be configured
                    continue
                start_delim_str, end_delim_str = delims_candidate

                if stripped_line_text.startswith(start_delim_str):
                    if len(start_delim_str) > longest_start_delim_len:
                        longest_start_delim_len = len(start_delim_str)
                        best_match_btype = btype_candidate
                        best_match_start_delim_str = start_delim_str
                        best_match_end_delim_str = end_delim_str

            if (
                best_match_btype is not None
                and best_match_start_delim_str is not None
                and best_match_end_delim_str is not None
            ):  # A start delimiter was found
                active_blocks_stack.append(
                    (
                        current_absolute_depth,
                        best_match_btype,
                        best_match_start_delim_str,
                        best_match_end_delim_str,
                    )
                )
                processed_as_delimiter = True

                # If this new block is THE target block we're looking for:
                if (
                    current_target_block_content is None
                    and current_absolute_depth == target_layer
                    and best_match_btype == block_type
                ):
                    current_target_block_content = (
                        []
                    )  # Start collecting its content (excluding this start delim line)
                elif current_target_block_content is not None:
                    # This start delimiter is for an inner block (or non-target block),
                    # so it's part of the currently-being-collected target block's content.
                    current_target_block_content.append(line_text)

            if processed_as_delimiter:
                i += 1
                continue

            # 3. If not any delimiter, it's plain content.
            # Add to current_target_block_content if we are actively collecting for a target block.
            if current_target_block_content is not None:
                current_target_block_content.append(line_text)

            i += 1

        # If EOF is reached while a target block is still open (e.g., malformed input)
        if current_target_block_content is not None:
            extracted_blocks.append("".join(current_target_block_content).rstrip("\n"))

        return extracted_blocks

    def extract_first_block(
        self, text: str, block_type: str = "text", target_layer: int = 1
    ) -> Optional[str]:
        """Extract just the first matching block"""
        blocks = self.find_blocks(text, block_type, target_layer)
        return blocks[0] if blocks else None
