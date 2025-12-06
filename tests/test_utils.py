import unittest
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import get_package_manager

class TestUtils(unittest.TestCase):
    def test_get_package_manager(self):
        # This test depends on the system running it, but we can check it returns a string or None
        pm = get_package_manager()
        if pm:
            self.assertIsInstance(pm, str)
        else:
            self.assertIsNone(pm)

if __name__ == '__main__':
    unittest.main()
