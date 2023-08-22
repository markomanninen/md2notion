
# md2notionpage

A Python package to convert Markdown text into Notion pages. This module provides functionality to create Notion pages from Markdown text, parse Markdown into Notion blocks, and process inline formatting.

## Installation

You can install the package using pip:

```bash
pip install md2notionpage
```

## Usage

Here's a basic example of how to use the `md2notionpage` function:

```python
from md2notionpage import md2notionpage

markdown_text = """
# My Page
This is a Notion page created from Markdown content.
"""

title = 'My Notion Page'

parent_page_id = 'YOUR_PARENT_PAGE_ID'

notion_page_url = md2notionpage(markdown_text, title, parent_page_id)
```

## Dependencies

- notion-client

## Environment Variables

You must set the `NOTION_SECRET` environment variable with your Notion API token.

## Notes

This package is designed to work with the Notion API and requires proper authentication. Make sure to follow Notion's API documentation to set up your integration.

## Development

1. Use .env to setup `NOTION_SECRET`
2. Change `parent_page_id` to your Notion page in the text file
3. Run tests: `python -m unittest discover tests`
4. Commit changes

## Package control

Change to next version numer in setup.py

1. Create wheels: `python setup.py sdist bdist_wheel`
2. Deploy: `python -m twine upload dist/*`

## License

This project is licensed under the MIT License. See the LICENSE file for details.
