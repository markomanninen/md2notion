import unittest
from md2notionpage.core import parse_markdown_to_notion_blocks


class TestListParsing(unittest.TestCase):
    """Test cases for list parsing, specifically for the KeyError fix."""

    def test_bulleted_list_after_numbered_list(self):
        """Test that a bulleted list item after a numbered list doesn't raise KeyError."""
        md_text = '''1. First numbered item
 - Bulleted item as nested'''
        
        result = parse_markdown_to_notion_blocks(md_text)
        # Should not raise KeyError
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'numbered_list_item')
        self.assertEqual(result[1]['type'], 'bulleted_list_item')

    def test_numbered_list_after_bulleted_list(self):
        """Test that a numbered list item after a bulleted list doesn't raise KeyError."""
        md_text = '''- First bulleted item
 1. Numbered item as nested'''
        
        result = parse_markdown_to_notion_blocks(md_text)
        # Should not raise KeyError
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'bulleted_list_item')
        self.assertEqual(result[1]['type'], 'numbered_list_item')

    def test_indented_bulleted_list_after_paragraph(self):
        """Test that an indented bulleted list after a paragraph doesn't raise KeyError."""
        md_text = '''This is a paragraph
 - Indented bulleted item'''
        
        result = parse_markdown_to_notion_blocks(md_text)
        # Should not raise KeyError
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'paragraph')
        self.assertEqual(result[1]['type'], 'bulleted_list_item')

    def test_indented_numbered_list_after_paragraph(self):
        """Test that an indented numbered list after a paragraph doesn't raise KeyError."""
        md_text = '''This is a paragraph
 1. Indented numbered item'''
        
        result = parse_markdown_to_notion_blocks(md_text)
        # Should not raise KeyError
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'paragraph')
        self.assertEqual(result[1]['type'], 'numbered_list_item')

    def test_nested_bulleted_lists(self):
        """Test that properly nested bulleted lists still work correctly."""
        md_text = '''- First item
 - Nested item
 - Another nested item
- Second item'''
        
        result = parse_markdown_to_notion_blocks(md_text)
        self.assertIsNotNone(result)
        # Should have proper nesting
        self.assertEqual(result[0]['type'], 'bulleted_list_item')
        self.assertIn('children', result[0]['bulleted_list_item'])
        self.assertEqual(len(result[0]['bulleted_list_item']['children']), 2)

    def test_nested_numbered_lists(self):
        """Test that properly nested numbered lists still work correctly."""
        md_text = '''1. First item
 1. Nested item
 2. Another nested item
2. Second item'''
        
        result = parse_markdown_to_notion_blocks(md_text)
        self.assertIsNotNone(result)
        # Should have proper nesting
        self.assertEqual(result[0]['type'], 'numbered_list_item')
        self.assertIn('children', result[0]['numbered_list_item'])
        self.assertEqual(len(result[0]['numbered_list_item']['children']), 2)


if __name__ == '__main__':
    unittest.main()
