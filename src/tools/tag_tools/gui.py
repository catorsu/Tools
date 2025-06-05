# File: /home/cator/project/Tools/src/tools/tag_tools/gui.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import Dict, Any, List, TYPE_CHECKING, Optional  # Import Optional

from ...core import BaseToolFrame

# REMOVED top-level imports for sub-frames to break circular dependency
# from .extractor_gui import TagContentExtractorSubFrame
# from .renamer_gui import TagRenamerSubFrame
# from .wrapper_gui import TagWrapperSubFrame

if TYPE_CHECKING:
    from .tool import TagToolsMainTool  # For type hinting

    # Add type hints for sub-frames for TYPE_CHECKING only
    from .extractor_gui import TagContentExtractorSubFrame
    from .renamer_gui import TagRenamerSubFrame
    from .wrapper_gui import TagWrapperSubFrame


class TagToolsMainFrame(BaseToolFrame):
    def __init__(self, parent, tool_logic: "TagToolsMainTool", **kwargs):
        self.tool_logic = tool_logic  # This is the TagToolsMainTool instance
        super().__init__(parent, **kwargs)

        # Store references to sub-frames for clearing/setting options
        # Initialize as Optional as they are created in setup_ui
        self.extractor_sub_frame: Optional["TagContentExtractorSubFrame"] = None
        self.renamer_sub_frame: Optional["TagRenamerSubFrame"] = None
        self.wrapper_sub_frame: Optional["TagWrapperSubFrame"] = None

    def setup_ui(self) -> None:
        # IMPORT sub-frames here, inside the method, where they are actually instantiated
        from .extractor_gui import TagContentExtractorSubFrame
        from .renamer_gui import TagRenamerSubFrame
        from .wrapper_gui import TagWrapperSubFrame

        # Main tab view
        self.tabview = ctk.CTkTabview(self, width=250)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs for each sub-tool
        self.tab_extractor = self.tabview.add("Extractor")
        self.tab_renamer = self.tabview.add("Renamer")
        self.tab_wrapper = self.tabview.add("Wrapper")  # New tab

        # Instantiate and pack sub-frames into their respective tabs
        self.extractor_sub_frame = TagContentExtractorSubFrame(
            self.tab_extractor, tool_logic=self.tool_logic
        )
        self.extractor_sub_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.renamer_sub_frame = TagRenamerSubFrame(
            self.tab_renamer, tool_logic=self.tool_logic
        )
        self.renamer_sub_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.wrapper_sub_frame = TagWrapperSubFrame(
            self.tab_wrapper, tool_logic=self.tool_logic
        )
        self.wrapper_sub_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def get_options(self) -> Dict[str, Any]:
        # Collect options from all sub-frames
        options = {}
        if self.extractor_sub_frame:  # Add check if frame is initialized
            options["extractor_options"] = self.extractor_sub_frame.get_options()
        if self.renamer_sub_frame:  # Add check if frame is initialized
            options["renamer_options"] = self.renamer_sub_frame.get_options()
        if self.wrapper_sub_frame:  # Add check if frame is initialized
            options["wrapper_options"] = self.wrapper_sub_frame.get_options()
        return options

    def set_options(self, options: Dict[str, Any]) -> None:
        # Distribute options to sub-frames
        if (
            self.extractor_sub_frame and "extractor_options" in options
        ):  # Add check if frame is initialized
            self.extractor_sub_frame.set_options(options["extractor_options"])
        if (
            self.renamer_sub_frame and "renamer_options" in options
        ):  # Add check if frame is initialized
            self.renamer_sub_frame.set_options(options["renamer_options"])
        if (
            self.wrapper_sub_frame and "wrapper_options" in options
        ):  # Add check if frame is initialized
            self.wrapper_sub_frame.set_options(options["wrapper_options"])

    def clear(self) -> None:
        # Clear all sub-frames
        if self.extractor_sub_frame:  # Add check if frame is initialized
            self.extractor_sub_frame.clear()
        if self.renamer_sub_frame:  # Add check if frame is initialized
            self.renamer_sub_frame.clear()
        if self.wrapper_sub_frame:  # Add check if frame is initialized
            self.wrapper_sub_frame.clear()

    def show_error(self, message: str) -> None:
        # Centralized error display
        messagebox.showerror("Error", message, parent=self)

    def show_success(self, message: str) -> None:
        # Centralized success display (now handled by sub-frames)
        pass
