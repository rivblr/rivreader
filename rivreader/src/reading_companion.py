import json
import os
from typing import List, Dict
import importlib
from .document_reader import DocumentReader
from .context_manager import ContextManager
from .prompts import (
    DEFAULT_READING_COMPANION_PROMPT,
    CHARACTER_ANALYSIS_PROMPT,
    LITERARY_ANALYSIS_PROMPT,
    prepend_copyright_disclaimer
)

class ReadingCompanion:
    def __init__(self, file_path: str, api_key: str):
        self.document_reader = DocumentReader(file_path)
        self.context_manager = ContextManager(self.document_reader, api_key)
        self.api_key = api_key
        self.book_path = file_path
        self.conversation_history: List[Dict[str, str]] = []
        self.anthropic_module = None
        self.client = None
        self.ai_name = "Assistant"
        self.system_prompt = DEFAULT_READING_COMPANION_PROMPT
        self.total_words = sum(chapter['word_count'] for chapter in self.document_reader.chapters)
        self.current_word = 0
        self._init_client()
    
    def _init_client(self):
        if self.client is None:
            try:
                if self.anthropic_module is None:
                    self.anthropic_module = importlib.import_module('anthropic')
                self.client = self.anthropic_module.Anthropic(api_key=self.api_key)
            except ImportError:
                print("Error: Unable to import anthropic module. Please ensure it's installed.")
            except Exception as e:
                print(f"Error initializing Anthropic client: {str(e)}")

    def _call_ai_model(self, context, message):
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": context},
                    {"role": "assistant", "content": f"As {self.ai_name}, I understand. I'm ready to assist with the book."},
                    {"role": "user", "content": message}
                ]
            )
            return f"{self.ai_name}: {response.content[0].text}"
        except Exception as e:
            return f"An error occurred while processing your request: {str(e)}"

    def set_additional_context(self, index: int, content: str):
        if 0 <= index < 3:
            self.context_manager.set_additional_context(index, content)
        else:
            raise ValueError("Additional context index must be 0, 1, or 2")

    def get_additional_context(self) -> List[str]:
        return self.context_manager.get_additional_context()

    def update_progress(self, new_word_index: int) -> bool:
        if 0 <= new_word_index < self.total_words:
            words_count = 0
            for i, chapter in enumerate(self.document_reader.chapters):
                if words_count + chapter['word_count'] > new_word_index:
                    self.document_reader.current_chapter = i
                    self.document_reader.current_word = new_word_index - words_count
                    break
                words_count += chapter['word_count']

            self.current_word = new_word_index
            self.context_manager.update_context(self.document_reader.current_word)
            return True
        return False

    def get_progress_percentage(self) -> float:
        if self.total_words > 0:
            return (self.current_word / self.total_words) * 100
        return 0

    def move_to_chapter(self, chapter_number: int) -> bool:
        if self.document_reader.move_to_chapter(chapter_number):
            self.current_word = sum(self.document_reader.chapters[i]['word_count'] for i in range(chapter_number))
            self.context_manager.update_context(0)
            return True
        return False

    def get_current_chapter_text(self) -> str:
        return self.document_reader.get_current_chapter_text()

    def get_total_chapters(self) -> int:
        return self.document_reader.get_total_chapters()

    def get_current_chapter(self) -> int:
        return self.document_reader.get_current_chapter_number()

    def chat(self, message: str) -> str:
        try:
            context = self._get_context()
            response = self._call_ai_model(context, message)
            self.conversation_history.append({"user": message, "ai": response})
            return response
        except Exception as e:
            return f"An error occurred in the chat method: {str(e)}"

    def _get_context(self) -> str:
        context = f"Current chapter: {self.document_reader.get_current_chapter_number()}\n"
        context += f"Word in chapter: {self.document_reader.get_current_word_index()}\n\n"
        context += self.context_manager.get_full_context()
        context += "\nRecent conversation:\n"
        for entry in self.conversation_history[-5:]:
            context += f"User: {entry['user']}\n{entry['ai']}\n\n"
        return context

    def save_conversation(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        book_name = os.path.basename(self.book_path)
        file_name = f"{book_name}_conversation.json"
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w') as f:
            json.dump({
                "conversation_history": self.conversation_history,
                "system_prompt": self.system_prompt,
                "additional_context": self.get_additional_context(),
                "ai_name": self.ai_name
            }, f)

    def load_conversation(self, directory: str) -> bool:
        book_name = os.path.basename(self.book_path)
        file_name = f"{book_name}_conversation.json"
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.conversation_history = data.get("conversation_history", [])
                self.system_prompt = data.get("system_prompt", self.system_prompt)
                for i, context in enumerate(data.get("additional_context", ["", "", ""])):
                    self.set_additional_context(i, context)
                self.ai_name = data.get("ai_name", "Assistant")
            return True
        return False

    def set_ai_persona(self, name: str, role: str):
        self.ai_name = name
        self.system_prompt = prepend_copyright_disclaimer(f"You are {name}, {role}.")
    
    def set_system_prompt(self, new_prompt: str):
        self.system_prompt = prepend_copyright_disclaimer(new_prompt)

    def get_current_chapter_content_up_to_word(self):
        return self.document_reader.get_current_chapter_content_up_to_word()

    def get_current_word_index(self):
        return self.document_reader.get_current_word_index()

    def move_to_next_chapter(self):
        if self.document_reader.move_to_next_chapter():
            self.current_word = sum(self.document_reader.chapters[i]['word_count'] for i in range(self.document_reader.current_chapter))
            self.context_manager.update_context(0)
            return True
        return False

    def move_to_previous_chapter(self):
        if self.document_reader.move_to_previous_chapter():
            self.current_word = sum(self.document_reader.chapters[i]['word_count'] for i in range(self.document_reader.current_chapter))
            self.context_manager.update_context(0)
            return True
        return False

    def get_current_chapter(self) -> int:
        return self.document_reader.get_current_chapter_number()

    def get_total_chapters(self) -> int:
        return self.document_reader.get_total_chapters()

    def get_navigation_unit(self) -> str:
        return self.document_reader.get_navigation_unit()

    def get_context_summary(self):
        return self.context_manager.get_dynamic_summary()

    def analyze_character(self, character_name, character_context):
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                temperature=0.7,
                system=prepend_copyright_disclaimer("You are an expert on character analysis."),
                messages=[
                    {"role": "user", "content": CHARACTER_ANALYSIS_PROMPT.format(
                        character_name=character_name,
                        character_context=character_context
                    )}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Error analyzing character: {str(e)}"

    def analyze_literary_elements(self, text):
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                temperature=0.7,
                system=prepend_copyright_disclaimer("You are a literary critic."),
                messages=[
                    {"role": "user", "content": LITERARY_ANALYSIS_PROMPT.format(
                        text_to_analyze=text
                    )}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Error analyzing literary elements: {str(e)}"