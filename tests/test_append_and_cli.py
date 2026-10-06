import unittest
from unittest.mock import patch, MagicMock
from md2notionpage.core import append_md_to_notion_block
from md2notionpage.cli import main
import os
import sys

class TestAppendAndCLI(unittest.TestCase):

    @patch('md2notionpage.core.notion')
    def test_append_md_to_notion_block_basic(self, mock_notion):
        """Test the basic behavior of appending Markdown to an existing block."""
        markdown_text = "This is a simple text.\n\nAnother paragraph."
        
        result_url = append_md_to_notion_block(markdown_text, "target-block-id", print_page_info=False)
        
        self.assertTrue(mock_notion.blocks.children.append.called)
        append_kwargs = mock_notion.blocks.children.append.call_args[1]
        self.assertEqual(mock_notion.blocks.children.append.call_args[0][0], "target-block-id")
        
        children = append_kwargs['children']
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0]['type'], 'paragraph')
        self.assertEqual(children[1]['type'], 'paragraph')
        self.assertEqual(result_url, "https://notion.so/target-block-id")

    @patch('md2notionpage.core.notion')
    def test_append_md_to_notion_block_split_and_batch(self, mock_notion):
        """Test that appending splits large blocks and batches API calls for >100 blocks."""
        # A long text exceeding 2000 chars should be split into multiple paragraph blocks
        long_paragraph = "A" * 2500
        # Create 150 simple paragraphs to trigger batching (> 100 blocks)
        many_paragraphs = "\n\n".join(f"Line {i}" for i in range(150))
        
        markdown_text = f"{long_paragraph}\n\n{many_paragraphs}"
        
        append_md_to_notion_block(markdown_text, "target-block-id")
        
        # 1 long paragraph (splits into 2 chunks) + 150 paragraphs = 152 blocks
        # Should be batched into two calls: 100 and 52 blocks
        self.assertEqual(mock_notion.blocks.children.append.call_count, 2)
        
        first_call = mock_notion.blocks.children.append.call_args_list[0]
        self.assertEqual(len(first_call[1]['children']), 100)
        self.assertEqual(first_call[0][0], "target-block-id")
        
        second_call = mock_notion.blocks.children.append.call_args_list[1]
        self.assertEqual(len(second_call[1]['children']), 52)
        self.assertEqual(second_call[0][0], "target-block-id")

    @patch('md2notionpage.cli.md2notionpage')
    @patch('md2notionpage.cli.append_md_to_notion_block')
    def test_cli_append_branch(self, mock_append, mock_md2notionpage):
        """Test that the CLI correctly triggers the append branch when a block URL is provided."""
        import tempfile
        import os
        
        mock_append.return_value = "https://notion.so/block_link"
        target_uuid = "12345678123456781234567812345678"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write("cli test")
            tmp_path = tmp_file.name
            
        try:
            test_args = ["md2notionpage", tmp_path, f"https://notion.so/my-page-11111111111111111111111111111111#{target_uuid}"]
            
            with patch('sys.argv', test_args):
                with patch('builtins.print') as mock_print:
                    main()
                    
            mock_append.assert_called_once_with("cli test", target_uuid, print_page_info=False)
            mock_md2notionpage.assert_not_called()
            mock_print.assert_any_call("Markdown content appended to Notion block: https://notion.so/block_link")
        finally:
            os.remove(tmp_path)

if __name__ == '__main__':
    unittest.main()
