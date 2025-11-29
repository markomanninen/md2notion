
# md2notionpage

A Python package to convert Markdown text into Notion pages. This module provides functionality to create Notion pages from Markdown text, parse Markdown into Notion blocks, and process inline formatting.

## Features

- Rich Markdown support - Headers, lists, code blocks, tables, images, and more
- Smart text splitting - Automatically handles Notion's 2000-character limit
- Batch processing - Efficiently handles large documents with 100+ blocks
- Cover images - Optional cover image support
- CLI & Python API - Use as a command-line tool or import as a module
- Helpful error messages - Clear guidance for common issues


## Installation

```bash
pip install md2notionpage
```

For development:

```bash
git clone https://github.com/markomanninen/md2notion.git
cd md2notion
pip install -e .
```

## Setup

### 1. Create a Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Give it a name and select the workspace
4. Copy the "Internal Integration Token"

### 2. Get Your Parent Page ID

1. Open the page in Notion where you want to create sub-pages
2. Click "Share" → "Copy link"
3. Extract the 32-character ID from the URL
   - Example: `https://notion.so/My-Page-abc123def456...`
   - Page ID: `abc123def456...`

### 3. Grant Integration Access

**Important**: You must grant your integration access to the parent page:

1. Open the parent page in Notion
2. Click "..." (more options) → "Add connections"
3. Select your integration from the list

Without this step, you'll get "restricted_resource" errors!

### 4. Configure Environment Variables

Create a `.env` file in your project directory:

```bash
NOTION_SECRET=your_notion_integration_token_here
NOTION_PARENT_PAGE_ID=your_target_parent_page_id_here
```

## Usage

### Command Line Interface

```bash
# Basic usage
md2notionpage example.md

# With custom title
md2notionpage example.md --title "My Custom Title"

# With cover image
md2notionpage example.md --cover_url "https://images.unsplash.com/photo-123..."

# Specify parent page ID directly
md2notionpage example.md parent-page-id-here
```

### Python Module

```python
from md2notionpage import md2notionpage

markdown_text = """
# My Page
This is a Notion page created from Markdown content.

## Features
- **Bold text**
- *Italic text*
- `Code inline`
"""

title = 'My Notion Page'
parent_page_id = 'YOUR_PARENT_PAGE_ID'

# Create page
notion_page_url = md2notionpage(markdown_text, title, parent_page_id)
print(f"Page created: {notion_page_url}")

# With cover image
notion_page_url = md2notionpage(
    markdown_text, 
    title, 
    parent_page_id,
    cover_url="https://images.unsplash.com/photo-123..."
)
```

## Supported Markdown Features

### Headings

```markdown
# Heading Level 1
## Heading Level 2
### Heading Level 3
```

### Text Formatting

- **Bold Text**: `**bold**` or `__bold__`
- *Italic Text*: `*italic*` or `_italic_`
- **_Bold and Italic_**: `__*text*__` or `**_text_**`
- ~Strikethrough~: `~text~`
- Inline `Code`: `` `code` ``
- Inline LaTeX: `$x = y^2$`

### LaTeX Blocks

```markdown
$$
x = \sqrt{y^2 + z^2}
$$
```

### Lists

**Unordered:**
```markdown
- Item 1
- Item 2
  - Nested item
```

**Ordered:**
```markdown
1. First item
2. Second item
   1. Nested item
```

### Links

```markdown
[Link text](https://example.com)
```

### Code Blocks

````markdown
```python
def hello_world():
    print("Hello, world!")
```
````

### Blockquotes

```markdown
> This is a quote
```

### Tables

**With headers:**
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Content  | Content  | Content  |
```

**Without headers:**
```markdown
| Content 1.1 | Content 2.1 | Content 3.1 |
| Content 1.2 | Content 2.2 | Content 3.2 |
```

Tables are rendered as LaTeX/KaTeX in Notion.

### Horizontal Lines

```markdown
---
```

### Images

**With caption:**
```markdown
![Alt Text](https://example.com/image.jpg)
```

**Without caption:**
```markdown
![](https://example.com/image.jpg)
```

## Error Handling

The tool provides helpful error messages for common issues:

- Invalid API token - Instructions for creating an integration
- Invalid parent page ID - How to find the correct page ID
- Page not found - Verification steps
- Access denied - How to grant integration access
- Invalid cover URL - Cover image requirements


## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e .[dev]

# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_md2notionpage.py -v
```

### Stress Testing

Test the splitting and batching logic with large documents:

```bash
python scripts/stress_test.py
```

This creates a page with:
- 3000+ character paragraph (tests text splitting)
- 150 list items (tests batch processing)

## Publishing

1. Update version in `pyproject.toml`
2. Build the package:
   ```bash
   python -m build
   ```
3. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

## Dependencies

- `notion-client` - Official Notion API client
- `python-dotenv` - Environment variable management

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with the [Notion API](https://developers.notion.com/)
- Inspired by the need for easy Markdown-to-Notion conversion
