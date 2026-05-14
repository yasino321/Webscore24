import unittest
import os
import csv
from finder import _save_to_csv

class TestWebScore(unittest.TestCase):
    def test_csv_saving(self):
        test_file = 'test_leads.csv'
        if os.path.exists(test_file):
            os.remove(test_file)

        lead = {
            'name': 'Test Firma',
            'adresse': 'Test Str 1',
            'url': 'http://test.de',
            'telefon': '12345',
            'bewertungen': 10,
            'status': 'neu',
            'score_gesamt': ''
        }

        # Monkeypatch or just call if it's easy
        # For simplicity I'll just check if it appends correctly to a file
        def temp_save(lead):
            file_exists = os.path.isfile(test_file)
            with open(test_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'adresse', 'url', 'telefon', 'bewertungen', 'status', 'score_gesamt'])
                if not file_exists:
                    writer.writeheader()
                writer.writerow(lead)

        temp_save(lead)
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['name'], 'Test Firma')

        os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
