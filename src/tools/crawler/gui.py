import customtkinter as ctk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import threading
import pyperclip
import tkinter as tk  # Add this import
from datetime import datetime
from typing import Dict, Any, Optional

from ...core import BaseToolFrame


class CrawlerToolFrame(BaseToolFrame):
    def __init__(self, parent, crawler, **kwargs):
        self.crawler = crawler
        self.crawler.set_progress_callback(self.update_progress)
        self.crawler.set_error_callback(self.show_error)
        self.found_links = []
        self.crawl_thread = None
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

    def setup_ui(self):
        # Title
        title_label = ctk.CTkLabel(
            self, text="Sublink Crawler", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Input section
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Start URL
        ctk.CTkLabel(input_frame, text="Start URL:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.start_url_entry = ctk.CTkEntry(
            input_frame, placeholder_text="https://example.com/products/"
        )
        self.start_url_entry.pack(fill="x", padx=10, pady=(0, 10))

        # URL Prefix (optional)
        ctk.CTkLabel(input_frame, text="URL Prefix Filter (optional):").pack(
            anchor="w", padx=10, pady=(5, 5)
        )
        self.url_prefix_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Leave empty to use start URL path"
        )
        self.url_prefix_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Parameters frame
        params_frame = ctk.CTkFrame(input_frame)
        params_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Parameters - Row 1
        params_row1 = ctk.CTkFrame(params_frame)
        params_row1.pack(fill="x", padx=5, pady=5)

        # Max Depth
        ctk.CTkLabel(params_row1, text="Max Depth:").pack(side="left", padx=(10, 5))
        self.max_depth_var = ctk.StringVar(value="2")
        self.max_depth_entry = ctk.CTkEntry(
            params_row1, textvariable=self.max_depth_var, width=60
        )
        self.max_depth_entry.pack(side="left", padx=(0, 20))

        # Max Pages
        ctk.CTkLabel(params_row1, text="Max Pages:").pack(side="left", padx=(0, 5))
        self.max_pages_var = ctk.StringVar(value="100")
        self.max_pages_entry = ctk.CTkEntry(
            params_row1, textvariable=self.max_pages_var, width=60
        )
        self.max_pages_entry.pack(side="left", padx=(0, 20))

        # Request Delay
        ctk.CTkLabel(params_row1, text="Delay (sec):").pack(side="left", padx=(0, 5))
        self.delay_var = ctk.StringVar(value="1.0")
        self.delay_entry = ctk.CTkEntry(
            params_row1, textvariable=self.delay_var, width=60
        )
        self.delay_entry.pack(side="left")

        # User Agent
        ctk.CTkLabel(input_frame, text="User Agent (optional):").pack(
            anchor="w", padx=10, pady=(5, 5)
        )
        self.user_agent_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Leave empty for default"
        )
        self.user_agent_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Control buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.start_button = ctk.CTkButton(
            button_frame, text="Start Crawl", command=self.start_crawl
        )
        self.start_button.pack(side="left", padx=10, pady=10)

        self.stop_button = ctk.CTkButton(
            button_frame, text="Stop", command=self.stop_crawl, state="disabled"
        )
        self.stop_button.pack(side="left", padx=(0, 10), pady=10)

        self.clear_button = ctk.CTkButton(
            button_frame, text="Clear Results", command=self.clear
        )
        self.clear_button.pack(side="left", padx=(0, 10), pady=10)

        self.export_button = ctk.CTkButton(
            button_frame,
            text="Export Results",
            command=self.export_results,
            state="disabled",
        )
        self.export_button.pack(side="right", padx=10, pady=10)

        # Progress section
        progress_frame = ctk.CTkFrame(self)
        progress_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(progress_frame, text="Progress:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        self.progress_text = ctk.CTkTextbox(progress_frame, height=100)
        self.progress_text.pack(fill="x", padx=10, pady=(0, 10))
        # Bind context menu to progress_text
        self.progress_text_context_menu = self._create_context_menu(self.progress_text)
        self.progress_text.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(
                event, self.progress_text_context_menu
            ),
        )

        # Results section
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=10)

        # Results header with copy button
        results_header = ctk.CTkFrame(results_frame)
        results_header.pack(fill="x", padx=10, pady=(10, 5))

        self.results_label = ctk.CTkLabel(results_header, text="Found Links (0):")
        self.results_label.pack(side="left")

        self.copy_button = ctk.CTkButton(
            results_header,
            text="Copy All Links",
            command=self.copy_links_to_clipboard,
            state="disabled",
            width=120,
        )
        self.copy_button.pack(side="right")

        # Results textbox
        self.results_textbox = ctk.CTkTextbox(
            results_frame, font=ctk.CTkFont(family="Courier", size=11)
        )
        self.results_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        # Bind context menu to results_textbox
        self.results_textbox_context_menu = self._create_context_menu(
            self.results_textbox
        )
        self.results_textbox.bind(
            "<Button-3>",
            lambda event: self._popup_context_menu(
                event, self.results_textbox_context_menu
            ),
        )

    def get_options(self) -> Dict[str, Any]:
        return {
            "start_url": self.start_url_entry.get().strip(),
            "url_prefix": self.url_prefix_entry.get().strip() or None,
            "max_depth": int(self.max_depth_var.get()),
            "max_pages": int(self.max_pages_var.get()),
            "request_delay": float(self.delay_var.get()),
            "user_agent": self.user_agent_entry.get().strip() or None,
        }

    def set_options(self, options: Dict[str, Any]) -> None:
        if "start_url" in options:
            self.start_url_entry.delete(0, "end")
            self.start_url_entry.insert(0, options["start_url"])
        if "url_prefix" in options and options["url_prefix"]:
            self.url_prefix_entry.delete(0, "end")
            self.url_prefix_entry.insert(0, options["url_prefix"])
        if "max_depth" in options:
            self.max_depth_var.set(str(options["max_depth"]))
        if "max_pages" in options:
            self.max_pages_var.set(str(options["max_pages"]))
        if "request_delay" in options:
            self.delay_var.set(str(options["request_delay"]))
        if "user_agent" in options and options["user_agent"]:
            self.user_agent_entry.delete(0, "end")
            self.user_agent_entry.insert(0, options["user_agent"])

    def clear(self) -> None:
        self.progress_text.delete("1.0", "end")
        self.results_textbox.delete("1.0", "end")
        self.results_label.configure(text="Found Links (0):")
        self.found_links = []
        self.export_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")

    def validate_inputs(self) -> bool:
        """Validate user inputs"""
        start_url = self.start_url_entry.get().strip()
        if not start_url:
            messagebox.showerror("Error", "Please enter a start URL")
            return False

        try:
            max_depth = int(self.max_depth_var.get())
            if max_depth < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Max depth must be a non-negative integer")
            return False

        try:
            max_pages = int(self.max_pages_var.get())
            if max_pages < 1:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Max pages must be a positive integer")
            return False

        try:
            delay = float(self.delay_var.get())
            if delay < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Request delay must be a non-negative number")
            return False

        return True

    def start_crawl(self):
        """Start the crawling process"""
        if not self.validate_inputs():
            return

        # Disable controls
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.export_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")

        # Clear previous results
        self.clear()

        # Get options
        options = self.get_options()

        # Start crawling in separate thread
        self.crawl_thread = threading.Thread(target=self._run_crawl, args=(options,))
        self.crawl_thread.daemon = True
        self.crawl_thread.start()

    def _run_crawl(self, options: Dict[str, Any]):
        """Run crawl in separate thread"""
        try:
            self.found_links = self.crawler.crawl(**options)
            self.master.after(0, self._crawl_completed)
        except Exception as e:
            self.master.after(0, lambda: self.show_error(f"Crawl error: {str(e)}"))
            self.master.after(0, self._crawl_completed)

    def _crawl_completed(self):
        """Handle crawl completion"""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

        if self.found_links:
            self.export_button.configure(state="normal")
            self.copy_button.configure(state="normal")

        # Update results display
        self.results_label.configure(text=f"Found Links ({len(self.found_links)}):")
        self._display_formatted_links()

    def _display_formatted_links(self):
        """Display links in the specified format with square brackets"""
        if not self.found_links:
            return

        for link in self.found_links:
            self.results_textbox.insert("end", f"[{link}]\n")

        if len(self.found_links) > 3:
            self.results_textbox.insert(
                "end", f"\n(Total: {len(self.found_links)} links)"
            )

    def stop_crawl(self):
        """Stop the crawling process"""
        self.crawler.stop_crawl()

    def export_results(self):
        """Export results to file"""
        if not self.found_links:
            pass
            return

        filename = filedialog.asksaveasfilename(
            title="Save Links",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if filename:
            if self.crawler.export_links_to_file(self.found_links, filename):
                pass

    def copy_links_to_clipboard(self):
        """Copy all found links to clipboard"""
        if not self.found_links:
            pass
            return

        try:
            formatted_text = ""
            for link in self.found_links:
                formatted_text += f"[{link}]\n"

            if len(self.found_links) > 3:
                formatted_text += f"\n(Total: {len(self.found_links)} links)"

            pyperclip.copy(formatted_text)
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")

    def update_progress(self, message: str):
        """Update progress display"""
        self.master.after(0, lambda: self._update_progress_ui(message))

    def _update_progress_ui(self, message: str):
        """Update progress UI (must run on main thread)"""
        self.progress_text.insert("end", f"{message}\n")
        self.progress_text.see("end")

    def show_error(self, message: str):
        """Show error message"""
        self.master.after(0, lambda: self._show_error_ui(message))

    def _show_error_ui(self, message: str):
        """Show error UI (must run on main thread)"""
        self.progress_text.insert("end", f"ERROR: {message}\n")
        self.progress_text.see("end")
        messagebox.showerror("Error", message)
