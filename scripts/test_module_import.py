#!/usr/bin/env python3
"""
Test script to verify the Python module import works correctly.
This demonstrates the programmatic usage of md2notionpage.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the module
from md2notionpage import md2notionpage

# Test markdown content
markdown_text = """
# My Test Page
This is a Notion page created from Markdown content using the Python module.

## Features tested:
- **Bold text**
- *Italic text*
- `Code inline`

### List example:
1. First item
2. Second item
3. Third item

> This is a blockquote

```python
def hello():
    print("Hello from code block!")
```
"""

title = f'Python Module Test'
parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')

if not parent_page_id:
    print("❌ Error: NOTION_PARENT_PAGE_ID not set in .env file")
    exit(1)

print(f"Creating page: {title}")
print(f"Parent page ID: {parent_page_id}")

try:
    notion_page_url = md2notionpage(markdown_text, title, parent_page_id)
    print(f"\n✅ Success! Page created at:\n{notion_page_url}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
