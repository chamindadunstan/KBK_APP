# views/themed_frame.py

import tkinter as tk


class ThemedFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def apply_theme(self, theme):
        """
        Apply theme colors to this frame and all child widgets.
        """
        self.configure(bg=theme["bg"])
        self._apply_to_children(self, theme)

    def _apply_to_children(self, widget, theme):
        """
        Recursively apply theme to all widgets inside this frame.
        """
        for child in widget.winfo_children():
            # --- FONT SIZE SUPPORT ---
            font_scale = {
                "small": 10,
                "medium": 12,
                "large": 14
            }
            size = font_scale[self.controller.shared_data["font_size"]]

            # Frame-like widgets
            if isinstance(child, (tk.Frame, tk.LabelFrame)):
                child.configure(bg=theme["bg"])

            # Labels
            elif isinstance(child, tk.Label):
                child.configure(
                    bg=theme["bg"],
                    fg=theme["fg"],
                    font=("Arial", size)
                )

            # Buttons
            elif isinstance(child, tk.Button):
                child.configure(
                    bg=theme["button_bg"],
                    fg=theme["fg"],
                    activebackground=theme["button_bg"],
                    activeforeground=theme["fg"],
                    font=("Arial", size)
                )

            # Entry fields
            elif isinstance(child, tk.Entry):
                child.configure(
                    bg=theme["bg"],
                    fg=theme["fg"],
                    insertbackground=theme["fg"],
                    font=("Arial", size)
                )

            # Text widgets
            elif isinstance(child, tk.Text):
                child.configure(
                    bg=theme["bg"],
                    fg=theme["fg"],
                    insertbackground=theme["fg"],
                    font=("Arial", size)
                )

            # Recursively theme children of this widget
            if child.winfo_children():
                self._apply_to_children(child, theme)
