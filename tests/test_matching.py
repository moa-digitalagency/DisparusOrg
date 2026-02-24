import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import algorithms.matching
from algorithms.matching import (
    text_similarity,
    description_similarity,
    compute_image_hash,
    compare_hashes,
    find_potential_matches
)

class TestMatching(unittest.TestCase):

    def setUp(self):
        algorithms.matching._HASH_CACHE.clear()

    def test_text_similarity(self):
        self.assertEqual(text_similarity("Paris", "Paris"), 1.0)
        self.assertGreater(text_similarity("Kalonji", "Kalonji "), 0.9)
        self.assertGreater(text_similarity("Kalonji", "kalonji"), 0.95)
        self.assertLess(text_similarity("Paris", "Londres"), 0.4)

    def test_description_similarity(self):
        d1 = "Homme shirt rouge"
        d2 = "Homme t-shirt rouge pantalon noir"
        score = description_similarity(d1, d2)
        self.assertGreater(score, 0.0)

        d3 = "Le chat est noir"
        d4 = "Un chat noir"
        self.assertAlmostEqual(description_similarity(d3, d4), 1.0)

    @patch('algorithms.matching.current_app', new_callable=MagicMock)
    @patch('algorithms.matching.Image.open')
    @patch('algorithms.matching.os.path.exists')
    def test_image_hashing(self, mock_exists, mock_open, mock_app):
        # Configure mock_app
        mock_app.root_path = "/app"

        mock_exists.return_value = True

        mock_img = MagicMock()
        mock_img.resize.return_value = mock_img
        mock_img.convert.return_value = mock_img
        pixels = [255]*9 + [0]*(72-9)
        mock_img.getdata.return_value = pixels

        mock_open.return_value.__enter__.return_value = mock_img

        hash1 = compute_image_hash("static/uploads/dummy.jpg")
        self.assertIsNotNone(hash1)
        self.assertEqual(len(hash1), 16)

        mock_open.assert_called()

    def test_compare_hashes(self):
        h1 = "ffff000000000000"
        h2 = "ffff000000000000"
        self.assertEqual(compare_hashes(h1, h2), 1.0)
        h3 = "0000000000000000"
        self.assertLess(compare_hashes(h1, h3), 0.8)

    @patch('algorithms.matching.Disparu')
    @patch('algorithms.matching.compute_image_hash')
    def test_find_potential_matches(self, mock_hash, MockDisparu):
        mock_query = MagicMock()
        MockDisparu.query.filter.return_value = mock_query

        d1 = MagicMock()
        d1.id = 1
        d1.first_name = "Jean"
        d1.last_name = "Dupont"
        d1.age = 30
        d1.country = "Congo"
        d1.city = "Kinshasa"
        d1.physical_description = "Grand noir"
        d1.photo_url = "photo1.jpg"
        d1.sex = "M"

        c1 = MagicMock()
        c1.id = 2
        c1.first_name = "Jean"
        c1.last_name = "Dupont"
        c1.age = 31
        c1.country = "Congo"
        c1.city = "Kinshasa"
        c1.physical_description = "Grand homme noir"
        c1.photo_url = "photo2.jpg"
        c1.sex = "M"
        c1.to_dict.return_value = {'id': 2, 'score': 0}

        mock_query.limit.return_value.all.return_value = [c1]

        def side_effect(path):
            if path == "photo1.jpg": return "ffffffffffffffff"
            if path == "photo2.jpg": return "ffffffffffffffff"
            return None
        mock_hash.side_effect = side_effect

        matches = find_potential_matches(d1)
        self.assertEqual(len(matches), 1)
        self.assertGreater(matches[0]['score'], 80)

if __name__ == '__main__':
    unittest.main()
