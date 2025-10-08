
# md2notionpage

A Python package to convert Markdown text into Notion Blocks pages. This module provides functionality to create Notion pages from Markdown text, parse Markdown into Notion blocks, and process inline formatting.

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
 Or calling the core function of convert markdown to notion blocks in your own function, and implement the logic of other notation operations yourself:
 ```python
from notion_client import Client as Notion
from md2notionpage import md2notion_parse_md

def create_page(title, industry, language, date_str, md_content=None):

	notion = Notion(auth=NOTION_API_KEY, notion_version=NOTION_VERSION) # Define your env parameters

	# is_latex_table = False means Markdown Table concerted to Notion Table instead of LaTeX Table
	children = md2notion_parse_md(md_content, is_latex_table=False) if md_content else []

	properties = {
		 "Name": {"title": [{"type": "text", "text": {"content": title}}]},
		 "Industry": {"rich_text": [{"type": "text", "text": {"content": industry}}]},
		 "Language": {"rich_text": [{"type": "text", "text": {"content": language}}]},
		 "Create Date": {"rich_text": [{"type": "text", "text": {"content": date_str + "UTC"}}]}
	} 
	resp = notion.pages.create(
	 	parent={"database_id": NOTION_DATABASE_ID},
	 	properties=properties,
	 	children=children
	)
```
# Supported Markdown Features

## Headings

You can create headings using the `#` symbol. The number of `#` symbols determines the level of the heading:

```
# Heading Level 1
## Heading Level 2
### Heading Level 3
```

## Text Formatting

- **Bold Text**: You can create bold text using `**` or `__`.
- *Italic Text*: You can create italic text using `*` or `_`.
- **_Bold and Italic_**: You can combine bold and italic using `__*` or `**_`.
- ~Strikethrough~: You can strikethrough text using `~`.
- Inline `Code`: You can create inline code using backticks `` ` ``.
- Inline Latex: You can create inline latex using `$`.

## Latex Block

You can create a Latex block using `$$`:

```
$$
x = \sqrt{y^2 + z^2}
$$
```

## Lists

- Unordered List: You can create an unordered list using `-`.
- Ordered List: You can create an ordered list using numbers followed by a dot `1.`.

## Links

You can create links using `[link text](url)`.

## Indented Code

You can create indented code using four spaces:

```
    def hello_world():
        print("Hello, world!")
```

## Code Block

You can create a code block using triple backticks:

	```python
	def hello_world2():
	    print("Hello, world2!")
	```

## Blockquote

You can create a blockquote using `>`:

```
> Quote text
```

## Tables

You can create tables with or without header rows. They will become LaTeX/KaTeX tables or Notion tables in the Notion page.
A switch parameter is_latex_table added to parse_md and create_notion_page_from_md functions in core.py. The default is_latex_table=True, and the original call is not affected.

### Table with Headers

```
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Content  | Content  | Content  |
```

### Table without Headers

```
| Content 1.1 | Content 2.1 | Content 3.1 |
| Content 1.2 | Content 2.2 | Content 3.2 |
```

## Horizontal Line

You can create a horizontal line using three or more dashes `---`.

## Images

You can insert images with or without alt text:

### With Alt Text:

```
![Alt Text](https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg)
```

Alt gives an image caption in Notion.

### Without Alt Text:

```
![](https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg)
```

## Nested Lists

You can create nested lists by indenting sub-items:

1. Item 1
   1. Sub-item 1
   2. Sub-item 2
      1. Sub-sub-item 1
      2. Sub-sub-item 2
2. Item 2

Similarly unordered lists are supported.

## Dependencies

- notion-client

## Environment Variables

You must set the `NOTION_SECRET` environment variable with your Notion API token.

## Notes

This package is designed to work with the Notion API and requires proper authentication. Make sure to follow Notion's API documentation to set up your integration.

## Development

1. Use .env to setup `NOTION_SECRET` and `NOTION_PARENT_PAGE_ID`
2. Run tests: `python -m unittest discover tests`
3. When tests are ok, commit changes

## Package control

Change to next version number in setup.py

1. Create wheels: `python setup.py sdist bdist_wheel`
2. Deploy: `python -m twine upload dist/*`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENCE) file for details.
