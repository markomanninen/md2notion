"""
core.py

This module provides functionality to convert Markdown text into Notion pages. It includes functions to create a Notion page from Markdown text, parse Markdown into Notion blocks, and process inline formatting for bold and italic text.

Functions:
    - create_notion_page_from_md(markdown_text, title, parent_page_id, cover_url): Create a Notion page from Markdown text.
    - parse_md(markdown_text): Parse Markdown text and convert it into Notion blocks.
    - parse_markdown_to_notion_blocks(markdown): Parse Markdown text and convert it into a list of Notion blocks.
    - process_inline_formatting(text): Process inline formatting in Markdown text and convert it to Notion rich text formatting.

Dependencies:
    - notion_client: Client library for interacting with the Notion API.
    - re: Regular expressions module.
    - os: Operating system interfaces module.
    - json: JSON encoder and decoder module.

Environment Variables:
    - NOTION_SECRET: Authentication token for the Notion API.

Example Usage:
    from md2notionpage import md2notionpage
    markdown_text = "# My Page\\nThis is a Notion page created from Markdown."
    title = "My Notion Page"
    parent_page_id = "YOUR_PARENT_PAGE_ID"
    notion_page_url = md2notionpage(markdown_text, title, parent_page_id)
"""

import os, re, glob, base64, json
from notion_client import Client
from os import environ

# Initialize the Notion client
notion = Client(auth=environ.get("NOTION_SECRET"))

def process_inline_formatting(text):
    """
    Process inline formatting in Markdown text and convert it to Notion rich text formatting.

    :param text: The Markdown text to be processed.
    :type text: str
    :return: A list of Notion rich text objects representing the processed text.
    :rtype: list
    """

    # Regular expressions for bold and italic markdown
    bold_pattern = r'\*\*(.+?)\*\*'
    italic_pattern = r'\*(.+?)\*'

    # Replace markdown with Notion rich text formatting
    def replace_bold(match):
        return {
            "type": "text",
            "text": {
                "content": match.group(1),
                "link": None
            },
            "annotations": {
                "bold": True,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": match.group(1),
            "href": None
        }

    def replace_italic(match):
        return {
            "type": "text",
            "text": {
                "content": match.group(1),
                "link": None
            },
            "annotations": {
                "bold": False,
                "italic": True,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": match.group(1),
            "href": None
        }

    # Apply the replacements for bold and italic formatting
    text_parts = []

    # Process bold matches
    bold_matches = list(re.finditer(bold_pattern, text))
    prev_end = 0
    for match in bold_matches:
        if prev_end != match.start():
            text_parts.append(text[prev_end:match.start()])
        text_parts.append(replace_bold(match))
        prev_end = match.end()
    text_parts.append(text[prev_end:])

    # Process italic matches
    new_text_parts = []
    for part in text_parts:
        if isinstance(part, str):
            italic_matches = list(re.finditer(italic_pattern, part))
            prev_end = 0
            for match in italic_matches:
                if prev_end != match.start():
                    new_text_parts.append(part[prev_end:match.start()])
                new_text_parts.append(replace_italic(match))
                prev_end = match.end()
            new_text_parts.append(part[prev_end:])
        else:
            new_text_parts.append(part)

    # Remove empty strings from the list and return the processed text parts
    return [({"type": "text", "text": {"content": part}} if type(part) == str else part) for part in new_text_parts if part != '']

def parse_markdown_to_notion_blocks(markdown):
    """
    Parse Markdown text and convert it into a list of Notion blocks.

    :param markdown: The Markdown text to be parsed.
    :type markdown: str
    :return: A list of Notion blocks representing the parsed Markdown content.
    :rtype: list
    """

    # Detect code blocks enclosed within triple backticks
    code_block_pattern = re.compile(r'```(.+?)```', re.DOTALL)
    numbered_list_pattern = r'^(\d+)\. '
    heading_pattern = r'^(#+) '

    code_blocks = {}
    def replace_code_blocks(match):
        index = len(code_blocks)
        code_blocks[index] = match.group(1)
        return f'CODE_BLOCK_{index}'

    # Replace code blocks with placeholders
    markdown = code_block_pattern.sub(replace_code_blocks, markdown)

    lines = markdown.split("\n")
    blocks = []
    for line in lines:

        # Check for headings and create appropriate heading blocks
        heading_match = re.match(heading_pattern, line)
        if heading_match:
            heading_level = len(heading_match.group(1))
            content = re.sub(heading_pattern, '', line)
            if 1 <= heading_level <= 3:
                block_type = f"heading_{heading_level}"
                blocks.append({
                    "object": "block",
                    "type": block_type,
                    block_type: {
                        "rich_text": process_inline_formatting(content)
                    }
                })

        # Check for code blocks and create code blocks
        elif line.startswith("CODE_BLOCK_"):
            code_block_index = int(line[len("CODE_BLOCK_"):])
            code_content = code_blocks[code_block_index].strip()
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "language": "plain text",
                    "rich_text": process_inline_formatting(code_content)
                }
            })

        # Check for bulleted lists and create bulleted list blocks
        elif line.startswith("* ") or line.startswith("- "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": process_inline_formatting(line[2:])
                }
            })

        # Check for numbered lists and create numbered list blocks
        elif re.match(numbered_list_pattern, line):
            line = re.sub(numbered_list_pattern, '', line)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": process_inline_formatting(line)
                }
            })

        # Create paragraph blocks for other lines
        elif line.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": process_inline_formatting(line)
                }
            })

    return blocks

def parse_md(markdown_text):
    """
    Parse Markdown text and convert it into Notion blocks.

    :param markdown_text: The Markdown text to be parsed.
    :type markdown_text: str
    :return: A list of Notion blocks representing the parsed Markdown content.
    :rtype: list
    """

    # Remove the first two lines of the Markdown text
    markdown_text = '\n'.join(markdown_text.splitlines()[2:]).strip()

    # Parse the transformed Markdown to create Notion blocks
    return parse_markdown_to_notion_blocks(markdown_text)


def create_notion_page_from_md(markdown_text, title, parent_page_id, cover_url=''):
    """
    Create a Notion page from Markdown text.

    :param markdown_text: The Markdown text to be converted into a Notion page.
    :type markdown_text: str
    :param title: The title of the new Notion page.
    :type title: str
    :param parent_page_id: The ID of the parent page under which the new page will be created.
    :type parent_page_id: str
    :param cover_url: (Optional) The URL of the cover image for the new page. Defaults to an empty string.
    :type cover_url: str
    :return: The URL of the created Notion page.
    :rtype: str
    """

    # Create a new child page under the parent page with the given title
    created_page = notion.pages.create(parent={
        "type": "page_id",
        "page_id": parent_page_id
    }, properties={}, children=[])

    cover = {}
    if cover_url != "":
        cover = {
            "external": {
                # Example URL: https://images.unsplash.com/photo-1507838153414-b4b713384a76?ixlib=rb-4.0.3&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=3600
                "url": cover_url
            }
        }

    # Update the page with the title and cover (if provided)
    notion.pages.update(created_page["id"], properties={
        "title": {
            "title": [{"type": "text", "text": {"content": title}}]
        }
    }, cover=cover)

    # Iterate through the parsed Markdown blocks and append them to the created page
    for block in parse_md(markdown_text):
        notion.blocks.children.append(
            created_page["id"],
            children=[block]
        )

    return created_page["url"]
