import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from docx import Document
from striprtf.striprtf import rtf_to_text
import html2text
import PyPDF2

class DocumentReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_type = self._get_file_type()
        self.chapters = []
        self.current_chapter = 0
        self.current_word = 0
        self.pdf_reader = None
        self.is_pdf = self.file_type == '.pdf'
        self._process_file()

    def _get_file_type(self):
        _, ext = os.path.splitext(self.file_path)
        return ext.lower()

    def _process_file(self):
        try:
            if self.file_type == '.epub':
                self._process_epub()
            elif self.file_type == '.txt':
                self._process_txt()
            elif self.file_type == '.docx':
                self._process_docx()
            elif self.file_type == '.rtf':
                self._process_rtf()
            elif self.file_type == '.html':
                self._process_html()
            elif self.file_type == '.pdf':
                self._process_pdf()
            else:
                raise ValueError(f"Unsupported file type: {self.file_type}")
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise
    
    def _process_pdf(self):
        try:
            with open(self.file_path, 'rb') as file:
                self.pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(self.pdf_reader.pages)):
                    content = self.pdf_reader.pages[page_num].extract_text()
                    words = content.split()
                    self.chapters.append({
                        'text': content,
                        'words': words,
                        'word_count': len(words)
                    })
        except PyPDF2.errors.PdfReadError as e:
            print(f"Error reading PDF file: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error processing PDF file: {str(e)}")
            raise

    def move_to_next_chapter(self):
        if self.current_chapter < len(self.chapters) - 1:
            self.current_chapter += 1
            self.current_word = 0
            return True
        return False

    def move_to_previous_chapter(self):
        if self.current_chapter > 0:
            self.current_chapter -= 1
            self.current_word = 0
            return True
        return False

    def get_current_chapter_number(self):
        return self.current_chapter + 1

    def get_total_chapters(self):
        return len(self.chapters)

    def get_navigation_unit(self):
        return "Page" if self.is_pdf else "Chapter"

    def _process_epub(self):
        try:
            book = epub.read_epub(self.file_path)
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                chapter_text = soup.get_text()
                words = chapter_text.split()
                self.chapters.append({
                    'text': chapter_text,
                    'words': words,
                    'word_count': len(words)
                })
        except ebooklib.epub.EpubException as e:
            print(f"Error processing EPUB file: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error processing EPUB file: {str(e)}")
            raise

    def _process_txt(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self._split_into_chapters(content)
        except UnicodeDecodeError:
            print("Error: Unable to decode the text file. It might be encoded in a different format.")
            raise
        except IOError as e:
            print(f"Error reading text file: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error processing text file: {str(e)}")
            raise

    def _process_docx(self):
        try:
            doc = Document(self.file_path)
            content = '\n'.join([para.text for para in doc.paragraphs])
            self._split_into_chapters(content)
        except IOError as e:
            print(f"Error reading DOCX file: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error processing DOCX file: {str(e)}")
            raise

    def _process_rtf(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = rtf_to_text(file.read())
            self._split_into_chapters(content)
        except UnicodeDecodeError:
            print("Error: Unable to decode the RTF file. It might be encoded in a different format.")
            raise
        except IOError as e:
            print(f"Error reading RTF file: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error processing RTF file: {str(e)}")
            raise

    def _process_html(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = html2text.html2text(file.read())
            self._split_into_chapters(content)
        except UnicodeDecodeError:
            print("Error: Unable to decode the HTML file. It might be encoded in a different format.")
            raise
        except IOError as e:
            print(f"Error reading HTML file: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error processing HTML file: {str(e)}")
            raise

    def _split_into_chapters(self, content):
        try:
            words = content.split()
            chapter_size = 1000
            for i in range(0, len(words), chapter_size):
                chapter_words = words[i:i+chapter_size]
                chapter_text = ' '.join(chapter_words)
                self.chapters.append({
                    'text': chapter_text,
                    'words': chapter_words,
                    'word_count': len(chapter_words)
                })
        except Exception as e:
            print(f"Error splitting content into chapters: {str(e)}")
            raise

    def get_current_chapter_content_up_to_word(self):
        try:
            words = self.chapters[self.current_chapter]['words']
            return ' '.join(words[:self.current_word])
        except IndexError:
            print("Error: Invalid chapter or word index.")
            return ""

    def get_current_chapter_text(self):
        try:
            return self.chapters[self.current_chapter]['text']
        except IndexError:
            print("Error: Invalid chapter index.")
            return ""

    def get_current_chapter_number(self):
        return self.current_chapter + 1  # Assuming current_chapter is 0-indexed

    def get_current_word_index(self):
        return self.current_word

    def move_to_next_chapter(self):
        if self.current_chapter < len(self.chapters) - 1:
            self.current_chapter += 1
            self.current_word = 0
            return True
        return False

    def move_to_previous_chapter(self):
        if self.current_chapter > 0:
            self.current_chapter -= 1
            self.current_word = 0
            return True
        return False
    
    def move_to_chapter(self, chapter_number: int) -> bool:
        if 0 <= chapter_number < len(self.chapters):
            self.current_chapter = chapter_number
            self.current_word = 0
            return True
        return False

    def update_current_word(self, word_index: int) -> bool:
        if 0 <= word_index < self.chapters[self.current_chapter]['word_count']:
            self.current_word = word_index
            return True
        return False

    def get_total_chapters(self):
        return len(self.chapters)

    def get_word_index_from_coordinates(self, line: int, char: int) -> int:
        try:
            content = self.get_current_chapter_text()
            lines = content.split('\n')
            word_index = sum(len(l.split()) for l in lines[:line])
            word_index += len(lines[line][:char].split())
            return word_index
        except IndexError:
            print("Error: Invalid line or character index.")
            return 0
        except Exception as e:
            print(f"Unexpected error in get_word_index_from_coordinates: {str(e)}")
            return 0