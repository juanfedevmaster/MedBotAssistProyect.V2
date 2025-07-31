# test_normalization.py

import unittest
from app.services.database_service import normalize_text_for_search

class TestTextNormalization(unittest.TestCase):
    def test_normalization_cases(self):
        test_cases = [
            ("Sánchez García", "sanchez garcia"),
            ("José María", "jose maria"),
            ("PÉREZ", "perez"),
            ("Ángel Rodríguez", "angel rodriguez"),
            ("María José Hernández", "maria jose hernandez"),
            ("GONZÁLEZ LÓPEZ", "gonzalez lopez"),
            ("   Extra   Space   ", "extra space"),
            ("Niño con ñ", "nino con n"),
            ("Multiple   spaces", "multiple spaces"),
            ("", "")
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                result = normalize_text_for_search(original)
                self.assertEqual(result, expected)

    def test_search_examples(self):
        examples = {
            "sanchez": "sanchez garcia",
            "jose maria": "jose maria rodriguez",
            "PEREZ": "perez lopez",
            "angel": "angel hernandez",
            "gonzalez": "gonzalez martinez"
        }

        for query, expected_target in examples.items():
            normalized_query = normalize_text_for_search(query)
            normalized_target = normalize_text_for_search(expected_target)
            with self.subTest(query=query):
                self.assertIn(normalized_query, normalized_target)

if __name__ == "__main__":
    unittest.main()
