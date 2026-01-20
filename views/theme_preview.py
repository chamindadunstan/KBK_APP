# views/theme_preview.py

import tkinter as tk


class ThemePreview(tk.Frame):
    def __init__(self, parent, theme_name, theme_data, on_click=None):
        super().__init__(parent, bd=1, relief="solid", width=120, height=80)

        self.theme_name = theme_name
        self.theme_data = theme_data
        self.on_click = on_click

        # Prevent auto-resizing
        self.pack_propagate(False)

        # Title
        tk.Label(
            self,
            text=theme_name.capitalize(),
            bg=theme_data["bg"],
            fg=theme_data["fg"],
            font=("Arial", 12, "bold")
        ).pack(fill="x")

        # Preview area
        preview = tk.Frame(
            self,
            bg=theme_data["bg"],
            height=40
        )
        preview.pack(fill="both", expand=True)

        # Optional click handler
        if on_click:
            self.bind("<Button-1>", lambda e: on_click(theme_name))
            preview.bind("<Button-1>", lambda e: on_click(theme_name))
