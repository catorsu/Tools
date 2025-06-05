import os
import json
import subprocess
import pyperclip
import tkinter as tk  # Add this import
from tkinter import filedialog
import customtkinter as ctk
from typing import Dict, Any

from core.base_gui import BaseToolFrame


class GitDiffFrame(BaseToolFrame):
    def __init__(self, parent, config: Dict[str, Any], tool=None, **kwargs):
        self.tool = tool
        self.config = dict(config)
        self.custom_tags = self.config.get("custom_tags", ["code_changes"])
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
                pass
            except pyperclip.PyperclipException as e:
                messagebox.showerror("Clipboard Error", f"Failed to copy: {e}")
            except tk.TclError:
                all_text = widget.get("1.0", "end-1c")
                pyperclip.copy(all_text)
                pass

        def paste_command():
            try:
                clipboard_content = pyperclip.paste()
                if widget.tag_ranges("sel"):
                    widget.delete("sel.first", "sel.last")
                widget.insert(tk.INSERT, clipboard_content)
                pass
            except pyperclip.PyperclipException as e:
                messagebox.showerror("Clipboard Error", f"Failed to paste: {e}")
            except tk.TclError:
                messagebox.showerror("Paste Error", "Failed to paste: Tkinter error.")

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
        # Path input frame
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=10, pady=(10, 5))

        path_label = ctk.CTkLabel(path_frame, text="Repository Path:")
        path_label.pack(side="left", padx=5)

        self.path_entry = ctk.CTkEntry(path_frame, width=300)
        self.path_entry.pack(side="left", padx=5, fill="x", expand=True)

        self.browse_btn = ctk.CTkButton(
            path_frame, text="Browse", command=self.browse_path, width=70
        )
        self.browse_btn.pack(side="right", padx=5)
        self.path_entry.insert(0, self.config.get("default_repo_path", ""))

        self.set_default_btn = ctk.CTkButton(
            path_frame, text="Set as Default", command=self.save_default_path
        )
        self.set_default_btn.pack(side="right", padx=5)

        # Tag input frame
        tag_frame = ctk.CTkFrame(self)
        tag_frame.pack(fill="x", padx=10, pady=5)

        tag_label = ctk.CTkLabel(tag_frame, text="Wrapper Tag:")
        tag_label.pack(side="left", padx=5)

        self.tag_combo = ctk.CTkComboBox(tag_frame, width=150, values=self.custom_tags)
        self.tag_combo.pack(side="left", padx=5)
        self.tag_combo.set("code_changes")

        self.new_tag_entry = ctk.CTkEntry(tag_frame, width=100)
        self.new_tag_entry.pack(side="left", padx=5)

        self.add_tag_btn = ctk.CTkButton(
            tag_frame, text="Add Tag", command=self.add_custom_tag, width=70
        )
        self.add_tag_btn.pack(side="left", padx=5)

        self.delete_tag_btn = ctk.CTkButton(
            tag_frame, text="Delete Tag", command=self.delete_custom_tag, width=70
        )
        self.delete_tag_btn.pack(side="left", padx=5)

        self.get_diff_btn = ctk.CTkButton(
            tag_frame, text="Show All Changes", command=self.get_all_changes
        )
        self.get_diff_btn.pack(side="right", padx=5)

        # Output frame
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.output_text = ctk.CTkTextbox(output_frame)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
        # Bind context menu to output_text
        self.output_text_context_menu = self._create_context_menu(self.output_text)
        self.output_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(
                event, self.output_text_context_menu
            ),
        )

        self.copy_btn = ctk.CTkButton(
            output_frame, text="Copy to Clipboard", command=self.copy_output
        )
        self.copy_btn.pack(pady=5)

    def delete_custom_tag(self) -> None:
        current_tag = self.tag_combo.get()
        if current_tag == "code_changes":
            messagebox.showerror("Error", "Cannot delete default tag")
            return

        if current_tag in self.custom_tags:
            self.custom_tags.remove(current_tag)
            self.config["custom_tags"] = self.custom_tags
            self.tag_combo.configure(values=self.custom_tags)
            self.tag_combo.set("code_changes")
            self.tool.save_config()
            pass

    def add_custom_tag(self) -> None:
        new_tag = self.new_tag_entry.get().strip()
        if not new_tag:
            messagebox.showerror("Error", "Please enter a tag name")
            return

        if new_tag not in self.custom_tags:
            self.custom_tags.append(new_tag)
            self.config["custom_tags"] = self.custom_tags
            self.tag_combo.configure(values=self.custom_tags)
            self.tag_combo.set(new_tag)
            self.new_tag_entry.delete(0, "end")
            self.tool.save_config()
            pass
        else:
            messagebox.showerror("Error", "Tag already exists")

    def get_options(self) -> Dict[str, Any]:
        return {"repo_path": self.path_entry.get(), "wrapper_tag": self.tag_combo.get()}

    def set_options(self, options: Dict[str, Any]) -> None:
        if "repo_path" in options:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, options["repo_path"])
        if "wrapper_tag" in options:
            if options["wrapper_tag"] not in self.custom_tags:
                self.custom_tags.append(options["wrapper_tag"])
                self.tag_combo.configure(values=self.custom_tags)
            self.tag_combo.set(options["wrapper_tag"])

    def clear(self) -> None:
        self.output_text.delete("1.0", "end")

    def save_default_path(self) -> None:
        repo_path = self.path_entry.get().strip()
        if not repo_path:
            messagebox.showerror("Error", "Please enter a repository path")
            return

        if not os.path.isdir(repo_path):
            messagebox.showerror("Error", "Invalid directory path")
            return

        git_dir = os.path.join(repo_path, ".git")
        if not os.path.isdir(git_dir):
            messagebox.showerror("Error", "Not a git repository")
            return

        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        config = {"default_repo_path": repo_path}

        try:
            with open(config_path, "w") as f:
                json.dump(config, f)
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def browse_path(self) -> None:
        path = filedialog.askdirectory(title="Select Git Repository")
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def get_all_changes(self) -> None:
        repo_path = self.path_entry.get().strip()
        if not repo_path:
            messagebox.showerror("Error", "Please enter a repository path")
            return

        if not os.path.isdir(repo_path):
            messagebox.showerror("Error", "Invalid directory path")
            return

        git_dir = os.path.join(repo_path, ".git")
        if not os.path.isdir(git_dir):
            messagebox.showerror("Error", "Not a git repository")
            return

        try:
            # Get unstaged changes
            diff_result = subprocess.run(
                ["git", "diff"], cwd=repo_path, capture_output=True, text=True
            )

            # Get untracked files
            ls_files_result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )

            if diff_result.returncode != 0:
                messagebox.showerror("Error", f"Git diff failed: {diff_result.stderr}")
                return

            output_parts = []

            # Add unstaged changes
            if diff_result.stdout:
                output_parts.append(diff_result.stdout)

            # Process untracked files
            if ls_files_result.stdout:
                for untracked_file in ls_files_result.stdout.splitlines():
                    try:
                        with open(os.path.join(repo_path, untracked_file), "r") as f:
                            content = f.read()

                        # Format as git diff output for new file
                        diff_header = (
                            f"diff --git a/{untracked_file} b/{untracked_file}\n"
                        )
                        diff_header += f"new file mode 100644\n"
                        diff_header += f"--- /dev/null\n"
                        diff_header += f"+++ b/{untracked_file}\n"

                        # Add content with + prefix for each line
                        content_lines = [f"+{line}" for line in content.splitlines()]
                        formatted_content = "\n".join(content_lines)

                        output_parts.append(diff_header + formatted_content)
                    except Exception as e:
                        messagebox.showerror(
                            "Error", f"Error reading {untracked_file}: {e}"
                        )
                        continue

            if not output_parts:
                messagebox.showerror("Error", "No changes found")
                return

            diff_output = "\n\n".join(output_parts)

            tag = self.tag_combo.get() or "code_changes"
            wrapped_output = f"<{tag}>\n```\n{diff_output}\n```\n</{tag}>"

            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", wrapped_output)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get diff: {e}")

    def copy_output(self) -> None:
        output = self.output_text.get("1.0", "end").strip()
        if not output:
            messagebox.showerror("Error", "No output to copy")
            return

        pyperclip.copy(output)
        pass
