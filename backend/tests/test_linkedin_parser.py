import unittest
import zipfile
import io
import csv
from services.linkedin_parser import parse_linkedin_zip

class TestLinkedinParser(unittest.TestCase):
    def setUp(self):
        # Create an in-memory ZIP file with Connections.csv and Positions.csv
        self.zip_buffer = io.BytesIO()
        with zipfile.ZipFile(self.zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Connections.csv
            conn_csv = io.StringIO()
            conn_writer = csv.writer(conn_csv)
            conn_writer.writerow(["First Name", "Last Name", "Email Address", "Company", "Position", "Connected On"])
            conn_writer.writerow(["John", "Doe", "john@example.com", "TechCorp", "Engineer", "01 Jan 2020"])
            zf.writestr("Connections.csv", conn_csv.getvalue().encode('utf-8'))
            
            # Positions.csv
            pos_csv = io.StringIO()
            pos_writer = csv.writer(pos_csv)
            pos_writer.writerow(["Company Name", "Title", "Description", "Location", "Started On", "Finished On"])
            pos_writer.writerow(["TechCorp", "Senior Engineer", "Did stuff", "Remote", "Jan 2020", "Present"])
            zf.writestr("Positions.csv", pos_csv.getvalue().encode('utf-8'))
            
        self.zip_bytes = self.zip_buffer.getvalue()

    def test_parse_linkedin_zip_success(self):
        result = parse_linkedin_zip(self.zip_bytes)
        
        # Check connections
        self.assertIn("connections", result)
        self.assertEqual(len(result["connections"]), 1)
        self.assertEqual(result["connections"][0]["First Name"], "John")
        self.assertEqual(result["connections"][0]["Company"], "TechCorp")
        
        # Check positions
        self.assertIn("positions", result)
        self.assertEqual(len(result["positions"]), 1)
        self.assertEqual(result["positions"][0]["Title"], "Senior Engineer")
        self.assertEqual(result["positions"][0]["Company Name"], "TechCorp")

    def test_parse_linkedin_zip_missing_files(self):
        # Create a ZIP with only Connections.csv
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Connections.csv", b"First Name,Last Name\nJane,Doe")
            
        result = parse_linkedin_zip(zip_buffer.getvalue())
        self.assertEqual(len(result["connections"]), 1)
        self.assertEqual(len(result["positions"]), 0)

    def test_parse_real_linkedin_zip_in_memory(self):
        import os
        real_zip_path = os.path.join(os.path.dirname(__file__), "..", "..", "zip_data", "linkedin zip data for sharique.zip")
        if os.path.exists(real_zip_path):
            with open(real_zip_path, 'rb') as f:
                zip_bytes = f.read()
            
            result = parse_linkedin_zip(zip_bytes)
            self.assertIn("connections", result)
            self.assertIn("positions", result)
            # The exact number of connections/positions depends on the real data,
            # but we can assert it parsed without throwing an error and returns a dict.
            self.assertIsInstance(result["connections"], list)
            self.assertIsInstance(result["positions"], list)
        else:
            self.skipTest(f"Real zip data not found at {real_zip_path}")

if __name__ == '__main__':
    unittest.main()
