# controller.py

import json
import os


class Controller:
    def __init__(self, container):
        # The parent widget (usually the main app's frame container)
        self.container = container

        # Load environment variables
        self.app_name = os.getenv("APP_NAME")
        self.test_path = os.getenv("TEST_PROJECT")
        self.default_theme = os.getenv("DEFAULT_THEME")
        self.app_env = os.getenv("APP_ENV")
        self.debug_mode = os.getenv("DEBUG")
        self.default_language = os.getenv("DEFAULT_LANGUAGE")
        self.default_font_size = os.getenv("DEFAULT_FONT_SIZE")
        self.default_color_mode = os.getenv("DEFAULT_COLOR_MODE")
        self.project_root = os.getenv("PROJECT_ROOT")
        self.vscode_path = os.getenv("VSCODE_PATH")
        self.python_path = os.getenv("PYTHON_PATH")

        # Validate environment variables
        self.validate_env()

        # Stores all frames/pages by name
        self.frames = {}

        # Shared data accessible by all frames
        # Example usage:
        # controller.shared_data["theme"] = "dark"
        # Example: controller.shared_data["username"] = "Chaminda"

        # Default settings
        self.shared_data = {
            "theme": "light",        # default theme light/dark
            "current_page": None,    # will be set by show_frame()
            "language": "en",        # en, jp, etc.
            "font_size": "medium",   # small, medium, large
            "color_mode": "normal"   # normal, dark, highcontrast
        }

        # Load saved settings
        self.load_settings()

        # --- TRANSLATIONS ---
        self.translations = {
            "en": {
                "home": "Home Page",
                "settings": "Settings Page",
                "about": "About This App",
                "back_home": "Back to Home",
                "version": "Version 1.0.0\nCreated by Chaminda",

                # NEW LABELS
                "language": "Language",
                "font_size": "Font Size",
                "color_mode": "Color Mode",

                "go_settings": "Go to Settings",
                "go_about": "Go to About",
                # about page
                "about_desc": "This is a Tkinter MVC demo with theming."
            },

            "jp": {
                "home": "ホームページ",
                "settings": "設定ページ",
                "about": "このアプリについて",
                "back_home": "ホームに戻る",
                "version": "バージョン 1.0.0\nChaminda 作成",

                # NEW LABELS
                "language": "言語",
                "font_size": "文字サイズ",
                "color_mode": "カラーモード",

                "go_settings": "設定ページへ",
                "go_about": "アプリ情報へ",
                # about page
                "about_desc": "これはテーマ付きの Tkinter MVC デモです。"
            }
        }

        # Theme definitions (light and dark)
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "button_bg": "#e0e0e0"
            },
            "dark": {
                "bg": "#2b2b2b",
                "fg": "#ffffff",
                "button_bg": "#444444"
            },
            "blue": {
                "bg": "#dce9ff",
                "fg": "#0a1a33",
                "button_bg": "#a9c4ff"
            },
            "solarized": {
                "bg": "#fdf6e3",
                "fg": "#657b83",
                "button_bg": "#eee8d5"
            },
            "highcontrast": {
                "bg": "#000000",
                "fg": "#ffff00",
                "button_bg": "#333333"
            }
        }

    # Validate environment variables
    def validate_env(self):
        """Check required environment
        variables and warn if any are missing."""
        required_vars = [
            "APP_NAME",
            "APP_ENV",
            "DEBUG",
            "DEFAULT_THEME",
            "DEFAULT_LANGUAGE",
            "DEFAULT_FONT_SIZE",
            "DEFAULT_COLOR_MODE",
            "PROJECT_ROOT",
            "TEST_PROJECT",
            "VSCODE_PATH",
            "PYTHON_PATH"
        ]

        missing = [var for var in required_vars if os.getenv(var) is None]

        if missing:
            print("\n[ENV VALIDATION WARNING]")
            print("The following environment variables are missing:")
            for var in missing:
                print(f"  - {var}")
            print("Please update your .env file.\n")
        else:
            print(
                "[ENV VALIDATION] All environment variables loaded "
                "successfully."
            )

    def register_frame(self, name, frame):
        """
        Register a frame with a name so it can be shown later.
        Example: controller.register_frame("HomePage", home_page_instance)
        """
        self.frames[name] = frame

    def show_frame(self, name):
        self.shared_data["current_page"] = name
        """
        Bring the requested frame to the front.
        Uses tkraise() to switch pages.
        Includes error handling if the frame is not registered.
        """
        try:
            self.frames[name].tkraise()
        except KeyError:
            print(f"[Controller] Frame '{name}' not registered.")

    def get_frame(self, name):
        """
        Retrieve a frame instance by name.
        Useful when you want to call a method on another frame.
        Example: controller.get_frame("SettingsPage").refresh()
        """
        return self.frames.get(name)

    # --- TRANSLATION HELPER ---
    def t(self, key):
        lang = self.shared_data["language"]
        return self.translations[lang][key]

    def apply_theme(self):
        # SAFETY CHECK — prevents KeyError when current_page is None
        page = self.shared_data.get("current_page")
        if not page or page not in self.frames:
            return

        # --- COLOR MODE SUPPORT ---
        color_mode_map = {
            "normal": "light",
            "dark": "dark",
            "highcontrast": "highcontrast"
        }
        # Convert color mode → theme name
        self.shared_data["theme"] = color_mode_map[
            self.shared_data["color_mode"]
        ]

        # Now load the theme
        theme_name = self.shared_data["theme"]
        theme = self.themes[theme_name]

        # Apply theme only to the current page
        current = self.frames[self.shared_data["current_page"]]
        current.apply_theme(theme)

    # --- SETTINGS: LOAD ---
    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r", encoding="utf-8") as f:
                self.shared_data.update(json.load(f))
        else:
            self.save_settings()

    # --- SETTINGS: SAVE ---
    def save_settings(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.shared_data, f, indent=4)
