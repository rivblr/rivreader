from tkinter import messagebox
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, simpledialog
import os
import json
import re
from ttkthemes import ThemedStyle
from .reading_companion import ReadingCompanion
from .theme_manager import ThemeManager
from .prompts import (
    DEFAULT_READING_COMPANION_PROMPT,
    CHARACTER_ANALYSIS_PROMPT,
    LITERARY_ANALYSIS_PROMPT,
    COPYRIGHT_DISCLAIMER,
    prepend_copyright_disclaimer
)

class ModernReadingCompanionGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Reading Companion")
        self.master.geometry("1600x900")

        self.style = ThemedStyle(self.master)
        self.style.set_theme("black")

        self.config_file = "config.json"
        self.api_key = self.load_or_prompt_api_key()
        self.companion = None
        self.conversation_directory = "conversations"
        self.book_name = "No book loaded"
        self.left_panel_expanded = True
        self.selection_mode = False
        self.reopen_button = None

        self.existing_prompts = {
            "Default": DEFAULT_READING_COMPANION_PROMPT,
            "Character Analysis": CHARACTER_ANALYSIS_PROMPT,
            "Literary Analysis": LITERARY_ANALYSIS_PROMPT,
        }
        
        self.current_highlight_color = "yellow"
        self.highlight_colors = {
            "Neon Yellow": "#FFFF00",
            "Neon Pink": "#FF69B4",
            "Neon Green": "#39FF14"}
        self.highlights = []

        self.theme_manager = ThemeManager()
        self.configure_styles()
        self.create_widgets()

    def load_or_prompt_api_key(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
        else:
            api_key = simpledialog.askstring("API Key", "Enter your Anthropic API key:", parent=self.master)
            if api_key:
                with open(self.config_file, 'w') as f:
                    json.dump({'api_key': api_key}, f)
                return api_key
            else:
                self.master.quit()  # Exit if no API key is provided

    def configure_styles(self):
        theme = self.theme_manager.get_current_theme()
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure("TButton", 
                            padding=theme["button_padding"], 
                            font=(theme["font_main"], theme["font_size_main"]), 
                            borderwidth=theme["button_borderwidth"], 
                            relief=theme["button_relief"],
                            background=theme["button_bg"], 
                            foreground=theme["button_fg"])
        self.style.map("TButton", background=[('active', theme["button_active_bg"])])
        self.style.configure("TLabel", background=theme["label_bg"], foreground=theme["label_fg"], 
                            font=(theme["font_main"], theme["font_size_main"]))
        self.style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], 
                            font=(theme["font_main"], theme["font_size_main"]))
        self.style.configure("Horizontal.TProgressbar", background=theme["progress_bar_fg"], 
                            troughcolor=theme["progress_bar_bg"])
        self.style.configure("Custom.TButton", background=theme["button_bg"], foreground=theme["button_fg"], 
                            borderwidth=theme["button_borderwidth"], relief=theme["button_relief"], 
                            padding=theme["button_padding"], font=(theme["font_main"], theme["font_size_main"]))
        self.style.map("Custom.TButton", background=[('active', theme["button_active_bg"])])
        self.style.configure("TNotebook", background=theme["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=theme["notebook_tab_bg"], 
                            foreground=theme["notebook_tab_fg"], padding=[10, 5], 
                            font=(theme["font_main"], theme["font_size_main"]))
        self.style.map("TNotebook.Tab", background=[("selected", theme["notebook_tab_selected_bg"])])
        
        # Update Combobox styles
        self.style.configure("TCombobox", 
                            fieldbackground=theme["dropdown_bg"], 
                            background=theme["dropdown_bg"],
                            foreground=theme["dropdown_fg"],
                            selectbackground=theme["dropdown_highlight_bg"],
                            selectforeground=theme["dropdown_fg"])
        self.style.map("TCombobox", 
                    fieldbackground=[("readonly", theme["dropdown_bg"])],
                    selectbackground=[("readonly", theme["dropdown_highlight_bg"])])
        
        # Configure Scrollbar style
        self.style.configure("Custom.Vertical.TScrollbar", 
                            background=theme["scrollbar_bg"], 
                            troughcolor=theme["bg"], 
                            bordercolor=theme["bg"],
                            arrowcolor=theme["scrollbar_fg"])
        self.style.map("Custom.Vertical.TScrollbar", 
                    background=[("active", theme["scrollbar_fg"])])

        # Configure Menu colors
        self.master.option_add('*Menu.background', theme["menu_bg"])
        self.style.configure('Custom.TMenubutton', 
                            background=theme["menu_bg"],
                            foreground=theme["menu_fg"],
                            padding=theme["button_padding"])
        self.style.map('Custom.TMenubutton',
                    background=[('active', theme["menu_active_bg"])],
                    foreground=[('active', theme["menu_active_fg"])])

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left panel (additional context and system prompt)
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=1)

        # Add collapse/expand button
        self.collapse_button = ttk.Button(self.left_frame, text="◀", command=self.toggle_left_panel, width=2, style="Custom.TButton")
        self.collapse_button.pack(side=tk.TOP, anchor=tk.NE, padx=5, pady=5)

        self.left_notebook = ttk.Notebook(self.left_frame)
        self.left_notebook.pack(fill=tk.BOTH, expand=True)

        # Create System Prompt tab
        self.create_system_prompt_tab()

        # Create Additional Context tabs
        self.create_additional_context_tabs()

        # Create Notes tab
        self.create_notes_tab()

        # Create Summary tab
        self.create_summary_tab()

        # Middle panel (book content and navigation)
        middle_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(middle_frame, weight=2)

        # Menu bar
        menu_frame = ttk.Frame(middle_frame)
        menu_frame.pack(fill=tk.X, pady=(0, 20))

        # Main menu row
        main_menu_frame = ttk.Frame(menu_frame)
        main_menu_frame.pack(fill=tk.X, pady=(0, 10))

        # Center-align buttons in the main menu row
        button_frame = ttk.Frame(main_menu_frame)
        button_frame.pack(expand=True)

        ttk.Button(button_frame, text="Select Book", command=self.select_file, style="Custom.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Custom Instructions", command=self.set_ai_persona, style="Custom.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        # Save/Load dropdown
        save_load_var = tk.StringVar()
        save_load_dropdown = ttk.Combobox(button_frame, textvariable=save_load_var, values=["Save Conversation", "Load Conversation"], state="readonly", style="TCombobox")
        save_load_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        save_load_dropdown.bind("<<ComboboxSelected>>", self.on_save_load_select)

        # Highlighter dropdown
        self.highlighter_var = tk.StringVar()
        self.highlighter_dropdown = ttk.Combobox(button_frame, textvariable=self.highlighter_var, values=list(self.get_highlighter_colors().keys()), state="readonly", style="TCombobox")
        self.highlighter_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        self.highlighter_dropdown.bind("<<ComboboxSelected>>", self.on_highlighter_select)

        # Appearance dropdown
        appearance_var = tk.StringVar()
        appearance_dropdown = ttk.Combobox(button_frame, textvariable=appearance_var, values=["Theme", "Font Size"], state="readonly", style="TCombobox")
        appearance_dropdown.pack(side=tk.LEFT)
        appearance_dropdown.bind("<<ComboboxSelected>>", self.on_appearance_select)

        # Navigation row
        nav_frame = ttk.Frame(menu_frame)
        nav_frame.pack(fill=tk.X)

        # Center-align buttons in the navigation row
        nav_button_frame = ttk.Frame(nav_frame)
        nav_button_frame.pack(expand=True)
        
        self.prev_chapter_button = ttk.Button(nav_button_frame, text="◀ Previous Chapter", command=self.previous_chapter, style="Custom.TButton")
        self.prev_chapter_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(nav_button_frame, text="Update Progress", command=self.toggle_selection_mode, style="Custom.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_chapter_button = ttk.Button(nav_button_frame, text="Next Chapter ▶", command=self.next_chapter, style="Custom.TButton")
        self.next_chapter_button.pack(side=tk.LEFT)

        # Progress bar
        self.progress_bar = ttk.Progressbar(menu_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        self.progress_bar.bind("<Button-1>", self.on_progress_bar_click)

        # Chapter info display
        self.chapter_info = ttk.Label(middle_frame, text="Chapter: N/A", 
                                      font=(self.theme_manager.get_current_theme()["font_main"], 
                                            self.theme_manager.get_current_theme()["font_size_main"]))
        self.chapter_info.pack(pady=(0, 10))

        # Book content display
        self.book_content = scrolledtext.ScrolledText(
            middle_frame, wrap=tk.WORD, 
            bg=self.theme_manager.get_current_theme()["reader_bg"], 
            fg=self.theme_manager.get_current_theme()["reader_fg"], 
            font=(self.theme_manager.get_current_theme()["font_reader"], 
                  self.theme_manager.get_current_theme()["font_size_reader"])
        )
        self.book_content.pack(fill=tk.BOTH, expand=True)
        self.book_content.config(state=tk.NORMAL)
        self.book_content.bind("<Button-1>", self.on_content_click)
        self.book_content.bind("<ButtonRelease-1>", self.on_content_release)

        # Right panel (chat interface)
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=1)

        self.chat_history = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD, height=20, 
            bg=self.theme_manager.get_current_theme()["chat_bg"], 
            fg=self.theme_manager.get_current_theme()["chat_fg"], 
            font=(self.theme_manager.get_current_theme()["font_main"], 
                  self.theme_manager.get_current_theme()["font_size_main"])
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_history.config(state=tk.DISABLED)

        self.chat_history.tag_configure("system", foreground=self.theme_manager.get_current_theme()["system_msg"])
        self.chat_history.tag_configure("assistant", foreground=self.theme_manager.get_current_theme()["assistant_msg"])
        self.chat_history.tag_configure("user", foreground=self.theme_manager.get_current_theme()["user_msg"])

        input_frame = ttk.Frame(right_frame)
        input_frame.pack(fill=tk.X)

        self.chat_entry = ttk.Entry(input_frame, 
                                    font=(self.theme_manager.get_current_theme()["font_main"], 
                                          self.theme_manager.get_current_theme()["font_size_main"]))
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.chat_button = ttk.Button(input_frame, text="Send", command=self.send_message, style="Custom.TButton")
        self.chat_button.pack(side=tk.RIGHT)

        # Bind Enter key to send message
        self.chat_entry.bind("<Return>", lambda event: self.send_message())

    def create_system_prompt_tab(self):
        system_prompt_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(system_prompt_frame, text="System Prompt")

        # Dropdown for existing prompts
        prompt_label = ttk.Label(system_prompt_frame, text="Select Prompt:")
        prompt_label.pack(pady=(10, 5))
        
        self.prompt_var = tk.StringVar(value="Default")
        prompt_dropdown = ttk.Combobox(system_prompt_frame, textvariable=self.prompt_var, values=list(self.existing_prompts.keys()), state="readonly")
        prompt_dropdown.pack(pady=5)
        prompt_dropdown.bind("<<ComboboxSelected>>", self.on_prompt_selected)

        # System prompt text area
        self.system_prompt_text = scrolledtext.ScrolledText(
            system_prompt_frame, wrap=tk.WORD, height=10,
            bg=self.theme_manager.get_current_theme()["bg"], 
            fg=self.theme_manager.get_current_theme()["fg"], 
            font=(self.theme_manager.get_current_theme()["font_main"], 
                  self.theme_manager.get_current_theme()["font_size_main"])
        )
        self.system_prompt_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.system_prompt_text.insert(tk.END, self.existing_prompts["Default"])

        # Buttons for managing prompts
        button_frame = ttk.Frame(system_prompt_frame)
        button_frame.pack(fill=tk.X, pady=10)

        save_button = ttk.Button(button_frame, text="Save Custom", command=self.save_custom_prompt, style="Custom.TButton")
        save_button.pack(side=tk.LEFT, padx=5)

        apply_button = ttk.Button(button_frame, text="Apply Prompt", command=self.apply_prompt, style="Custom.TButton")
        apply_button.pack(side=tk.LEFT, padx=5)

        # Add a checkbox for including the copyright disclaimer
        self.include_copyright_var = tk.BooleanVar(value=True)
        copyright_checkbox = ttk.Checkbutton(system_prompt_frame, text="Include Copyright Disclaimer", 
                                             variable=self.include_copyright_var, 
                                             command=self.update_prompt_preview)
        copyright_checkbox.pack(pady=5)

        # Add a preview area for the full prompt
        preview_label = ttk.Label(system_prompt_frame, text="Full Prompt Preview:")
        preview_label.pack(pady=(10, 5))
        
        self.prompt_preview = scrolledtext.ScrolledText(
            system_prompt_frame, wrap=tk.WORD, height=5,
            bg=self.theme_manager.get_current_theme()["bg"], 
            fg=self.theme_manager.get_current_theme()["fg"], 
            font=(self.theme_manager.get_current_theme()["font_main"], 
                  self.theme_manager.get_current_theme()["font_size_main"])
        )
        self.prompt_preview.pack(fill=tk.BOTH, expand=True, pady=10)
        self.prompt_preview.config(state=tk.DISABLED)

        self.update_prompt_preview()

    def on_prompt_selected(self, event):
        selected_prompt = self.prompt_var.get()
        self.system_prompt_text.delete(1.0, tk.END)
        self.system_prompt_text.insert(tk.END, self.existing_prompts[selected_prompt])
        self.update_prompt_preview()

    def save_custom_prompt(self):
        custom_prompt = self.system_prompt_text.get(1.0, tk.END).strip()
        if custom_prompt:
            name = simpledialog.askstring("Save Custom Prompt", "Enter a name for this custom prompt:")
            if name:
                self.existing_prompts[name] = custom_prompt
                self.prompt_var.set(name)
                self.left_notebook.nametowidget(self.left_notebook.select()).nametowidget("prompt_dropdown")['values'] = list(self.existing_prompts.keys())
                self.add_to_chat_history(f"Custom prompt '{name}' saved.\n", "system")
                self.update_prompt_preview()

    def apply_prompt(self):
        if self.companion:
            new_prompt = self.system_prompt_text.get(1.0, tk.END).strip()
            if self.include_copyright_var.get():
                new_prompt = prepend_copyright_disclaimer(new_prompt)
            self.companion.set_system_prompt(new_prompt)
            self.add_to_chat_history("New system prompt applied.\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def update_prompt_preview(self):
        current_prompt = self.system_prompt_text.get(1.0, tk.END).strip()
        if self.include_copyright_var.get():
            full_prompt = prepend_copyright_disclaimer(current_prompt)
        else:
            full_prompt = current_prompt
        
        self.prompt_preview.config(state=tk.NORMAL)
        self.prompt_preview.delete(1.0, tk.END)
        self.prompt_preview.insert(tk.END, full_prompt)
        self.prompt_preview.config(state=tk.DISABLED)

    def create_additional_context_tabs(self):
        self.additional_context_texts = []
        self.additional_context_buttons = []
        for i in range(1):
            context_frame = ttk.Frame(self.left_notebook)
            self.left_notebook.add(context_frame, text=f"Additional Context")
            
            context_text = scrolledtext.ScrolledText(
                context_frame, wrap=tk.WORD, 
                bg=self.theme_manager.get_current_theme()["bg"], 
                fg=self.theme_manager.get_current_theme()["fg"], 
                font=(self.theme_manager.get_current_theme()["font_main"], 
                      self.theme_manager.get_current_theme()["font_size_main"])
            )
            context_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
            self.additional_context_texts.append(context_text)
            
            set_button = ttk.Button(context_frame, text="Set", command=lambda idx=i: self.set_additional_context(idx), style="Custom.TButton")
            set_button.pack(side=tk.BOTTOM, anchor=tk.SE)
            self.additional_context_buttons.append(set_button)

    def toggle_left_panel(self):
        if self.left_panel_expanded:
            self.paned_window.forget(self.left_frame)
            self.collapse_button.config(text="▶")
            self.create_reopen_button()
        else:
            self.paned_window.insert(0, self.left_frame)
            self.collapse_button.config(text="◀")
            if self.reopen_button:
                self.reopen_button.destroy()
                self.reopen_button = None
        self.left_panel_expanded = not self.left_panel_expanded

    def create_reopen_button(self):
        if not self.reopen_button:
            self.reopen_button = ttk.Button(self.master, text="▶", command=self.toggle_left_panel, width=2, style="Custom.TButton")
            self.reopen_button.place(x=0, y=0)

    def select_file(self):
        file_types = [
            ("Supported files", "*.epub *.txt *.docx *.rtf *.html *.pdf"),
            ("EPUB files", "*.epub"),
            ("Text files", "*.txt"),
            ("Word documents", "*.docx"),
            ("Rich Text Format", "*.rtf"),
            ("HTML files", "*.html"),
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            try:
                self.companion = ReadingCompanion(file_path, self.api_key)
                self.book_name = os.path.basename(file_path)
                self.add_to_chat_history(f"File loaded: {self.book_name}\n", "system")
                self.load_conversation()
                self.update_book_content()
                self.update_chapter_info()
                self.update_system_prompt_display()
                self.load_additional_context()
            except ValueError as e:
                self.add_to_chat_history(f"Error loading file: {str(e)}\n", "system")

    def set_ai_persona(self):
        if self.companion:
            name = simpledialog.askstring("AI Name", "Enter a name for the AI:", parent=self.master)
            role = simpledialog.askstring("AI Role", "Enter a role for the AI (this will be used as the system prompt):", parent=self.master)
            if name and role:
                self.companion.set_ai_persona(name, role)
                self.update_system_prompt_display()
                self.add_to_chat_history(f"AI persona updated. Name: {name}, Role: {role}\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def update_system_prompt_display(self):
        if self.companion and self.companion.system_prompt:
            self.system_prompt_text.config(state=tk.NORMAL)
            self.system_prompt_text.delete(1.0, tk.END)
            self.system_prompt_text.insert(tk.END, f"AI Name: {self.companion.ai_name}\n\nSystem Prompt:\n{self.companion.system_prompt}")
            self.system_prompt_text.config(state=tk.DISABLED)

    def load_additional_context(self):
        if self.companion:
            for i, context in enumerate(self.companion.get_additional_context()):
                self.additional_context_texts[i].delete(1.0, tk.END)
                self.additional_context_texts[i].insert(tk.END, context)

    def set_additional_context(self, index):
        if self.companion:
            content = self.additional_context_texts[index].get(1.0, tk.END).strip()
            self.companion.set_additional_context(index, content)
            self.add_to_chat_history(f"Additional context {index+1} updated.\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def change_font_size(self, new_size):
        current_theme = self.theme_manager.get_current_theme()
        self.theme_manager.update_theme_property(self.theme_manager.current_theme, "font_size_reader", new_size)
        self.book_content.config(font=(current_theme["font_reader"], new_size))

    def on_progress_bar_click(self, event):
        if self.companion:
            width = self.progress_bar.winfo_width()
            click_position = event.x / width
            target_chapter = int(click_position * self.companion.get_total_chapters())
            
            if target_chapter != self.companion.get_current_chapter() - 1:
                if messagebox.askyesno("Confirm Navigation", f"Do you want to move to Chapter {target_chapter + 1}?"):
                    if self.companion.move_to_chapter(target_chapter):
                        self.update_book_content()
                        self.update_chapter_info()
                        self.add_to_chat_history(f"Moved to Chapter {self.companion.get_current_chapter()}\n", "system")
                    else:
                        self.add_to_chat_history("Failed to move to the selected chapter.\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")
            
    def update_book_content(self):
        if self.companion:
            self.book_content.config(state=tk.NORMAL)
            self.book_content.delete(1.0, tk.END)
            
            raw_text = self.companion.get_current_chapter_text()
            
            # Check if the current file is an EPUB
            if self.companion.book_path.lower().endswith('.epub'):
                formatted_text = raw_text  # No additional formatting for EPUBs
            else:
                formatted_text = self.format_text(raw_text)
            
            self.book_content.insert(tk.END, formatted_text)
            self.book_content.config(state=tk.NORMAL)  # Keep it normal for click functionality
            self.update_progress_bar()

    def format_text(self, text):
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n|\. ', text)
        
        # Format each paragraph
        formatted_paragraphs = []
        for paragraph in paragraphs:
            # Trim whitespace and add a newline for paragraph separation
            formatted_paragraph = paragraph.strip() + "\n\n"
            formatted_paragraphs.append(formatted_paragraph)
        
        return ''.join(formatted_paragraphs)

    def update_chapter_info(self):
        if self.companion:
            current_chapter = self.companion.get_current_chapter()
            total_chapters = self.companion.get_total_chapters()
            navigation_unit = self.companion.get_navigation_unit()
            self.chapter_info.config(text=f"{navigation_unit}: {current_chapter}/{total_chapters}")

    def update_progress_bar(self):
        if self.companion:
            progress = self.companion.get_progress_percentage()
            self.progress_bar["value"] = progress
            
    def toggle_selection_mode(self):
        self.selection_mode = not self.selection_mode
        if self.selection_mode:
            self.book_content.config(cursor="hand2")
            self.add_to_chat_history("Selection mode activated. Click on a word to update the assistant's context.\n", "system")
        else:
            self.book_content.config(cursor="")
            self.add_to_chat_history("Selection mode deactivated.\n", "system")

    def on_content_click(self, event):
        if self.selection_mode and self.companion:
            index = self.book_content.index(f"@{event.x},{event.y}")
            line, char = map(int, index.split("."))
            
            word_index = self.companion.document_reader.get_word_index_from_coordinates(line, char)
            
            if self.companion.update_progress(word_index):
                current_chapter = self.companion.get_current_chapter()
                current_word = self.companion.get_current_word_index()
                self.add_to_chat_history(f"Assistant context updated to Chapter {current_chapter}, Word Index: {current_word}\n", "system")
                
                # Highlight the selected word (keep existing code)
                
                # Update progress bar
                self.update_progress_bar()
                
                # Deactivate selection mode
                self.toggle_selection_mode()
            else:
                self.add_to_chat_history("Failed to update context. Please try again.\n", "system")

    def update_progress_bar(self):
        if self.companion:
            progress = self.companion.get_progress_percentage()
            self.progress_bar["value"] = progress

    def on_content_click(self, event):
        if self.selection_mode and self.companion:
            index = self.book_content.index(f"@{event.x},{event.y}")
            line, char = map(int, index.split("."))
            
            word_index = self.companion.document_reader.get_word_index_from_coordinates(line, char)
            
            if self.companion.update_progress(word_index):
                current_chapter = self.companion.get_current_chapter()
                current_word = self.companion.get_current_word_index()
                self.add_to_chat_history(f"Assistant context updated to Chapter {current_chapter}, Word Index: {current_word}\n", "system")
                
                # Highlight the selected word (keep existing code)
                
                # Update progress bar
                self.update_progress_bar()
                
                # Deactivate selection mode
                self.toggle_selection_mode()
            else:
                self.add_to_chat_history("Failed to update context. Please try again.\n", "system")

    def next_chapter(self):
        if self.companion and self.companion.move_to_next_chapter():
            self.update_book_content()
            self.update_chapter_info()
            self.update_progress_bar()
            navigation_unit = self.companion.get_navigation_unit()
            self.add_to_chat_history(f"Moved to {navigation_unit} {self.companion.get_current_chapter()}\n", "system")

    def previous_chapter(self):
        if self.companion and self.companion.move_to_previous_chapter():
            self.update_book_content()
            self.update_chapter_info()
            self.update_progress_bar()
            navigation_unit = self.companion.get_navigation_unit()
            self.add_to_chat_history(f"Moved to {navigation_unit} {self.companion.get_current_chapter()}\n", "system")

    def on_progress_bar_click(self, event):
        if self.companion:
            width = self.progress_bar.winfo_width()
            click_position = event.x / width
            target_chapter = int(click_position * self.companion.get_total_chapters())
            
            if target_chapter != self.companion.get_current_chapter() - 1:
                if messagebox.askyesno("Confirm Navigation", f"Do you want to move to Chapter {target_chapter + 1}?"):
                    if self.companion.move_to_chapter(target_chapter):
                        self.update_book_content()
                        self.update_chapter_info()
                        self.update_progress_bar()
                        self.add_to_chat_history(f"Moved to Chapter {self.companion.get_current_chapter()}\n", "system")
                    else:
                        self.add_to_chat_history("Failed to move to the selected chapter.\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def send_message(self):
        if self.companion:
            message = self.chat_entry.get()
            self.add_to_chat_history(f"You: {message}\n", "user")
            response = self.companion.chat(message)
            self.add_to_chat_history(f"{response}\n", "assistant")
            self.chat_entry.delete(0, tk.END)
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def add_to_chat_history(self, message, message_type):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message, message_type)
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def save_conversation(self):
        if self.companion:
            self.companion.save_conversation(self.conversation_directory)
            self.add_to_chat_history("Conversation saved.\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def load_conversation(self):
        if self.companion:
            if self.companion.load_conversation(self.conversation_directory):
                self.add_to_chat_history("Previous conversation loaded.\n", "system")
                for message in self.companion.conversation_history:
                    self.add_to_chat_history(f"You: {message['user']}\n", "user")
                    self.add_to_chat_history(f"{message['ai']}\n", "assistant")
            else:
                self.add_to_chat_history("No previous conversation found for this book.\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def apply_theme(self, theme_name):
        self.theme_manager.set_current_theme(theme_name)
        self.configure_styles()
        self.update_widgets_theme()

    def update_widgets_theme(self):
        theme = self.theme_manager.get_current_theme()
        self.master.configure(bg=theme["bg"])
        self.book_content.config(bg=theme["reader_bg"], fg=theme["reader_fg"], 
                                 font=(theme["font_reader"], theme["font_size_reader"]))
        self.chat_history.config(bg=theme["chat_bg"], fg=theme["chat_fg"], 
                                 font=(theme["font_main"], theme["font_size_main"]))
        self.chat_history.tag_configure("system", foreground=theme["system_msg"])
        self.chat_history.tag_configure("assistant", foreground=theme["assistant_msg"])
        self.chat_history.tag_configure("user", foreground=theme["user_msg"])
        self.chat_entry.config(font=(theme["font_main"], theme["font_size_main"]))
        self.chapter_info.config(font=(theme["font_main"], theme["font_size_main"]))
        self.system_prompt_text.config(bg=theme["bg"], fg=theme["fg"], 
                                       font=(theme["font_main"], theme["font_size_main"]))
        for context_text in self.additional_context_texts:
            context_text.config(bg=theme["bg"], fg=theme["fg"], 
                                font=(theme["font_main"], theme["font_size_main"]))
        self.configure_menu_colors()
        self.configure_styles()
    
    def configure_menu_colors(self):
        theme = self.theme_manager.get_current_theme()
        self.master.option_add('*Menu.background', theme["menu_bg"])
        self.master.option_add('*Menu.foreground', theme["menu_fg"])
        self.master.option_add('*Menu.selectColor', theme["menu_active_bg"])
        self.master.option_add('*Menu.activeBackground', theme["menu_active_bg"])
        self.master.option_add('*Menu.activeForeground', theme["menu_active_fg"])
    
    def set_highlight_color(self, color):
        self.current_highlight_color = color

    def on_content_release(self, event):
        if self.current_highlight_color:
            try:
                start = self.book_content.index("sel.first")
                end = self.book_content.index("sel.last")
                self.book_content.tag_add(f"highlight_{self.current_highlight_color}", start, end)
                self.book_content.tag_config(f"highlight_{self.current_highlight_color}", background=self.current_highlight_color)
                
                # Store the highlight
                highlighted_text = self.book_content.get(start, end)
                self.highlights.append((start, end, self.current_highlight_color, highlighted_text))
                
                # Update the Notes tab
                self.update_notes_tab()
            except tk.TclError:
                # No text selected
                pass
    
    def create_notes_tab(self):
        notes_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(notes_frame, text="Notes")

        # Create nested notebook for Highlights and Notepad
        notes_notebook = ttk.Notebook(notes_frame)
        notes_notebook.pack(fill=tk.BOTH, expand=True)

        # Highlights tab
        highlights_frame = ttk.Frame(notes_notebook)
        notes_notebook.add(highlights_frame, text="Highlights")

        self.highlights_text = scrolledtext.ScrolledText(
            highlights_frame, wrap=tk.WORD, 
            bg=self.theme_manager.get_current_theme()["bg"], 
            fg=self.theme_manager.get_current_theme()["fg"], 
            font=(self.theme_manager.get_current_theme()["font_main"], 
                  self.theme_manager.get_current_theme()["font_size_main"])
        )
        self.highlights_text.pack(fill=tk.BOTH, expand=True)
        self.highlights_text.config(state=tk.DISABLED)

        # Notepad tab
        notepad_frame = ttk.Frame(notes_notebook)
        notes_notebook.add(notepad_frame, text="Notepad")

        self.notepad_text = scrolledtext.ScrolledText(
            notepad_frame, wrap=tk.WORD, 
            bg=self.theme_manager.get_current_theme()["bg"], 
            fg=self.theme_manager.get_current_theme()["fg"], 
            font=(self.theme_manager.get_current_theme()["font_main"], 
                  self.theme_manager.get_current_theme()["font_size_main"])
        )
        self.notepad_text.pack(fill=tk.BOTH, expand=True)

        # Export button
        export_button = ttk.Button(notes_frame, text="Export Notes", command=self.export_notes, style="Custom.TButton")
        export_button.pack(pady=10)

    def update_notes_tab(self):
        self.highlights_text.config(state=tk.NORMAL)
        self.highlights_text.delete(1.0, tk.END)
        for start, end, color, text in self.highlights:
            self.highlights_text.insert(tk.END, f"[{color}] {text}\n\n")
            last_insert = self.highlights_text.index(tk.INSERT)
            self.highlights_text.tag_add(f"highlight_{color}", f"{last_insert} linestart", f"{last_insert} lineend")
            self.highlights_text.tag_config(f"highlight_{color}", background=color)
        self.highlights_text.config(state=tk.DISABLED)

    def export_notes(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write("Highlights:\n\n")
                for _, _, color, text in self.highlights:
                    file.write(f"[{color}] {text}\n\n")
                file.write("\nNotes:\n\n")
                file.write(self.notepad_text.get(1.0, tk.END))
            self.add_to_chat_history(f"Notes exported to {file_path}\n", "system")

    def create_summary_tab(self):
        summary_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(summary_frame, text="Summary")

        self.summary_text = scrolledtext.ScrolledText(
            summary_frame, wrap=tk.WORD,
            bg=self.theme_manager.get_current_theme()["bg"],
            fg=self.theme_manager.get_current_theme()["fg"],
            font=(self.theme_manager.get_current_theme()["font_main"],
                  self.theme_manager.get_current_theme()["font_size_main"])
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.summary_text.config(state=tk.DISABLED)

        button_frame = ttk.Frame(summary_frame)
        button_frame.pack(fill=tk.X)

        refresh_button = ttk.Button(button_frame, text="Refresh", command=self.refresh_summary, style="Custom.TButton")
        refresh_button.pack(side=tk.LEFT, padx=5)

        export_button = ttk.Button(button_frame, text="Export Summary", command=self.export_summary, style="Custom.TButton")
        export_button.pack(side=tk.LEFT, padx=5)

    def refresh_summary(self):
        if self.companion:
            summary = self.companion.get_context_summary()
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, summary)
            self.summary_text.config(state=tk.DISABLED)
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def export_summary(self):
        if self.companion:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                summary = self.companion.get_context_summary()
                with open(file_path, "w") as file:
                    file.write(summary)
                self.add_to_chat_history(f"Summary exported to {file_path}\n", "system")
        else:
            self.add_to_chat_history("Please select a book first.\n", "system")

    def on_save_load_select(self, event):
        selection = event.widget.get()
        if selection == "Save Conversation":
            self.save_conversation()
        elif selection == "Load Conversation":
            self.load_conversation()
        event.widget.set('')  # Reset the dropdown

    def on_highlighter_select(self, event):
        color_name = event.widget.get()
        color = self.get_highlighter_colors()[color_name]
        self.set_highlight_color(color)
        event.widget.set('')  # Reset the dropdown

    def on_appearance_select(self, event):
        selection = event.widget.get()
        if selection == "Theme":
            self.show_theme_menu()
        elif selection == "Font Size":
            self.show_font_size_menu()
        event.widget.set('')  # Reset the dropdown

    def show_theme_menu(self):
        theme_menu = tk.Menu(self.master, tearoff=0)
        for theme_name in self.theme_manager.get_theme_names():
            theme_menu.add_command(label=theme_name, command=lambda tn=theme_name: self.apply_theme(tn))
        theme_menu.post(self.master.winfo_pointerx(), self.master.winfo_pointery())

    def show_font_size_menu(self):
        font_size_menu = tk.Menu(self.master, tearoff=0)
        for size in range(8, 25, 2):
            font_size_menu.add_command(label=str(size), command=lambda s=size: self.change_font_size(s))
        font_size_menu.post(self.master.winfo_pointerx(), self.master.winfo_pointery())

    def get_highlighter_colors(self):
        theme = self.theme_manager.get_current_theme()
        return theme.get("highlighter_colors", {
            "Neon Yellow": "#FFFF00",
            "Neon Pink": "#FF69B4",
            "Neon Green": "#39FF14"
        })
    