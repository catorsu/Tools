import customtkinter as ctk
import tkinter.messagebox as messagebox  # Still needed for askyesno
import pyperclip
import tkinter as tk  # Add this import
from typing import Dict, Any, List, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from .tool import TagToolsMainTool


class TagContentExtractorSubFrame(ctk.CTkFrame):  # Changed inheritance
    def __init__(
        self,
        parent,
        tool_logic: "TagToolsMainTool",  # Changed type hint and purpose
        **kwargs,
    ):
        self.tool_logic = tool_logic  # This is the TagToolsMainTool instance
        # Fetch initial tags directly from tool_logic
        self.custom_tags = self.tool_logic.get_custom_tags()
        if not self.custom_tags:
            # This should ideally not happen if tool_logic handles defaults
            self.tool_logic.add_custom_tag("content")
            self.custom_tags = self.tool_logic.get_custom_tags()

        super().__init__(parent, **kwargs)
        self.setup_ui()
        self._update_tag_dropdown()  # Ensure dropdown is populated correctly at init

    def _create_context_menu(self, widget: ctk.CTkTextbox) -> tk.Menu:
        menu = tk.Menu(widget, tearoff=0)

        def copy_command():
            try:
                if widget.tag_ranges("sel"):
                    # If text is selected, copy the selection
                    selected_text = widget.get("sel.first", "sel.last")
                    pyperclip.copy(selected_text)
                else:
                    # If no text is selected, copy all text
                    all_text = widget.get("1.0", "end-1c")
                    pyperclip.copy(all_text)
                pass
            except pyperclip.PyperclipException as e:
                self.tool_logic.show_error(f"Clipboard error: {e}")
            except tk.TclError:
                # No selection, or other Tkinter error during get("sel.first", "sel.last")
                all_text = widget.get("1.0", "end-1c")
                pyperclip.copy(all_text)
                pass

        def paste_command():
            try:
                clipboard_content = pyperclip.paste()
                if widget.tag_ranges("sel"):
                    # If text is selected, replace the selection
                    widget.delete("sel.first", "sel.last")
                widget.insert(tk.INSERT, clipboard_content)
                pass
            except pyperclip.PyperclipException as e:
                self.tool_logic.show_error(f"Clipboard error: {e}")
            except tk.TclError:
                self.tool_logic.show_error("Failed to paste: Tkinter error.")

        def select_all_command():
            widget.tag_add("sel", "1.0", "end")
            widget.mark_set(tk.INSERT, "1.0")
            pass

        menu.add_command(label="Copy", command=copy_command)
        menu.add_command(label="Paste", command=paste_command)
        menu.add_command(label="Select All", command=select_all_command)
        return menu

    def _popup_context_menu(self, event, menu: tk.Menu):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def setup_ui(self) -> None:  # Added type hint
        # Title (adjusted for sub-frame)
        title_label = ctk.CTkLabel(
            self,
            text="Tag Content Extractor",
            font=ctk.CTkFont(size=20, weight="bold"),  # Smaller font
        )
        title_label.pack(pady=(10, 20), padx=10, anchor="w")

        # Input and Configuration Frame
        config_input_frame = ctk.CTkFrame(self)
        config_input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Tag Management Frame
        tag_management_frame = ctk.CTkFrame(config_input_frame)
        tag_management_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(tag_management_frame, text="Extraction Tag:").pack(
            side="left", padx=(5, 5)
        )
        self.tag_combo = ctk.CTkComboBox(
            tag_management_frame, width=180, values=self.custom_tags
        )
        self.tag_combo.pack(side="left", padx=5)

        self.new_tag_entry = ctk.CTkEntry(
            tag_management_frame, placeholder_text="New tag name", width=150
        )
        self.new_tag_entry.pack(side="left", padx=5)

        self.add_tag_btn = ctk.CTkButton(
            tag_management_frame,
            text="Add",
            command=self.add_tag,
            width=60,
        )
        self.add_tag_btn.pack(side="left", padx=5)

        self.delete_tag_btn = ctk.CTkButton(
            tag_management_frame,
            text="Delete",
            command=self.delete_tag,
            width=70,
        )
        self.delete_tag_btn.pack(side="left", padx=5)

        # Input Text Area
        ctk.CTkLabel(config_input_frame, text="Input Text:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.input_text = ctk.CTkTextbox(config_input_frame, height=200)
        self.input_text.pack(fill="x", expand=True, padx=10, pady=(0, 10))
        # Bind context menu to input_text
        self.input_text_context_menu = self._create_context_menu(self.input_text)
        self.input_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(event, self.input_text_context_menu),
        )

        # Control Buttons Frame
        control_buttons_frame = ctk.CTkFrame(self)
        control_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.extract_button = ctk.CTkButton(
            control_buttons_frame, text="Extract Content", command=self.run_extraction
        )
        self.extract_button.pack(side="left", padx=10, pady=10)

        self.clear_button = ctk.CTkButton(
            control_buttons_frame, text="Clear All", command=self.clear
        )
        self.clear_button.pack(side="left", padx=(0, 10), pady=10)

        self.copy_output_button = ctk.CTkButton(
            control_buttons_frame, text="Copy Output", command=self.copy_output
        )
        self.copy_output_button.pack(side="right", padx=10, pady=10)

        # Results Section
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ctk.CTkLabel(results_frame, text="Extracted Content:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.output_text = ctk.CTkTextbox(
            results_frame, font=ctk.CTkFont(family="Courier", size=11)
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        # Bind context menu to output_text
        self.output_text_context_menu = self._create_context_menu(self.output_text)
        self.output_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(
                event, self.output_text_context_menu
            ),
        )

    def _update_tag_dropdown(self):
        self.custom_tags = self.tool_logic.get_custom_tags()
        current_selection = self.tag_combo.get()

        if not self.custom_tags:
            self.tool_logic.add_custom_tag("content")  # Ensure default exists
            self.custom_tags = self.tool_logic.get_custom_tags()

        self.tag_combo.configure(values=self.custom_tags)

        if current_selection in self.custom_tags:
            self.tag_combo.set(current_selection)
        elif self.custom_tags:
            self.tag_combo.set(self.custom_tags[0])
        else:
            self.tag_combo.set("Error: No Tags")

    def add_tag(self):
        new_tag = self.new_tag_entry.get().strip()
        if not new_tag:
            self.tool_logic.show_error(
                "Please enter a tag name."
            )  # Call main tool's error
            return
        if not re.match(r"^[a-zA-Z0-9_-]+$", new_tag):
            self.tool_logic.show_error(
                "Tag name should be alphanumeric (can include '-' or '_') and have no spaces."
            )
            return

        if self.tool_logic.add_custom_tag(new_tag):
            self._update_tag_dropdown()
            self.tag_combo.set(new_tag)
            self.new_tag_entry.delete(0, "end")
        else:
            self.tool_logic.show_error(
                f"Tag '{new_tag}' already exists or could not be added."
            )

    def delete_tag(self):
        tag_to_delete = self.tag_combo.get()
        if not tag_to_delete or tag_to_delete == "Error: No Tags":
            self.tool_logic.show_error("No tag selected to delete.")
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the tag '{tag_to_delete}'?",
            parent=self,  # Parent is now the sub-frame itself
        ):
            if self.tool_logic.delete_custom_tag(tag_to_delete):
                self._update_tag_dropdown()
            else:
                self.tool_logic.show_error(
                    f"Could not delete tag '{tag_to_delete}'. It might be the last tag or an error occurred."
                )

    def run_extraction(self):
        input_val = self.input_text.get("1.0", "end-1c")
        selected_tag = self.tag_combo.get()

        if not input_val.strip():
            self.tool_logic.show_error("Input text is empty.")
            return
        if not selected_tag or selected_tag == "Error: No Tags":
            self.tool_logic.show_error(
                "No extraction tag selected or tags are not loaded correctly."
            )
            return

        try:
            extracted_contents = self.tool_logic.perform_extraction(
                input_val, selected_tag
            )
            self.output_text.delete("1.0", "end")
            if extracted_contents:
                output_str = ""
                for i, content in enumerate(extracted_contents):
                    output_str += content.strip()
                    output_str += "\n\n"
                self.output_text.insert("end", output_str.strip())
                # Removed success message as per new instruction
            else:
                self.output_text.insert(
                    "end", f"No content found for tag '{selected_tag}'.\n"
                )
                # Removed success message as per new instruction
        except Exception as e:
            self.tool_logic.show_error(f"Extraction error: {str(e)}")

    def copy_output(self):
        output_val = self.output_text.get("1.0", "end-1c")
        if output_val.strip():
            pyperclip.copy(output_val)
            # Removed success message as per new instruction
        else:
            self.tool_logic.show_error("No output to copy.")

    def get_options(self) -> Dict[str, Any]:
        return {
            "selected_tag": self.tag_combo.get(),
            "input_text": self.input_text.get("1.0", "end-1c"),
        }

    def set_options(self, options: Dict[str, Any]) -> None:
        if "selected_tag" in options and options["selected_tag"] in self.custom_tags:
            self.tag_combo.set(options["selected_tag"])
        if "input_text" in options:
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", options["input_text"])

    def clear(self) -> None:
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
