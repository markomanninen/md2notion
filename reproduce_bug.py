from md2notionpage.core import parse_markdown_to_notion_blocks
import json

markdown_OK = """# Otsikko 1
- Ensimmäinen kohta
buggy
 - Alaluettelo
"""

markdown_buggy = """# Otsikko 1
- Ensimmäinen kohta
buggy
 - Alaluettelo
"""

try:
    blocks = parse_markdown_to_notion_blocks(markdown_buggy)
    print(json.dumps(blocks, indent=2))
except Exception as e:
    print(f"An error occurred: {repr(e)}")
