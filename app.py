# app.py

import tkinter as tk
# from tkinter import ttk

from controller import Controller
from views.home_page import HomePage
from views.settings_page import SettingsPage
from views.about_page import AboutPage


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tkinter MVC App")
        self.geometry("800x600")

        # Create the container frame (must be tk.Frame, not ttk.Frame)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        # Create the controller with the container
        self.controller = Controller(self.container)

        self._load_frames()

    def _load_frames(self):
        for FrameClass in (HomePage, SettingsPage, AboutPage):
            frame = FrameClass(
                parent=self.container, controller=self.controller)
            self.controller.register_frame(FrameClass.__name__, frame)
            frame.grid(row=0, column=0, sticky="nsew")

        self.controller.show_frame("HomePage")
