import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import Dict, Any, Optional

from ...core import BaseToolFrame

class BlockExtractorFrame(BaseToolFrame):
    def __init__(self, parent, extractor, **kwargs):
        self.extractor = extractor
        super().__init__(parent, **kwargs)

    def setup_ui(self):
        # Title
        title_label = ctk.CTkLabel(
            self, text="Markdown Block Extractor", font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # Input section
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Block type selection
        type_frame = ctk.CTkFrame(input_frame)
        type_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(type_frame, text="Block Type:").pack(side="left", padx=(10, 5))
        self.block_type_var = ctk.StringVar(value="text")
        self.block_type_menu = ctk.CTkOptionMenu(
            type_frame,
            variable=self.block_type_var,
            values=["text", "markdown", "python", "custom"],
            command=self._on_type_change
        )
        self.block_type_menu.pack(side="left", padx=5)

        # Custom delimiters frame (initially hidden)
        self.custom_frame = ctk.CTkFrame(input_frame)
        
        ctk.CTkLabel(self.custom_frame, text="Start:").pack(side="left", padx=(10, 5))
        self.custom_start_entry = ctk.CTkEntry(self.custom_frame, width=100)
        self.custom_start_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.custom_frame, text="End:").pack(side="left", padx=(10, 5))
        self.custom_end_entry = ctk.CTkEntry(self.custom_frame, width=100)
        self.custom_end_entry.pack(side="left", padx=5)

        # Layer selection
        layer_frame = ctk.CTkFrame(input_frame)
        layer_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(layer_frame, text="Target Layer:").pack(side="left", padx=(10, 5))
        self.layer_var = ctk.StringVar(value="1")
        self.layer_entry = ctk.CTkEntry(
            layer_frame, textvariable=self.layer_var, width=60
        )
        self.layer_entry.pack(side="left", padx=5)
        ctk.CTkLabel(layer_frame, text="(1 = outermost)").pack(side="left", padx=5)

        # Input text
        ctk.CTkLabel(input_frame, text="Input Text:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        self.input_text = ctk.CTkTextbox(input_frame, height=150)
        self.input_text.pack(fill="x", padx=10, pady=(0, 10))

        # Control buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.extract_button = ctk.CTkButton(
            button_frame, text="Extract Blocks", command=self.extract_blocks
        )
        self.extract_button.pack(side="left", padx=10, pady=10)

        self.clear_button = ctk.CTkButton(
            button_frame, text="Clear All", command=self.clear
        )
        self.clear_button.pack(side="left", padx=(0, 10), pady=10)

        # Results section
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=10)

        ctk.CTkLabel(results_frame, text="Extracted Blocks:").pack(
            anchor="w", padx=10, pady=(10, 5)
        )

        self.results_text = ctk.CTkTextbox(
            results_frame, font=ctk.CTkFont(family="Courier", size=11)
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Debug output
        debug_frame = ctk.CTkFrame(self)
        debug_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(debug_frame, text="Debug Info:").pack(
            anchor="w", padx=10, pady=(5, 5)
        )
        
        self.debug_text = ctk.CTkTextbox(debug_frame, height=100)
        self.debug_text.pack(fill="x", padx=10, pady=(0, 10))

    def _on_type_change(self, _):
        """Handle block type change"""
        if self.block_type_var.get() == "custom":
            self.custom_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.custom_frame.pack_forget()

    def get_options(self) -> Dict[str, Any]:
        return {
            "block_type": self.block_type_var.get(),
            "target_layer": int(self.layer_var.get()),
            "custom_start": self.custom_start_entry.get().strip(),
            "custom_end": self.custom_end_entry.get().strip()
        }

    def set_options(self, options: Dict[str, Any]) -> None:
        if "block_type" in options:
            self.block_type_var.set(options["block_type"])
            self._on_type_change(None)
        if "target_layer" in options:
            self.layer_var.set(str(options["target_layer"]))
        if "custom_start" in options:
            self.custom_start_entry.delete(0, "end")
            self.custom_start_entry.insert(0, options["custom_start"])
        if "custom_end" in options:
            self.custom_end_entry.delete(0, "end")
            self.custom_end_entry.insert(0, options["custom_end"])

    def clear(self) -> None:
        """Clear all inputs and results"""
        self.input_text.delete("1.0", "end")
        self.results_text.delete("1.0", "end")
        self.debug_text.delete("1.0", "end")
        self.block_type_var.set("text")
        self.layer_var.set("1")
        self.custom_start_entry.delete(0, "end")
        self.custom_end_entry.delete(0, "end")
        self._on_type_change(None)

    def validate_inputs(self) -> bool:
        """Validate user inputs"""
        input_text = self.input_text.get("1.0", "end").strip()
        if not input_text:
            messagebox.showerror("Error", "Please enter some text to process")
            return False

        try:
            layer = int(self.layer_var.get())
            if layer < 1:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Layer must be a positive integer")
            return False

        block_type = self.block_type_var.get()
        if block_type == "custom":
            if not self.custom_start_entry.get().strip():
                messagebox.showerror("Error", "Please enter start delimiter")
                return False
            if not self.custom_end_entry.get().strip():
                messagebox.showerror("Error", "Please enter end delimiter")
                return False

        return True

    def extract_blocks(self) -> None:
        """Extract blocks from input text"""
        if not self.validate_inputs():
            return

        try:
            # Get options
            options = self.get_options()
            
            # Set custom delimiters if needed
            if options["block_type"] == "custom":
                self.extractor.set_custom_delimiters(
                    options["custom_start"],
                    options["custom_end"]
                )

            # Extract blocks
            input_text = self.input_text.get("1.0", "end")
            
            # Debug info
            block_type = options["block_type"]
            delims = self.extractor.block_types[block_type]
            self.debug_text.delete("1.0", "end")
            self.debug_text.insert("end", f"Block type: {block_type}\n")
            self.debug_text.insert("end", f"Start delimiter: {delims[0]!r}\n")
            self.debug_text.insert("end", f"End delimiter: {delims[1]!r}\n")
            self.debug_text.insert("end", f"Target layer: {options['target_layer']}\n")
            self.debug_text.insert("end", f"Input text length: {len(input_text)} chars\n")
            
            blocks = self.extractor.find_blocks(
                input_text,
                options["block_type"],
                options["target_layer"]
            )
            
            self.debug_text.insert("end", f"Found blocks: {len(blocks)}\n")

            # Display results
            self.results_text.delete("1.0", "end")
            
            if not blocks:
                self.results_text.insert("end", "No matching blocks found.")
                return
                
            for i, block in enumerate(blocks, 1):
                self.results_text.insert("end", f"Block {i}:\n")
                self.results_text.insert("end", f"{block}\n")
                if i < len(blocks):
                    self.results_text.insert("end", "\n---\n\n")

        except Exception as e:
            messagebox.showerror("Error", f"Error extracting blocks: {str(e)}")

    def show_error(self, message: str) -> None:
        messagebox.showerror("Error", message)

    def show_success(self, message: str) -> None:
        messagebox.showinfo("Success", message)