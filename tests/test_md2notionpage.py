
import unittest
from unittest.mock import patch, MagicMock, call
from md2notionpage import md2notionpage
from datetime import datetime

class TestMd2NotionPage(unittest.TestCase):

    def setUp(self):
        # Common setup for all tests
        self.parent_page_id = "test-parent-id"
        self.cover_url = "https://example.com/cover.jpg"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.title = f"Test Page {self.timestamp}"

    @patch('md2notionpage.core.notion')
    def test_create_complex_page_structure(self, mock_notion):
        """
        Test that a complex markdown document is correctly parsed and sent to Notion
        via the expected API calls (create -> update -> append children).
        """
        # Setup mock return values
        mock_page = {"id": "test-page-id", "url": "https://www.notion.so/test-page-url"}
        mock_notion.pages.create.return_value = mock_page
        mock_notion.pages.update.return_value = mock_page
        mock_notion.blocks.children.append.return_value = {}

        markdown_text = r"""
# Main Title

## Subtitle

- Item 1
- Item 2

1. Numbered 1
2. Numbered 2

> A quote

```python
print("Hello")
```

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |

![Image](https://example.com/image.png)
"""
        # Execute
        url = md2notionpage(markdown_text, self.title, self.parent_page_id, self.cover_url)

        # 1. Verify Page Creation
        mock_notion.pages.create.assert_called_once_with(
            parent={"type": "page_id", "page_id": self.parent_page_id},
            properties={},
            children=[]
        )

        # 2. Verify Page Update (Title & Cover)
        mock_notion.pages.update.assert_called_once()
        update_call_args = mock_notion.pages.update.call_args
        self.assertEqual(update_call_args[0][0], "test-page-id") # page_id
        self.assertEqual(
            update_call_args[1]['properties']['title']['title'][0]['text']['content'], 
            self.title
        )
        self.assertEqual(
            update_call_args[1]['cover']['external']['url'], 
            self.cover_url
        )

        # 3. Verify Content Appending
        # We expect at least one call to blocks.children.append
        self.assertTrue(mock_notion.blocks.children.append.called)
        
        # Inspect the blocks sent
        append_call_args = mock_notion.blocks.children.append.call_args
        self.assertEqual(append_call_args[0][0], "test-page-id") # page_id
        children = append_call_args[1]['children']
        
        # We expect specific block types in order
        expected_types = [
            'heading_1', 
            'heading_2', 
            'bulleted_list_item', 'bulleted_list_item',
            'numbered_list_item', 'numbered_list_item',
            'quote',
            'code',
            'equation', # Table is converted to equation/latex
            'image'
        ]
        
        # Extract types from the actual call
        actual_types = [
            block.get('type') or block.get('object') # fallback for safety
            for block in children
        ]
        
        # Check if all expected types are present (we might have extra paragraphs or dividers)
        for expected in expected_types:
            self.assertIn(expected, actual_types)

        # Specific check for content
        self.assertEqual(children[0]['heading_1']['rich_text'][0]['text']['content'], "Main Title")
        self.assertEqual(children[7]['code']['rich_text'][0]['text']['content'], 'print("Hello")')

        # 4. Verify Return Value
        self.assertEqual(url, "https://www.notion.so/test-page-url")

    @patch('md2notionpage.core.notion')
    def test_create_simple_page_no_cover(self, mock_notion):
        """
        Test creating a simple page without a cover image.
        """
        mock_page = {"id": "simple-page-id", "url": "https://notion.so/simple"}
        mock_notion.pages.create.return_value = mock_page
        
        markdown_text = "Just some simple text."
        
        # Execute with empty cover_url
        md2notionpage(markdown_text, "Simple Title", self.parent_page_id, "")

        # Verify update call does NOT include cover
        update_call_kwargs = mock_notion.pages.update.call_args[1]
        self.assertNotIn('cover', update_call_kwargs)
        self.assertEqual(
            update_call_kwargs['properties']['title']['title'][0]['text']['content'], 
            "Simple Title"
        )

    @patch('md2notionpage.core.notion')
    def test_batching_logic(self, mock_notion):
        """
        Test that large content is split into batches of 100 blocks.
        """
        mock_notion.pages.create.return_value = {"id": "batch-page-id", "url": "url"}
        
        # Generate 150 lines of text, which should result in 150 paragraph blocks
        markdown_text = "\n".join([f"Line {i}" for i in range(150)])
        
        md2notionpage(markdown_text, "Batch Test", self.parent_page_id)
        
        # Should be called twice: once for first 100, once for remaining 50
        self.assertEqual(mock_notion.blocks.children.append.call_count, 2)
        
        # Verify first batch size
        first_call = mock_notion.blocks.children.append.call_args_list[0]
        self.assertEqual(len(first_call[1]['children']), 100)
        
        # Verify second batch size
        second_call = mock_notion.blocks.children.append.call_args_list[1]
        self.assertEqual(len(second_call[1]['children']), 50)

if __name__ == '__main__':
    unittest.main()
