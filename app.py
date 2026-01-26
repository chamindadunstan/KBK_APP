# app.py
import sys
import os
import tkinter as tk
# from tkinter import ttk
from waveform import draw_test_waveform

from controller import Controller
from views.home_page import HomePage
from views.settings_page import SettingsPage
from views.initial_page import InitialPage
from views.about_page import AboutPage


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("KBK App")
        self.geometry("800x440")
        self.iconbitmap(resource_path("assets/kbk.ico"))
        # Create the container frame (must be tk.Frame, not ttk.Frame)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        # Create the controller with the container
        self.controller = Controller(self.container)

        self._load_frames()

    def _load_frames(self):
        for FrameClass in (HomePage, SettingsPage, InitialPage, AboutPage):
            frame = FrameClass(
                parent=self.container, controller=self.controller)
            self.controller.register_frame(FrameClass.__name__, frame)
            frame.grid(row=0, column=0, sticky="nsew")

        # Show home page
        self.controller.show_frame("HomePage")

        # Inject waveform
        draw_test_waveform(self.controller)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):  # type: ignore
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
