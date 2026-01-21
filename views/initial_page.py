# views/initial_page.py

import tkinter as tk
from views.themed_frame import ThemedFrame


class InitialPage(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # grid 4x3
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)

        self.controller = controller

        self.label = tk.Label(
            self, text="initial Page", font=("Arial", 20))
        self.label.grid(column=3, row=0, sticky=tk.NE, padx=5, pady=5)

        # Back button
        self.btn_back = tk.Button(
            self,
            text="Back to Home",
            command=lambda: controller.show_frame("HomePage")
        )
        self.btn_back.grid(column=7, row=0, sticky=tk.NE, padx=5, pady=5)
