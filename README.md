
# md2notion

A Python package to convert Markdown text into Notion pages. This module provides functionality to create Notion pages from Markdown text, parse Markdown into Notion blocks, and process inline formatting.

## Installation

You can install the package using pip:

```bash
pip install md2notion
```

## Usage

Here's a basic example of how to use the `md2notion` function:

```python
from md2notion import md2notion
markdown_text = """
# My Page
This is a Notion page created from Markdown.
"""
title = 'My Notion Page'
parent_page_id = 'YOUR_PARENT_PAGE_ID'
notion_page_url = create_notion_page_from_md(markdown_text, title, parent_page_id)
```

## Dependencies

- notion-client
- mistune
- html2text

## Environment Variables

You must set the `NOTION_SECRET` environment variable with your Notion API token.

## Notes

This package is designed to work with the Notion API and requires proper authentication. Make sure to follow Notion's API documentation to set up your integration.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
