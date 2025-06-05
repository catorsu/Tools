# File: /home/cator/project/Tools/src/tools/tag_tools/tool.py
import os
import json
from typing import Dict, Any, List, TypeVar, Generic, Callable, Optional

from ...core import BaseTool
from .extractor import ContentExtractor
from .renamer import TagRenamer
from .wrapper import TagWrapper

# Forward declaration for type hinting the GUI frame
T = TypeVar("T")  # This will be TagToolsMainFrame

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_TAGS = sorted(
    list(
        set(
            [  # Ensure DEFAULT_TAGS are sorted and unique
                "content",
                "data",
                "example",
                "code",
                "output",
                "file_contents",
                "new_tag",
                "renamed_tag",
                "wrapped_text",
                "default_tag",  # Added a generic default
            ]
        )
    )
)


class TagToolsMainTool(BaseTool[T]):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.extractor_logic = ContentExtractor()
        self.renamer_logic = TagRenamer()
        self.wrapper_logic = TagWrapper()

        # Callbacks for GUI messages, set by the main GUI frame
        self._show_error_callback: Optional[Callable[[str], None]] = None
        self._show_success_callback: Optional[Callable[[str], None]] = None

    def set_gui_message_callbacks(
        self, error_cb: Callable[[str], None], success_cb: Callable[[str], None]
    ):
        """Set the callbacks for displaying messages in the GUI."""
        self._show_error_callback = error_cb
        self._show_success_callback = success_cb

    def show_error(self, message: str) -> None:
        """Display an error message in the GUI."""
        if self._show_error_callback:
            self._show_error_callback(message)
        else:
            print(f"ERROR: {message}")  # Fallback for console if GUI callback not set

    def show_success(self, message: str) -> None:
        """Display a success message in the GUI."""
        if self._show_success_callback:
            self._show_success_callback(message)
        else:
            print(f"SUCCESS: {message}")  # Fallback for console if GUI callback not set

    def get_tool_name(self) -> str:
        return "Tag Tools"

    def get_tool_description(self) -> str:
        return "A collection of tools for manipulating content within tags."

    def get_tool_options(self) -> Dict[str, Any]:
        return {"custom_tags": self.get_custom_tags()}

    def create_tool_gui(self, parent) -> T:
        from .gui import TagToolsMainFrame  # Keep this import local

        gui_frame = TagToolsMainFrame(parent, tool_logic=self)
        # Register the GUI's message display methods with the tool logic
        self.set_gui_message_callbacks(gui_frame.show_error, gui_frame.show_success)
        return gui_frame

    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config_data = json.load(f)
                    if (
                        "custom_tags" not in config_data
                        or not isinstance(config_data["custom_tags"], list)
                        # Ensure custom_tags is not empty after loading
                    ):
                        config_data["custom_tags"] = list(DEFAULT_TAGS)

                    # Ensure all tags are strings and list is sorted and unique
                    current_tags = {
                        str(tag) for tag in config_data.get("custom_tags", [])
                    }
                    # Add default tags if the list becomes empty through manual edit or corruption
                    if not current_tags:
                        current_tags.update(DEFAULT_TAGS)

                    config_data["custom_tags"] = sorted(list(current_tags))
                    return config_data
            except json.JSONDecodeError:
                return {"custom_tags": list(DEFAULT_TAGS)}  # Use a copy
        return {"custom_tags": list(DEFAULT_TAGS)}  # Use a copy

    def save_config(self) -> None:
        try:
            with open(CONFIG_FILE, "w") as f:
                # Ensure tags are sorted and unique before saving
                tags_to_save = sorted(
                    list(set(str(tag) for tag in self.config.get("custom_tags", [])))
                )
                # Ensure there's at least one tag before saving
                if not tags_to_save:
                    tags_to_save = list(DEFAULT_TAGS)
                self.config["custom_tags"] = tags_to_save
                json.dump(self.config, f, indent=4)
        except IOError as e:
            self.show_error(f"Error saving config for TagTools: {e}")  # Use show_error

    def get_custom_tags(self) -> List[str]:
        # This method should always return a sorted list of unique string tags, and never be empty.
        tags = self.config.get("custom_tags", [])
        if not tags:  # Should not happen if load_config and save_config are robust
            return list(DEFAULT_TAGS)
        return sorted(list(set(str(tag) for tag in tags)))

    def add_custom_tag(self, tag_name: str) -> bool:
        tags = self.get_custom_tags()  # Gets a sorted, unique list
        tag_name_stripped = tag_name.strip()
        if tag_name_stripped and tag_name_stripped not in tags:
            tags.append(tag_name_stripped)
            self.config["custom_tags"] = sorted(
                list(set(tags))
            )  # Re-sort and ensure uniqueness
            self.save_config()
            return True
        return False

    def delete_custom_tag(self, tag_name: str) -> bool:
        tags = self.get_custom_tags()
        if tag_name in tags and len(tags) > 1:  # Prevent deleting the last tag
            tags.remove(tag_name)
            self.config["custom_tags"] = sorted(
                list(set(tags))
            )  # Should already be sorted/unique
            self.save_config()
            return True
        elif len(tags) <= 1 and tag_name in tags:
            self.show_error("Cannot delete the last remaining tag.")
        return False

    def perform_extraction(self, text: str, tag_name: str) -> List[str]:
        return self.extractor_logic.extract_content(text, tag_name)

    def perform_renaming(self, text: str, old_tag_name: str, new_tag_name: str) -> str:
        return self.renamer_logic.rename_tag(text, old_tag_name, new_tag_name)

    def perform_wrapping(self, text: str, tag_name: str) -> str:
        return self.wrapper_logic.wrap_text(text, tag_name)
