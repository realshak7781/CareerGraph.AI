import unittest
from unittest.mock import patch, MagicMock
from services.pdf_parser import extract_text_from_pdf

class TestPdfParser(unittest.TestCase):
    @patch('services.pdf_parser.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        # Create mock pages
        mock_page_1 = MagicMock()
        mock_page_1.extract_text.return_value = "Page 1 text."
        mock_page_2 = MagicMock()
        mock_page_2.extract_text.return_value = "Page 2 text."
        
        # Setup mock reader instance
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page_1, mock_page_2]
        mock_pdf_reader.return_value = mock_reader_instance
        
        result = extract_text_from_pdf(b"dummy pdf bytes")
        
        self.assertIn("Page 1 text.", result)
        self.assertIn("Page 2 text.", result)
        self.assertEqual(result, "Page 1 text.\nPage 2 text.")

if __name__ == '__main__':
    unittest.main()
