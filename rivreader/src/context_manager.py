import importlib
from .prompts import DYNAMIC_SUMMARY_PROMPT

class ContextManager:
    def __init__(self, document_reader, api_key):
        self.document_reader = document_reader
        self.dynamic_summary = ""
        self.current_context = ""
        self.last_update_word = 0
        self.additional_context = ["", "", ""]
        self.anthropic_module = None
        self.client = None
        self.api_key = api_key
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

    def update_context(self, new_word_index):
        current_chapter = self.document_reader.get_current_chapter_number() - 1
        
        if new_word_index > self.last_update_word:
            new_content = ' '.join(self.document_reader.chapters[current_chapter]['words'][self.last_update_word:new_word_index])
            self.current_context += new_content
            self._update_dynamic_summary(new_content)
        else:
            self.current_context = self.document_reader.get_current_chapter_content_up_to_word()

        self.last_update_word = new_word_index

    def _update_dynamic_summary(self, new_content):
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=400,
                temperature=0.7,
                system="You are a helpful assistant that provides dynamic book summaries.",
                messages=[
                    {"role": "user", "content": DYNAMIC_SUMMARY_PROMPT.format(
                        previous_summary=self.dynamic_summary,
                        new_content=new_content
                    )}
                ]
            )
            self.dynamic_summary = response.content[0].text.strip()
        except Exception as e:
            print(f"Error updating dynamic summary: {str(e)}")

    def get_full_context(self):
        context = ""
        
        # Add dynamic summary
        context += f"Book Summary:\n{self.dynamic_summary}\n\n"
        
        # Add additional context
        for i, add_context in enumerate(self.additional_context, 1):
            if add_context:
                context += f"Additional Context {i}:\n{add_context}\n\n"
        
        # Add current chapter context
        context += f"Current chapter content:\n{self.current_context}"
        return context

    def _init_client(self):
        if self.client is None:
            if self.anthropic_module is None:
                self.anthropic_module = importlib.import_module('anthropic')
            self.client = self.anthropic_module.Anthropic(api_key=self.api_key)

    def get_current_chapter_summary(self):
        # This method now returns the dynamic summary instead of a chapter-specific summary
        return self.get_dynamic_summary()

    def get_dynamic_summary(self):
        return self.dynamic_summary

    def reset_context_for_new_chapter(self):
        self.current_context = ""
        self.last_update_word = 0

    def set_additional_context(self, index, content):
        if 0 <= index < 3:
            self.additional_context[index] = content
        else:
            raise ValueError("Additional context index must be 0, 1, or 2")

    def get_additional_context(self):
        return self.additional_context