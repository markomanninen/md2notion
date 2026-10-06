
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
            'table', # Table is converted to native table
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

        # Check table properties and cells
        table_block = [b for b in children if b.get('type') == 'table'][0]
        self.assertEqual(table_block['table']['table_width'], 2)
        self.assertEqual(table_block['table']['has_column_header'], True)
        self.assertEqual(len(table_block['table']['children']), 2)

        header_row = table_block['table']['children'][0]['table_row']
        self.assertEqual(header_row['cells'][0][0]['text']['content'], "Header 1")
        self.assertEqual(header_row['cells'][1][0]['text']['content'], "Header 2")

        body_row = table_block['table']['children'][1]['table_row']
        self.assertEqual(body_row['cells'][0][0]['text']['content'], "Cell 1")
        self.assertEqual(body_row['cells'][1][0]['text']['content'], "Cell 2")

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
        
        # Generate 150 lines of text with double newlines, which should result in 150 paragraph blocks
        markdown_text = "\n\n".join([f"Line {i}" for i in range(150)])
        
        md2notionpage(markdown_text, "Batch Test", self.parent_page_id)
        
        # Should be called twice: once for first 100, once for remaining 50
        self.assertEqual(mock_notion.blocks.children.append.call_count, 2)
        
        # Verify first batch size
        first_call = mock_notion.blocks.children.append.call_args_list[0]
        self.assertEqual(len(first_call[1]['children']), 100)
        
        # Verify second batch size
        second_call = mock_notion.blocks.children.append.call_args_list[1]
        self.assertEqual(len(second_call[1]['children']), 50)

    @patch('md2notionpage.core.notion')
    def test_create_database_entry_with_auto_title_property(self, mock_notion):
        """
        Test creating a page as a database entry with default title property name.
        """
        mock_page = {"id": "db-entry-id", "url": "https://notion.so/db-entry"}
        mock_notion.pages.create.return_value = mock_page
        
        markdown_text = "# Database Entry Content\n\nSome content here."
        
        # Execute with parent_type='database' (uses default title_property_name='Name')
        url = md2notionpage(
            markdown_text, 
            "My Database Entry", 
            "test-database-id",
            parent_type='database'
        )
        
        # Verify page creation with correct title property
        create_call = mock_notion.pages.create.call_args
        self.assertEqual(create_call[1]['parent'], {"database_id": "test-database-id"})
        
        # Check that the title property uses the default "Name"
        properties = create_call[1]['properties']
        self.assertIn("Name", properties)
        self.assertEqual(
            properties["Name"]["title"][0]["text"]["content"], 
            "My Database Entry"
        )
        
        # Verify return value
        self.assertEqual(url, "https://notion.so/db-entry")

    @patch('md2notionpage.core.notion')
    def test_create_database_entry_with_custom_properties(self, mock_notion):
        """
        Test creating a database entry with custom properties provided.
        """
        mock_database_info = {
            "id": "test-database-id",
            "properties": {
                "Task": {"type": "title"},
                "Priority": {"type": "select"}
            }
        }
        mock_notion.databases.retrieve.return_value = mock_database_info
        
        mock_page = {"id": "custom-entry-id", "url": "https://notion.so/custom"}
        mock_notion.pages.create.return_value = mock_page
        
        # Custom properties including title
        custom_properties = {
            "Task": {"title": [{"text": {"content": "Complete project"}}]},
            "Priority": {"select": {"name": "High"}},
            "Due Date": {"date": {"start": "2026-12-31"}}
        }
        
        markdown_text = "Task details here."
        
        url = md2notionpage(
            markdown_text,
            "Ignored Title",  # Should be ignored when properties provided
            "test-database-id",
            parent_type='database',
            properties=custom_properties
        )
        
        # Verify custom properties were used
        create_call = mock_notion.pages.create.call_args
        self.assertEqual(create_call[1]['properties'], custom_properties)
        self.assertEqual(url, "https://notion.so/custom")

    @patch('md2notionpage.core.notion')
    def test_database_entry_creation_succeeds(self, mock_notion):
        """
        Test that database entry creation succeeds with default title property.
        """
        mock_page = {"id": "db-entry-id", "url": "https://notion.so/db-entry"}
        mock_notion.pages.create.return_value = mock_page
        
        markdown_text = "Test content"
        
        # Should succeed using default title_property_name='Name'
        url = md2notionpage(
            markdown_text,
            "Test Title",
            "test-db-id",
            parent_type='database'
        )
        
        # Verify the page was created
        self.assertEqual(url, "https://notion.so/db-entry")
        create_call = mock_notion.pages.create.call_args
        properties = create_call[1]['properties']
        self.assertIn("Name", properties)

    @patch('md2notionpage.core.notion')
    def test_invalid_parent_type_raises_error(self, mock_notion):
        """
        Test that an invalid parent_type raises a ValueError.
        """
        markdown_text = "Test content"
        
        with self.assertRaises(ValueError) as context:
            md2notionpage(
                markdown_text,
                "Test Title",
                "some-id",
                parent_type='invalid_type'
            )
        
        self.assertIn("Unrecognized parent_type", str(context.exception))
        self.assertIn("'invalid_type'", str(context.exception))

    @patch('md2notionpage.core.notion')
    @patch('md2notionpage.core.pprint.pprint')
    def test_print_page_info_flag(self, mock_pprint, mock_notion):
        """
        Test that print_page_info flag triggers page info printing.
        """
        mock_page = {"id": "page-id", "url": "https://notion.so/page"}
        mock_notion.pages.create.return_value = mock_page
        
        md2notionpage(
            "Content",
            "Title",
            "parent-id",
            print_page_info=True
        )
        
        # Verify pprint was called with page info
        mock_pprint.assert_called()
        self.assertEqual(mock_pprint.call_args[0][0], mock_page)

    @patch('md2notionpage.core.notion')
    def test_create_database_entry_with_custom_title_property_name(self, mock_notion):
        """
        Test creating a database entry with a custom title property name.
        """
        mock_notion.databases.retrieve.return_value = {"id": "test-db"}
        mock_page = {"id": "custom-title-entry-id", "url": "https://notion.so/custom-title"}
        mock_notion.pages.create.return_value = mock_page
        
        markdown_text = "Test content with custom title property."
        
        url = md2notionpage(
            markdown_text,
            "My Custom Entry",
            "test-db-id",
            parent_type='database',
            title_property_name='Task'  # Custom title property name
        )
        
        # Verify page creation with custom title property name
        create_call = mock_notion.pages.create.call_args
        properties = create_call[1]['properties']
        
        # Should use "Task" not "Name"
        self.assertIn("Task", properties)
        self.assertNotIn("Name", properties)
        self.assertEqual(
            properties["Task"]["title"][0]["text"]["content"],
            "My Custom Entry"
        )
        self.assertEqual(url, "https://notion.so/custom-title")

