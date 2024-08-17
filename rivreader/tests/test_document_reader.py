import unittest
import tempfile
import os
from src.document_reader import DocumentReader

class TestDocumentReader(unittest.TestCase):

    def setUp(self):
        # Create temporary PDF and ePub files for testing
        self.pdf_content = b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\ntrailer<</Root 1 0 R>>"
        self.epub_content = b'PK\x03\x04\x14\x00\x00\x00\x00\x00!kWJ\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00mimetype\xed\xbd\x07`\x1c\xc9u%&\x80\x01(\x80@\x80 \xc1\x00d\xc1\x88\x00A\x82 A\x92\x00A\x10$\x08\x92hPh4\x1a\xcd\xf6\xcc\xf4\x98\xd3\xcc\xec\xce\xec\xce\xee\xbc}\xfb\xde\xee\xbc\xdd\xf7\xde\xfb\x90\xac\xef\xbf?\x7f\xfe\'E\xaa$\xcb\xb2ly\x8d\x7f\xaf\xdf\xef\xdf\x7f\xf5\xaa\xba\xab\xab+\xab221\x91\x19\x99U]\x9d\x95\x95\x95\x95\x91\x99\x95\xe7\xf1&\xd3n\xdb\xfb\xbf\xfe\xa7\xcd\xc0\xe9\xd9\x16\x0c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        self.pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        self.pdf_file.write(self.pdf_content)
        self.pdf_file.close()
        
        self.epub_file = tempfile.NamedTemporaryFile(delete=False, suffix='.epub')
        self.epub_file.write(self.epub_content)
        self.epub_file.close()

    def tearDown(self):
        os.unlink(self.pdf_file.name)
        os.unlink(self.epub_file.name)

    def test_init_pdf(self):
        reader = DocumentReader(self.pdf_file.name)
        self.assertEqual(reader.file_type, 'pdf')

    def test_init_epub(self):
        reader = DocumentReader(self.epub_file.name)
        self.assertEqual(reader.file_type, 'epub')

    def test_init_unsupported_file(self):
        with self.assertRaises(ValueError):
            DocumentReader('unsupported.txt')

    def test_init_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            DocumentReader('nonexistent.pdf')

    def test_extract_text(self):
        reader = DocumentReader(self.pdf_file.name)
        with self.assertRaises(ValueError):
            reader.extract_text(-1, 1)
        with self.assertRaises(ValueError):
            reader.extract_text(0, 100)
        with self.assertRaises(ValueError):
            reader.extract_text(2, 1)

    def test_set_position(self):
        reader = DocumentReader(self.pdf_file.name)
        reader.set_position(0)
        self.assertEqual(reader.get_current_position(), 0)
        with self.assertRaises(ValueError):
            reader.set_position(-1)
        with self.assertRaises(ValueError):
            reader.set_position(100)

    def test_navigation(self):
        reader = DocumentReader(self.pdf_file.name)
        reader.move_to_next_section()
        self.assertEqual(reader.get_current_position(), 1)
        reader.move_to_previous_section()
        self.assertEqual(reader.get_current_position(), 0)
        with self.assertRaises(ValueError):
            reader.move_to_previous_section()

if __name__ == '__main__':
    unittest.main()