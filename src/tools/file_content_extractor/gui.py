# src/tools/file_content_extractor/gui.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import pyperclip
import tkinter as tk
import os
from typing import Dict, Any, TYPE_CHECKING

from ...core import BaseToolFrame

if TYPE_CHECKING:
    from .tool import FileContentExtractorTool


class FileContentExtractorFrame(BaseToolFrame):
    def __init__(self, parent, tool_logic: "FileContentExtractorTool", **kwargs):
        self.tool_logic = tool_logic
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
                messagebox.showerror(
                    "Clipboard Error", f"Failed to copy: {e}", parent=self
                )
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
                messagebox.showerror(
                    "Clipboard Error", f"Failed to paste: {e}", parent=self
                )
            except tk.TclError:
                messagebox.showerror(
                    "Paste Error", "Failed to paste: Tkinter error.", parent=self
                )

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
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="File Content Extractor",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.pack(pady=(10, 20), padx=20, anchor="w")

        # Input section
        input_section_frame = ctk.CTkFrame(self)
        input_section_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Base path selection
        ctk.CTkLabel(input_section_frame, text="Base Path:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        path_entry_frame = ctk.CTkFrame(input_section_frame, fg_color="transparent")
        path_entry_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.path_entry = ctk.CTkEntry(path_entry_frame)
        self.path_entry.pack(side="left", fill="x", expand=True)
        browse_btn = ctk.CTkButton(
            path_entry_frame, text="Browse", command=self.browse_path, width=80
        )
        browse_btn.pack(side="left", padx=(10, 0))

        # Input Textbox
        ctk.CTkLabel(input_section_frame, text="Input with <relevant_files> tag:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.input_text = ctk.CTkTextbox(input_section_frame, height=150)
        self.input_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.input_text_context_menu = self._create_context_menu(self.input_text)
        self.input_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(event, self.input_text_context_menu),
        )

        # Controls
        controls_frame = ctk.CTkFrame(self)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        process_btn = ctk.CTkButton(
            controls_frame, text="Extract File Contents", command=self.process_files
        )
        process_btn.pack(side="left", padx=10, pady=10)
        clear_btn = ctk.CTkButton(controls_frame, text="Clear", command=self.clear)
        clear_btn.pack(side="left", padx=0, pady=10)
        copy_btn = ctk.CTkButton(
            controls_frame, text="Copy Output", command=self.copy_output
        )
        copy_btn.pack(side="right", padx=10, pady=10)

        # Output Section
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        ctk.CTkLabel(output_frame, text="Concatenated File Contents:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.output_text = ctk.CTkTextbox(output_frame)
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.output_text_context_menu = self._create_context_menu(self.output_text)
        self.output_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(
                event, self.output_text_context_menu
            ),
        )

    def browse_path(self):
        path = filedialog.askdirectory(title="Select Base Directory")
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def process_files(self):
        input_content = self.input_text.get("1.0", "end-1c")
        base_path = self.path_entry.get().strip()

        if not base_path or not os.path.isdir(base_path):
            messagebox.showerror(
                "Error", "Please provide a valid base path.", parent=self
            )
            return

        if not input_content.strip():
            messagebox.showerror("Error", "Input text is empty.", parent=self)
            return

        try:
            result = self.tool_logic.extract_and_read_files(input_content, base_path)

            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", result["concatenated"])

            # Only show report if there was an attempt to process files
            if result["total"] > 0:
                report_lines = [
                    "File Extraction Report",
                    "=" * 25,
                    f"Total files listed: {result['total']}",
                    f"Files found and read: {result['found']}",
                    f"Files not found: {len(result['not_found'])}",
                ]

                if result["not_found"]:
                    report_lines.append("\nNot Found Files:")
                    for f in result["not_found"]:
                        report_lines.append(f"- {f}")

                messagebox.showinfo(
                    "Extraction Report", "\n".join(report_lines), parent=self
                )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}", parent=self)

    def copy_output(self):
        output = self.output_text.get("1.0", "end-1c").strip()
        if output:
            pyperclip.copy(output)
        else:
            messagebox.showwarning("Warning", "No output to copy.", parent=self)

    def clear(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")

    def get_options(self) -> Dict[str, Any]:
        return {
            "base_path": self.path_entry.get(),
            "input_text": self.input_text.get("1.0", "end-1c"),
        }

    def set_options(self, options: Dict[str, Any]) -> None:
        if "base_path" in options:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, options["base_path"])
        if "input_text" in options:
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", options["input_text"])
