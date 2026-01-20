# views/settings_page.py

import tkinter as tk
from views.themed_frame import ThemedFrame
from views.theme_preview import ThemePreview


class SettingsPage(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.controller = controller

        self.label = tk.Label(
            self, text="Settings Page", font=("Arial", 20))
        self.label.pack(pady=20)

        # --- Theme Grid Section ---
        grid_frame = tk.Frame(self)
        grid_frame.pack(pady=10)

        themes = controller.themes
        columns = 3

        row = 0
        col = 0

        for theme_name, theme_data in themes.items():
            preview = ThemePreview(
                grid_frame,
                theme_name,
                theme_data,
                on_click=self.set_theme
            )
            preview.grid(row=row, column=col, padx=10, pady=10)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        # --- Preferences Section ---
        prefs_frame = tk.Frame(self)
        prefs_frame.pack(pady=20)

        # Language selector
        self.lbl_language = tk.Label(prefs_frame, text="Language")
        self.lbl_language.pack()
        lang_var = tk.StringVar(value=self.controller.shared_data["language"])
        tk.OptionMenu(
            prefs_frame, lang_var, "en", "jp", command=self.set_language
        ).pack(pady=5)

        # Font size selector
        self.lbl_font = tk.Label(prefs_frame, text="Font Size")
        self.lbl_font.pack()
        size_var = tk.StringVar(value=self.controller.shared_data["font_size"])
        tk.OptionMenu(
            prefs_frame, size_var,
            "small", "medium", "large",
            command=self.set_font_size
        ).pack(pady=5)

        # Color mode selector
        self.lbl_color = tk.Label(prefs_frame, text="Color Mode")
        self.lbl_color.pack()
        mode_var = tk.StringVar(
            value=self.controller.shared_data["color_mode"])
        tk.OptionMenu(
            prefs_frame,
            mode_var,
            "normal", "dark", "highcontrast",
            command=self.set_color_mode
        ).pack(pady=5)

        # Back button
        self.btn_back = tk.Button(
            self,
            text="Back to Home",
            command=lambda: controller.show_frame("HomePage")
        )
        self.btn_back.pack(pady=5)

        # Reset to defaults
        tk.Button(
            prefs_frame,
            text="Reset to Defaults",
            command=self.reset_defaults
        ).pack(pady=10)

    # multilingual version:
    def set_language(self, lang):
        self.controller.shared_data["language"] = lang
        self.controller.save_settings()

        # Refresh ALL pages
        for frame in self.controller.frames.values():
            if hasattr(frame, "refresh_text"):
                frame.refresh_text()

        self.controller.apply_theme()

    def set_font_size(self, size):
        self.controller.shared_data["font_size"] = size
        self.controller.save_settings()
        self.controller.apply_theme()

    def set_color_mode(self, mode):
        self.controller.shared_data["color_mode"] = mode
        self.controller.save_settings()
        self.controller.apply_theme()

    def set_theme(self, theme_name):
        self.controller.shared_data["theme"] = theme_name
        self.controller.save_settings()
        self.controller.apply_theme()

    def refresh_text(self):
        self.label.config(text=self.controller.t("settings"))
        self.lbl_language.config(text=self.controller.t("language"))
        self.lbl_font.config(text=self.controller.t("font_size"))
        self.lbl_color.config(text=self.controller.t("color_mode"))
        self.btn_back.config(text=self.controller.t("back_home"))

    def reset_defaults(self):
        defaults = {
            "theme": "light",
            "current_page": "SettingsPage",
            "language": "en",
            "font_size": "medium",
            "color_mode": "normal"
        }

        self.controller.shared_data.update(defaults)
        self.controller.save_settings()
        self.refresh_text()
        self.controller.apply_theme()
