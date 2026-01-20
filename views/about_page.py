# views/about_page.py

import tkinter as tk
from views.themed_frame import ThemedFrame


class AboutPage(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Container for all content
        container = tk.Frame(self)
        container.pack(pady=20)
