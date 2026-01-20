# views/home_page.py

# import tkinter as tk
from views.themed_frame import ThemedFrame


class HomePage(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

    def refresh_text(self):
        self.label.config(text=self.controller.t("home"))
        self.btn_settings.config(text=self.controller.t("go_settings"))
        self.btn_about.config(text=self.controller.t("go_about"))
