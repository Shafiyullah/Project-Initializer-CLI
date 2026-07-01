import unittest
import os
import sys
import logging

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import get_package_manager, is_admin, ColorFormatter

class TestUtils(unittest.TestCase):
    def test_get_package_manager(self):
        # This test depends on the system running it, but we can check it returns a string or None
        pm = get_package_manager()
        if pm:
            self.assertIsInstance(pm, str)
        else:
            self.assertIsNone(pm)

    def test_is_admin(self):
        # Check that it returns a boolean
        admin = is_admin()
        self.assertIsInstance(admin, bool)

    def test_color_formatter(self):
        formatter = ColorFormatter()
        
        # Test INFO message formatting (should be just the clean message)
        info_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="hello %s",
            args=("world",),
            exc_info=None
        )
        self.assertEqual(formatter.format(info_record), "hello world")

        # Test WARNING message formatting (should include yellow warning tags)
        warn_record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=10,
            msg="warning message",
            args=(),
            exc_info=None
        )
        formatted_warn = formatter.format(warn_record)
        self.assertTrue(formatted_warn.startswith(ColorFormatter.YELLOW))
        self.assertTrue(formatted_warn.endswith(ColorFormatter.RESET))
        self.assertIn("WARNING: warning message", formatted_warn)

if __name__ == '__main__':
    unittest.main()
