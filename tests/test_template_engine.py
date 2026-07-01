import unittest
import os
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.template_engine import substitute_variables, _get_author


class TestSubstituteVariables(unittest.TestCase):
    def test_project_name_substituted(self):
        result = substitute_variables("Hello {{project_name}}", "/some/path/my-cool-app")
        self.assertEqual(result, "Hello my-cool-app")

    def test_year_substituted(self):
        result = substitute_variables("Copyright {{year}}", "/tmp/proj")
        self.assertIn(str(datetime.now().year), result)

    def test_date_substituted(self):
        result = substitute_variables("Created on {{date}}", "/tmp/proj")
        self.assertIn(datetime.now().strftime("%Y-%m-%d"), result)

    def test_author_substituted(self):
        result = substitute_variables("By {{author}}", "/tmp/proj")
        # Author should be a non-empty string (either git name or OS user)
        self.assertNotIn("{{author}}", result)
        self.assertTrue(len(result) > len("By "))

    def test_multiple_placeholders(self):
        template = "# {{project_name}}\nBy {{author}} - {{year}}"
        result = substitute_variables(template, "/home/user/my-project")
        self.assertIn("my-project", result)
        self.assertIn(str(datetime.now().year), result)
        self.assertNotIn("{{author}}", result)

    def test_no_placeholders(self):
        content = "This is plain text with no placeholders."
        result = substitute_variables(content, "/tmp/proj")
        self.assertEqual(result, content)

    def test_empty_string(self):
        result = substitute_variables("", "/tmp/proj")
        self.assertEqual(result, "")


class TestGetAuthor(unittest.TestCase):
    def test_returns_string(self):
        author = _get_author()
        self.assertIsInstance(author, str)
        self.assertTrue(len(author) > 0)


if __name__ == '__main__':
    unittest.main()
