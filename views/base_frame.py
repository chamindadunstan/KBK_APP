# views/base_frame.py

import tkinter as tk


class BaseFrame(tk.Frame):
    """
    A simple base class for all pages.
    Provides:
      - access to the controller
      - a .show() helper method
    Does NOT apply theming (ThemedFrame handles that).
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def show(self):
        """Bring this frame to the front."""
        self.controller.show_frame(self.__class__.__name__)