class TestTableToNotion(unittest.TestCase):
    """Tests for native Notion table conversion."""

    def _parse_table_md(self, markdown):
        from md2notionpage.core import NotionBlockConverter
        converter = NotionBlockConverter()
        blocks = converter.parse(markdown)
        table_blocks = [b for b in blocks if b.get('type') == 'table']
        self.assertEqual(len(table_blocks), 1, "Expected exactly one table block from table")
        return table_blocks[0]['table']

    def test_basic_table_conversion(self):
        md = (
            "| Header A | Header B |\n"
            "|----------|----------|\n"
            "| **Bold** | *Italic* |\n"
        )
        table = self._parse_table_md(md)
        self.assertEqual(table['table_width'], 2)
        self.assertEqual(table['has_column_header'], True)
        self.assertEqual(len(table['children']), 2)
        
        # Check header
        header_row = table['children'][0]['table_row']
        self.assertEqual(header_row['cells'][0][0]['text']['content'], "Header A")
        self.assertEqual(header_row['cells'][1][0]['text']['content'], "Header B")

        # Check cells with inline formatting
        body_row = table['children'][1]['table_row']
        self.assertEqual(body_row['cells'][0][0]['text']['content'], "Bold")
        self.assertTrue(body_row['cells'][0][0]['annotations']['bold'])
        self.assertEqual(body_row['cells'][1][0]['text']['content'], "Italic")
        self.assertTrue(body_row['cells'][1][0]['annotations']['italic'])

    def test_dollar_sign_in_cell_is_not_escaped(self):
        """Bare $ in a table cell does not need KaTeX escaping in native tables."""
        md = (
            "| Tool | MRR |\n"
            "|------|-----|\n"
            "| Copy to Notion | ~$100 MRR |\n"
        )
        table = self._parse_table_md(md)
        body_row = table['children'][1]['table_row']
        cell_tool = body_row['cells'][0][0]['text']['content']
        self.assertEqual(cell_tool, "Copy to Notion")
        
        cell_mrr = body_row['cells'][1][0]['text']['content']
        self.assertEqual(cell_mrr, "~$100 MRR")

    def test_footnote_reference_in_cell(self):
        """[^N] footnote refs do not break native tables and are preserved as text/rich text."""
        md = (
            "| Tool | Notes |\n"
            "|------|-------|\n"
            "| foo  | bar [^18] |\n"
        )
        table = self._parse_table_md(md)
        body_row = table['children'][1]['table_row']
        cell_notes_list = body_row['cells'][1]
        cell_notes = "".join(rt['text']['content'] for rt in cell_notes_list)
        self.assertEqual(cell_notes, "bar [^18]")

    def test_column_count_mismatch_alignment(self):
        """Table cells must be aligned to the declared column count (pad / truncate)."""
        from md2notionpage.core import NotionBlockConverter
        converter = NotionBlockConverter()
        
        # Manually craft a token with mismatched column counts
        token = {
            'type': 'table',
            'children': [
                {
                    'type': 'table_head',
                    'children': [
                        {'type': 'table_cell', 'children': [{'type': 'text', 'raw': 'A'}]},
                        {'type': 'table_cell', 'children': [{'type': 'text', 'raw': 'B'}]},
                        {'type': 'table_cell', 'children': [{'type': 'text', 'raw': 'C'}]}
                    ]
                },
                {
                    'type': 'table_body',
                    'children': [
                        {
                            'type': 'table_row',
                            'children': [
                                {'type': 'table_cell', 'children': [{'type': 'text', 'raw': '1'}]},
                                {'type': 'table_cell', 'children': [{'type': 'text', 'raw': '2'}]}
                            ]
                        },
                        {
                            'type': 'table_row',
                            'children': [
                                {'type': 'table_cell', 'children': [{'type': 'text', 'raw': '1'}]},
                                {'type': 'table_cell', 'children': [{'type': 'text', 'raw': '2'}]},
                                {'type': 'table_cell', 'children': [{'type': 'text', 'raw': '3'}]},
                                {'type': 'table_cell', 'children': [{'type': 'text', 'raw': '4'}]}
                            ]
                        }
                    ]
                }
            ]
        }
        
        block = converter.convert_table_token_to_notion(token)
        table = block['table']
        self.assertEqual(table['table_width'], 3)
        self.assertEqual(len(table['children']), 3) # 1 header row + 2 body rows
        
        row1 = table['children'][1]['table_row']
        self.assertEqual(len(row1['cells']), 3) # padded
        self.assertEqual(row1['cells'][2], []) # empty cell

        row2 = table['children'][2]['table_row']
        self.assertEqual(len(row2['cells']), 3) # truncated
        self.assertEqual(row2['cells'][2][0]['text']['content'], "3")


if __name__ == '__main__':
    unittest.main()
