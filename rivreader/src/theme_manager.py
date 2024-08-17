from typing import Dict, Any, List
import json
import os

class ThemeManager:
    def __init__(self):
        self.themes = {
            "modern_dark": {
                "bg": "#000000",
                "fg": "#FFFFFF",
                "button_bg": "#000000",
                "button_fg": "#FFFFFF",
                "button_active_bg": "#222222",
                "entry_bg": "#000000",
                "entry_fg": "#FFFFFF",
                "reader_bg": "#061123",
                "reader_fg": "#70798C",
                "chat_bg": "#000000",
                "chat_fg": "#FFFFFF",
                "system_msg": "#00FF00",
                "assistant_msg": "#A5D7E8",
                "user_msg": "#FF69B4",
                "font_main": "Menlo",
                "font_reader": "Verdana",
                "font_size_main": 12,
                "font_size_reader": 16,
                "button_relief": "flat",
                "button_borderwidth": 1,
                "button_padding": 10,
                "progress_bar_bg": "#000000",
                "progress_bar_fg": "#226CE0",
                "highlight_bg": "#FFFF00",
                "highlight_fg": "#000000",
                "notebook_tab_bg": "#000000",
                "notebook_tab_fg": "#FFFFFF",
                "notebook_tab_selected_bg": "#226CE0",
                "scrollbar_bg": "#222222",
                "scrollbar_fg": "#666666",
                "combobox_bg": "#000000",
                "combobox_fg": "#FFFFFF",
                "combobox_listbox_bg": "#222222",
                "combobox_listbox_fg": "#FFFFFF",
                "menu_bg": "#000000",
                "menu_fg": "#FFFFFF",
                "menu_active_bg": "#226CE0",
                "menu_active_fg": "#FFFFFF",
                "tooltip_bg": "#333333",
                "tooltip_fg": "#FFFFFF",
                "separator_color": "#444444",
                "label_bg": "#000000",
                "label_fg": "#FFFFFF",
                "dropdown_bg": "#222222",
                "dropdown_fg": "#FFFFFF",
                "dropdown_highlight_bg": "#444444",
                "dialog_bg": "#111111",
                "dialog_fg": "#FFFFFF",
                "highlighter_colors": {
                    "Neon Yellow": "#FFFF00",
                    "Neon Pink": "#FF69B4",
                    "Neon Green": "#39FF14"
                }
            },
            "modern_light": {
                "bg": "#FFFFFF",
                "fg": "#000000",
                "button_bg": "#FFFFFF",
                "button_fg": "#000000",
                "button_active_bg": "#A3F3F5",
                "entry_bg": "#FFFFFF",
                "entry_fg": "#000000",
                "reader_bg": "#FAF5F0",
                "reader_fg": "#143642",
                "chat_bg": "#FFFFFF",
                "chat_fg": "#000000",
                "system_msg": "#0E7F81",
                "assistant_msg": "#143642",
                "user_msg": "#932548",
                "font_main": "Menlo",
                "font_reader": "Verdana",
                "font_size_main": 12,
                "font_size_reader": 16,
                "button_relief": "flat",
                "button_borderwidth": 1,
                "button_padding": 10,
                "progress_bar_bg": "#FFFFFF",
                "progress_bar_fg": "#20BF55",
                "highlight_bg": "#FFFF00",
                "highlight_fg": "#000000",
                "notebook_tab_bg": "#16C7CA",
                "notebook_tab_fg": "#000000",
                "notebook_tab_selected_bg": "#A3F3F5",
                "scrollbar_bg": "#E0E0E0",
                "scrollbar_fg": "#999999",
                "combobox_bg": "#FFFFFF",
                "combobox_fg": "#000000",
                "combobox_listbox_bg": "#FFFFFF",
                "combobox_listbox_fg": "#000000",
                "menu_bg": "#FFFFFF",
                "menu_fg": "#000000",
                "menu_active_bg": "#A3F3F5",
                "menu_active_fg": "#000000",
                "tooltip_bg": "#FFFFCC",
                "tooltip_fg": "#000000",
                "separator_color": "#CCCCCC",
                "label_bg": "#FFFFFF",
                "label_fg": "#000000",
                "dropdown_bg": "#F0F0F0",
                "dropdown_fg": "#000000",
                "dropdown_highlight_bg": "#D0D0D0",
                "dialog_bg": "#FFFFFF",
                "dialog_fg": "#000000",
                "highlighter_colors": {
                    "Pastel Yellow": "#FFFFA5",
                    "Pastel Pink": "#FFB3BA",
                    "Pastel Green": "#BAFFC9"
                }
            },
            "classic_dark": {
                "bg": "#1E1E1E",
                "fg": "#D4D4D4",
                "button_bg": "#2D2D2D",
                "button_fg": "#D4D4D4",
                "button_active_bg": "#3D3D3D",
                "entry_bg": "#2D2D2D",
                "entry_fg": "#D4D4D4",
                "reader_bg": "#252526",
                "reader_fg": "#D4D4D4",
                "chat_bg": "#1E1E1E",
                "chat_fg": "#D4D4D4",
                "system_msg": "#6A9955",
                "assistant_msg": "#569CD6",
                "user_msg": "#CE9178",
                "font_main": "Open Sans",
                "font_reader": "Calibri",
                "font_size_main": 10,
                "font_size_reader": 16,
                "button_relief": "raised",
                "button_borderwidth": 2,
                "button_padding": 5,
                "progress_bar_bg": "#333333",
                "progress_bar_fg": "#569CD6",
                "highlight_bg": "#FFFF00",
                "highlight_fg": "#000000",
                "notebook_tab_bg": "#2D2D2D",
                "notebook_tab_fg": "#D4D4D4",
                "notebook_tab_selected_bg": "#1E1E1E",
                "scrollbar_bg": "#2D2D2D",
                "scrollbar_fg": "#4D4D4D",
                "combobox_bg": "#2D2D2D",
                "combobox_fg": "#D4D4D4",
                "combobox_listbox_bg": "#3D3D3D",
                "combobox_listbox_fg": "#D4D4D4",
                "menu_bg": "#2D2D2D",
                "menu_fg": "#D4D4D4",
                "menu_active_bg": "#3D3D3D",
                "menu_active_fg": "#FFFFFF",
                "tooltip_bg": "#3D3D3D",
                "tooltip_fg": "#D4D4D4",
                "separator_color": "#4D4D4D",
                "label_bg": "#1E1E1E",
                "label_fg": "#D4D4D4",
                "dropdown_bg": "#2D2D2D",
                "dropdown_fg": "#D4D4D4",
                "dropdown_highlight_bg": "#3D3D3D",
                "dialog_bg": "#1E1E1E",
                "dialog_fg": "#D4D4D4",
                "highlighter_colors": {
                    "Bright Yellow": "#FFFF00",
                    "Bright Pink": "#FF1493",
                    "Bright Green": "#00FF00"
                }
            },
            "classic_light": {
                "bg": "#F3F3F3",
                "fg": "#333333",
                "button_bg": "#E1E1E1",
                "button_fg": "#333333",
                "button_active_bg": "#D1D1D1",
                "entry_bg": "#FFFFFF",
                "entry_fg": "#333333",
                "reader_bg": "#FFFFFF",
                "reader_fg": "#333333",
                "chat_bg": "#F3F3F3",
                "chat_fg": "#333333",
                "system_msg": "#008000",
                "assistant_msg": "#0000FF",
                "user_msg": "#8B0000",
                "font_main": "Open Sans",
                "font_reader": "Calibri",
                "font_size_main": 10,
                "font_size_reader": 16,
                "button_relief": "raised",
                "button_borderwidth": 2,
                "button_padding": 5,
                "progress_bar_bg": "#E1E1E1",
                "progress_bar_fg": "#4CAF50",
                "highlight_bg": "#FFFF00",
                "highlight_fg": "#000000",
                "notebook_tab_bg": "#E1E1E1",
                "notebook_tab_fg": "#333333",
                "notebook_tab_selected_bg": "#F3F3F3",
                "scrollbar_bg": "#E1E1E1",
                "scrollbar_fg": "#B1B1B1",
                "combobox_bg": "#FFFFFF",
                "combobox_fg": "#333333",
                "combobox_listbox_bg": "#FFFFFF",
                "combobox_listbox_fg": "#333333",
                "menu_bg": "#F3F3F3",
                "menu_fg": "#333333",
                "menu_active_bg": "#D1D1D1",
                "menu_active_fg": "#000000",
                "tooltip_bg": "#FFFFC0",
                "tooltip_fg": "#333333",
                "separator_color": "#D1D1D1",
                "label_bg": "#F3F3F3",
                "label_fg": "#333333",
                "dropdown_bg": "#F3F3F3",
                "dropdown_fg": "#333333",
                "dropdown_highlight_bg": "#D1D1D1",
                "dialog_bg": "#FFFFFF",
                "dialog_fg": "#333333",
                "highlighter_colors": {
                    "Light Yellow": "#FFFFE0",
                    "Light Pink": "#FFB6C1",
                    "Light Green": "#90EE90"
                }
            }
        }
        self.config_file = "theme_config.json"
        self.current_theme = self.load_theme()

    def get_theme(self, theme_name: str) -> Dict[str, Any]:
        return self.themes.get(theme_name, self.themes["modern_dark"])

    def set_current_theme(self, theme_name: str) -> None:
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.save_theme()

    def get_current_theme(self) -> Dict[str, Any]:
        return self.themes[self.current_theme]

    def get_theme_names(self) -> List[str]:
        return list(self.themes.keys())

    def update_theme_property(self, theme_name: str, property_name: str, value: Any) -> None:
        if theme_name in self.themes and property_name in self.themes[theme_name]:
            self.themes[theme_name][property_name] = value
            if theme_name == self.current_theme:
                self.save_theme()

    def add_new_theme(self, theme_name: str, theme_properties: Dict[str, Any]) -> None:
        if all(key in theme_properties for key in self.themes["modern_dark"].keys()):
            self.themes[theme_name] = theme_properties
        else:
            raise ValueError("New theme must contain all properties present in the default theme.")

    def save_theme(self) -> None:
        with open(self.config_file, 'w') as f:
            json.dump({"current_theme": self.current_theme}, f)

    def load_theme(self) -> str:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get("current_theme", "modern_dark")
        return "modern_dark"