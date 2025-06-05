# File: /home/cator/project/Tools/src/tools/tag_tools/renamer_gui.py
import customtkinter as ctk
import tkinter.messagebox as messagebox  # Still needed for askyesno
import pyperclip
import tkinter as tk  # Add this import
from typing import Dict, Any, List, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from .tool import TagToolsMainTool


class TagRenamerSubFrame(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        tool_logic: "TagToolsMainTool",
        **kwargs,
    ):
        self.tool_logic = tool_logic
        self.custom_tags = []  # Will be populated by _update_tag_dropdown
        super().__init__(parent, **kwargs)
        self.setup_ui()
        self._update_tag_dropdown()

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

    def setup_ui(self) -> None:
        title_label = ctk.CTkLabel(
            self, text="Tag Renamer", font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20), padx=10, anchor="w")

        config_input_frame = ctk.CTkFrame(self)
        config_input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # --- Old Tag Name Section ---
        old_tag_frame = ctk.CTkFrame(config_input_frame)
        old_tag_frame.pack(fill="x", padx=5, pady=(5, 2))

        ctk.CTkLabel(old_tag_frame, text="Old Tag Name:").pack(side="left", padx=(5, 5))
        self.old_tag_combo = ctk.CTkComboBox(old_tag_frame, width=150)
        self.old_tag_combo.pack(side="left", padx=5)

        self.add_old_tag_entry = ctk.CTkEntry(
            old_tag_frame, placeholder_text="Add to list", width=120
        )
        self.add_old_tag_entry.pack(side="left", padx=(10, 5))
        self.add_old_tag_btn = ctk.CTkButton(
            old_tag_frame, text="Add", command=self.add_old_tag_to_list, width=60
        )
        self.add_old_tag_btn.pack(side="left", padx=5)
        self.delete_old_tag_btn = ctk.CTkButton(
            old_tag_frame,
            text="Delete Selected",
            command=self.delete_selected_old_tag,
            width=100,
        )
        self.delete_old_tag_btn.pack(side="left", padx=5)

        # --- New Tag Name Section ---
        new_tag_frame = ctk.CTkFrame(config_input_frame)
        new_tag_frame.pack(fill="x", padx=5, pady=(2, 5))

        ctk.CTkLabel(new_tag_frame, text="New Tag Name:").pack(side="left", padx=(5, 5))
        self.new_tag_combo = ctk.CTkComboBox(new_tag_frame, width=150)
        self.new_tag_combo.pack(side="left", padx=5)

        self.add_new_tag_entry = ctk.CTkEntry(
            new_tag_frame, placeholder_text="Add to list", width=120
        )
        self.add_new_tag_entry.pack(side="left", padx=(10, 5))
        self.add_new_tag_btn = ctk.CTkButton(
            new_tag_frame, text="Add", command=self.add_new_tag_to_list, width=60
        )
        self.add_new_tag_btn.pack(side="left", padx=5)
        self.delete_new_tag_btn = ctk.CTkButton(
            new_tag_frame,
            text="Delete Selected",
            command=self.delete_selected_new_tag,
            width=100,
        )
        self.delete_new_tag_btn.pack(side="left", padx=5)

        # --- Input Text Section ---
        ctk.CTkLabel(config_input_frame, text="Input Text:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.input_text = ctk.CTkTextbox(config_input_frame, height=180)
        self.input_text.pack(fill="x", expand=True, padx=10, pady=(0, 10))
        # Bind context menu to input_text
        self.input_text_context_menu = self._create_context_menu(self.input_text)
        self.input_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(event, self.input_text_context_menu),
        )

        # --- Control Buttons Frame ---
        control_buttons_frame = ctk.CTkFrame(self)
        control_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.rename_button = ctk.CTkButton(
            control_buttons_frame, text="Rename Tags", command=self.run_renaming
        )
        self.rename_button.pack(side="left", padx=10, pady=10)

        self.clear_button = ctk.CTkButton(
            control_buttons_frame, text="Clear All", command=self.clear
        )
        self.clear_button.pack(side="left", padx=(0, 10), pady=10)

        self.copy_output_button = ctk.CTkButton(
            control_buttons_frame, text="Copy Output", command=self.copy_output
        )
        self.copy_output_button.pack(side="right", padx=10, pady=10)

        # --- Results Section ---
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ctk.CTkLabel(results_frame, text="Modified Content:").pack(
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

    def _validate_tag_name(self, tag_name: str) -> bool:
        if not tag_name:
            self.tool_logic.show_error("Please enter a tag name.")
            return False
        if not re.match(r"^[a-zA-Z0-9_-]+$", tag_name):
            self.tool_logic.show_error(
                "Tag name should be alphanumeric (can include '-' or '_') and have no spaces."
            )
            return False
        return True

    def _add_tag_to_shared_list(self, tag_name: str) -> bool:
        if self.tool_logic.add_custom_tag(tag_name):
            self._update_tag_dropdown()  # This will refresh both combo boxes' options
            return True
        else:
            self.tool_logic.show_error(
                f"Tag '{tag_name}' already exists or could not be added."
            )
            return False

    def add_old_tag_to_list(self):
        new_tag = self.add_old_tag_entry.get().strip()
        if self._validate_tag_name(new_tag):
            if self._add_tag_to_shared_list(new_tag):
                self.old_tag_combo.set(
                    new_tag
                )  # Set the added tag as current for this combo
                self.add_old_tag_entry.delete(0, "end")

    def add_new_tag_to_list(self):
        new_tag = self.add_new_tag_entry.get().strip()
        if self._validate_tag_name(new_tag):
            if self._add_tag_to_shared_list(new_tag):
                self.new_tag_combo.set(
                    new_tag
                )  # Set the added tag as current for this combo
                self.add_new_tag_entry.delete(0, "end")

    def _delete_tag_from_shared_list(self, tag_to_delete: str):
        if not tag_to_delete or tag_to_delete == "Error: No Tags":
            self.tool_logic.show_error("No tag selected to delete.")
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the tag '{tag_to_delete}' from the shared list?",
            parent=self,
        ):
            if self.tool_logic.delete_custom_tag(tag_to_delete):
                self._update_tag_dropdown()  # This will refresh both combo boxes' options
            else:
                self.tool_logic.show_error(
                    f"Could not delete tag '{tag_to_delete}'. It might be the last tag or an error occurred."
                )

    def delete_selected_old_tag(self):
        tag_to_delete = self.old_tag_combo.get()
        self._delete_tag_from_shared_list(tag_to_delete)

    def delete_selected_new_tag(self):
        tag_to_delete = self.new_tag_combo.get()
        self._delete_tag_from_shared_list(tag_to_delete)

    def _update_tag_dropdown(self):
        # Preserve current selections before updating the list of available options
        old_selection_before_update = self.old_tag_combo.get()
        new_selection_before_update = self.new_tag_combo.get()

        # Fetch the latest shared list of tags (which might have changed due to add/delete)
        # tool_logic.get_custom_tags() is guaranteed to return a sorted, non-empty list.
        updated_shared_tags = self.tool_logic.get_custom_tags()

        # Configure both ComboBoxes with the new list of available tags
        self.old_tag_combo.configure(values=updated_shared_tags)
        self.new_tag_combo.configure(values=updated_shared_tags)

        # Attempt to restore the selection for the Old Tag ComboBox
        if old_selection_before_update in updated_shared_tags:
            self.old_tag_combo.set(old_selection_before_update)
        elif (
            updated_shared_tags
        ):  # If previous selection is invalid, but there are other tags
            self.old_tag_combo.set(
                updated_shared_tags[0]
            )  # Set to the first available tag
        else:
            # This case should ideally not be reached if tool_logic prevents deleting the last tag.
            self.old_tag_combo.set("Error: No Tags")

        # Attempt to restore the selection for the New Tag ComboBox
        if new_selection_before_update in updated_shared_tags:
            self.new_tag_combo.set(new_selection_before_update)
        elif (
            updated_shared_tags
        ):  # If previous selection is invalid, but there are other tags
            self.new_tag_combo.set(
                updated_shared_tags[0]
            )  # Set to the first available tag
        else:
            # This case should ideally not be reached.
            self.new_tag_combo.set("Error: No Tags")

    def run_renaming(self):
        input_val = self.input_text.get("1.0", "end-1c")
        old_tag = self.old_tag_combo.get().strip()
        new_tag = self.new_tag_combo.get().strip()

        if not input_val.strip():
            self.tool_logic.show_error("Input text is empty.")
            return
        if not old_tag or old_tag == "Error: No Tags":
            self.tool_logic.show_error("Please select an 'Old Tag Name'.")
            return
        if not new_tag or new_tag == "Error: No Tags":
            self.tool_logic.show_error("Please select or add a 'New Tag Name'.")
            return
        if old_tag == new_tag:
            self.tool_logic.show_error(
                "Old tag name and new tag name cannot be the same."
            )
            return
        if not re.match(r"^[a-zA-Z0-9_-]+$", old_tag):
            self.tool_logic.show_error("Selected 'Old Tag Name' is invalid.")
            return
        if not re.match(r"^[a-zA-Z0-9_-]+$", new_tag):
            self.tool_logic.show_error("Selected 'New Tag Name' is invalid.")
            return

        try:
            modified_content = self.tool_logic.perform_renaming(
                input_val, old_tag, new_tag
            )
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", modified_content)
            # Removed success message as per new instruction
        except Exception as e:
            self.tool_logic.show_error(f"Renaming error: {str(e)}")

    def copy_output(self):
        output_val = self.output_text.get("1.0", "end-1c")
        if output_val.strip():
            pyperclip.copy(output_val)
            # Removed success message as per new instruction
        else:
            self.tool_logic.show_error("No output to copy.")

    def get_options(self) -> Dict[str, Any]:
        return {
            "old_tag_selection": self.old_tag_combo.get(),
            "new_tag_selection": self.new_tag_combo.get(),
            "input_text": self.input_text.get("1.0", "end-1c"),
        }

    def set_options(self, options: Dict[str, Any]) -> None:
        self._update_tag_dropdown()

        current_tags = (
            self.tool_logic.get_custom_tags()
        )  # Use the consistently updated list

        if (
            "old_tag_selection" in options
            and options["old_tag_selection"] in current_tags
        ):
            self.old_tag_combo.set(options["old_tag_selection"])
        elif current_tags:
            self.old_tag_combo.set(current_tags[0])
        else:
            self.old_tag_combo.set("Error: No Tags")

        if (
            "new_tag_selection" in options
            and options["new_tag_selection"] in current_tags
        ):
            self.new_tag_combo.set(options["new_tag_selection"])
        elif current_tags:
            self.new_tag_combo.set(current_tags[0])
        else:
            self.new_tag_combo.set("Error: No Tags")

        if "input_text" in options:
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", options["input_text"])

    def clear(self) -> None:
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.add_old_tag_entry.delete(0, "end")
        self.add_new_tag_entry.delete(0, "end")
        self._update_tag_dropdown()
