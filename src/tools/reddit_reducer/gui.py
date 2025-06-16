import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
import pyperclip
import tkinter as tk
from typing import Dict, Any

from ...core import BaseToolFrame


class RedditReducerFrame(BaseToolFrame):
    def __init__(self, parent, tool_logic, **kwargs):
        self.reducer = tool_logic.reducer_logic
        super().__init__(parent, **kwargs)

    def _create_context_menu(self, widget: ctk.CTkTextbox) -> tk.Menu:
        menu = tk.Menu(widget, tearoff=0)

        def copy_command():
            try:
                if widget.tag_ranges("sel"):
                    selected_text = widget.get("sel.first", "sel.last")
                    pyperclip.copy(selected_text)
                else:
                    all_text = widget.get("1.0", "end-1c")
                    pyperclip.copy(all_text)
            except pyperclip.PyperclipException as e:
                messagebox.showerror("Clipboard Error", f"Failed to copy: {e}")
            except tk.TclError:
                all_text = widget.get("1.0", "end-1c")
                pyperclip.copy(all_text)

        def paste_command():
            try:
                clipboard_content = pyperclip.paste()
                if widget.tag_ranges("sel"):
                    widget.delete("sel.first", "sel.last")
                widget.insert(tk.INSERT, clipboard_content)
            except pyperclip.PyperclipException as e:
                messagebox.showerror("Clipboard Error", f"Failed to paste: {e}")
            except tk.TclError:
                messagebox.showerror("Paste Error", "Failed to paste: Tkinter error.")

        def select_all_command():
            widget.tag_add("sel", "1.0", "end")
            widget.mark_set(tk.INSERT, "1.0")

        menu.add_command(label="Copy", command=copy_command)
        menu.add_command(label="Paste", command=paste_command)
        menu.add_command(label="Select All", command=select_all_command)
        return menu

    def _popup_context_menu(self, event, menu: tk.Menu):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def setup_ui(self):
        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Reddit JSON Reducer",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=10, pady=(10, 20), sticky="w")

        # Input Textbox
        ctk.CTkLabel(self, text="Raw Reddit JSON Input:").grid(
            row=1, column=0, padx=10, pady=(0, 5), sticky="sw"
        )
        self.input_text = ctk.CTkTextbox(self)
        self.input_text.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.input_text_context_menu = self._create_context_menu(self.input_text)
        self.input_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(event, self.input_text_context_menu),
        )

        # Controls Frame
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.process_button = ctk.CTkButton(
            controls_frame, text="Process JSON", command=self.process_json
        )
        self.process_button.pack(side="left", padx=10, pady=10)

        self.clear_button = ctk.CTkButton(
            controls_frame, text="Clear", command=self.clear
        )
        self.clear_button.pack(side="left", padx=10, pady=10)

        self.copy_button = ctk.CTkButton(
            controls_frame, text="Copy Output", command=self.copy_output
        )
        self.copy_button.pack(side="right", padx=10, pady=10)

        # Output Textbox
        ctk.CTkLabel(self, text="Simplified JSON Output:").grid(
            row=4, column=0, padx=10, pady=(0, 5), sticky="sw"
        )
        self.output_text = ctk.CTkTextbox(self)
        self.output_text.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.output_text_context_menu = self._create_context_menu(self.output_text)
        self.output_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(
                event, self.output_text_context_menu
            ),
        )

    def process_json(self):
        input_json = self.input_text.get("1.0", "end-1c")
        if not input_json.strip():
            messagebox.showerror("Error", "Input JSON is empty.")
            return

        try:
            simplified_data = self.reducer.process_json_string(input_json)
            output_json = json.dumps(simplified_data, indent=2)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", output_json)
        except ValueError as e:
            messagebox.showerror("Processing Error", f"Failed to process JSON: {e}")
        except Exception as e:
            messagebox.showerror(
                "Unexpected Error", f"An unexpected error occurred: {e}"
            )

    def copy_output(self):
        output_val = self.output_text.get("1.0", "end-1c")
        if output_val.strip():
            pyperclip.copy(output_val)
        else:
            messagebox.showwarning("Warning", "No output to copy.")

    def clear(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")

    def get_options(self) -> Dict[str, Any]:
        return {"input_text": self.input_text.get("1.0", "end-1c")}

    def set_options(self, options: Dict[str, Any]) -> None:
        if "input_text" in options:
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", options["input_text"])
