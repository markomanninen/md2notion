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

def replace_part(parts, pattern, replace_function):
    # Process italic matches
    new_text_parts = []
    for part in parts:
        if isinstance(part, str):
            matches = list(re.finditer(pattern, part))
            prev_end = 0
            for match in matches:
                if prev_end != match.start():
                    new_text_parts.append(part[prev_end:match.start()])
                new_text_parts.append(replace_function(match))
                prev_end = match.end()
            new_text_parts.append(part[prev_end:])
        else:
            new_text_parts.append(part)
    return new_text_parts

def process_inline_formatting(text):
    """
    Process inline formatting in Markdown text and convert it to Notion rich text formatting.

    :param text: The Markdown text to be processed.
    :type text: str
    :return: A list of Notion rich text objects representing the processed text.
    :rtype: list
    """

    # Regular expressions for bold and italic markdown
    code_pattern = r'`(.+?)`'
    bold_pattern = r'(\*\*(.+?)\*\*)|(__(.+?)__)'
    overline_pattern = r'\~(.+?)\~'
    inline_katex_pattern = r'\$(.+?)\$'
    italic_pattern = r'(\*(.+?)\*)|(_(.+?)_)'
    link_pattern = r'\[(.+?)\]\((.+?)\)'
    bold_italic_pattern = r'(__\*(.+?)\*__)|(\*\*_(.+?)_\*\*)'

    def replace_katex(match):
        return {
            "type": "equation",
            "equation": {
                "expression": match.group(1)
            }
        }

    def replace_bolditalic(match):
        content = match.group(2) or match.group(4)
        return {
            "type": "text",
            "text": {
                "content": content,
                "link": None
            },
            "annotations": {
                "bold": True,
                "italic": True,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": content,
            "href": None
        }

    # Replace markdown with Notion rich text formatting
    def replace_code(match):
        return {
            "type": "text",
            "text": {
                "content": match.group(1),
                "link": None
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": True,
                "color": "default"
            },
            "plain_text": match.group(1),
            "href": None
        }

    # Replace markdown with Notion rich text formatting
    def replace_overline(match):
        return {
            "type": "text",
            "text": {
                "content": match.group(1),
                "link": None
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": True,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": match.group(1),
            "href": None
        }
    # Replace markdown with Notion rich text formatting
    def replace_bold(match):
        return {
            "type": "text",
            "text": {
                "content": match.group(2) or match.group(4),
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
            "plain_text": match.group(2) or match.group(4),
            "href": None
        }

    def replace_italic(match):
        return {
            "type": "text",
            "text": {
                "content": match.group(2) or match.group(4),
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
            "plain_text": match.group(2) or match.group(4),
            "href": None
        }

    def replace_link(match):
        return {
            "type": "text",
            "text": {
                "content": match.group(1),
                "link": {
                    "url": match.group(2)
                }
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": match.group(1),
            "href": match.group(2)
        }

    # Apply the replacements for bold and italic formatting
    text_parts = []

    # Process bold italic matches
    matches = list(re.finditer(bold_italic_pattern, text))
    prev_end = 0
    for match in matches:
        if prev_end != match.start():
            text_parts.append(text[prev_end:match.start()])
        text_parts.append(replace_bolditalic(match))
        prev_end = match.end()
    text_parts.append(text[prev_end:])

    text_parts = replace_part(text_parts, inline_katex_pattern, replace_katex)
    text_parts = replace_part(text_parts, bold_pattern, replace_bold)
    text_parts = replace_part(text_parts, italic_pattern, replace_italic)
    text_parts = replace_part(text_parts, overline_pattern, replace_overline)
    text_parts = replace_part(text_parts, code_pattern, replace_code)
    text_parts = replace_part(text_parts, link_pattern, replace_link)

    # Remove empty strings from the list and return the processed text parts
    return [({"type": "text", "text": {"content": part}} if type(part) == str else part) for part in text_parts if part != '']

# katex
def convert_markdown_table_to_latex(text):
    split_column = text.split('\n')
    has_header = False
    # Check if the second line is a delimiter
    if re.match(r'\|\s*-+\s*\|', split_column[1]):
        # Remove the delimiter line
        split_column.pop(1)
        has_header = True
    table_content = ""
    for i, row in enumerate(split_column):
        modified_content = re.findall(r'(?<=\|).*?(?=\|)', row)
        new_text = ""
        for j, cell in enumerate(modified_content):
            cell_text = f"\\textsf{{{cell.strip()}}}"
            if i == 0 and has_header:
                cell_text = f"\\textsf{{\\textbf{{{cell.strip()}}}}}"
            if j == len(modified_content) - 1:
                cell_text += " \\\\\\hline\n"
            else:
                cell_text += " & "
            new_text += cell_text
        table_content += new_text

    count_column = len(split_column[0].split('|'))

    table_column = "|c" * count_column
    add_table = f"\\def\\arraystretch{{1.4}}\\begin{{array}}{{{table_column}|}}\\hline\n{table_content}\\end{{array}}"

    return add_table

def parse_markdown_to_notion_blocks(markdown):
    """
    Parse Markdown text and convert it into a list of Notion blocks.

    :param markdown: The Markdown text to be parsed.
    :type markdown: str
    :return: A list of Notion blocks representing the parsed Markdown content.
    :rtype: list
    """

    # Detect code blocks enclosed within triple backticks
    code_block_pattern = re.compile(r'```(\w+?)\n(.+?)```', re.DOTALL)
    # katex
    latex_block_pattern = re.compile(r'\$\$(.+?)\$\$', re.DOTALL)
    numbered_list_pattern_nested = r'^( *)(\d+)\. '
    unordered_list_pattern_nested = r'^( *)(\-) '
    heading_pattern = r'^(#+) '

    #indented_code_pattern = re.compile(r'^ {4}(.+)$', re.MULTILINE)
    triple_backtick_code_pattern = re.compile(r'^```(.+?)```', re.MULTILINE | re.DOTALL)
    blockquote_pattern = r'^> (.+)$'
    horizontal_line_pattern = r'^-{3,}$'
    image_pattern = r'!\[(.*?)\]\((.*?)\)'

    code_blocks = {}
    def replace_code_blocks(match):
        index = len(code_blocks)
        language, content = match.group(1), match.group(2)
        code_blocks[index] = (language or 'plain text').strip(), content.strip()
        return f'CODE_BLOCK_{index}'

    # Replace code blocks with placeholders
    markdown = code_block_pattern.sub(replace_code_blocks, markdown)

    # katex
    latex_blocks = {}
    def replace_latex_blocks(match):
        index = len(latex_blocks)
        latex_blocks[index] = (match.group(1)+"").strip()
        return f'LATEX_BLOCK_{index}'

    # Replace code blocks with placeholders
    markdown = latex_block_pattern.sub(replace_latex_blocks, markdown)

    lines = markdown.split("\n")
    blocks = []

    # Initialize variables to keep track of the current table
    current_table = []
    in_table = False

    current_indent = 0
    stack = [blocks]

    indented_code_accumulator = []
    for line in lines:

        # Check if the line is a table row (e.g., "| Header 1 | Header 2 |" or "| Content 1 | Content 2 |")
        is_table_row = re.match(r'\|\s*[^-|]+\s*\|', line)
        # Check if the line is a table delimiter (e.g., "|---|---|")
        is_table_delimiter = re.match(r'\|\s*[-]+\s*\|\s*[-]+\s*\|', line)

        # If we find table row or delimiter, add the line to the current table
        if is_table_row or is_table_delimiter:
            current_table.append(line)
            in_table = True
            continue
        elif in_table and (not is_table_row and not is_table_delimiter):
            # If we find a non-table line and we're in a table, end the current table
            in_table = False
            # Process the current table
            table_str = "\n".join(current_table)
            # katex
            latex_table = convert_markdown_table_to_latex(table_str)
            # Create Notion equation block with LaTeX table expression
            equation_block = {
                "type": "equation",
                "equation": {
                    "expression": latex_table
                }
            }
            blocks.append(equation_block)
            # Reset the current table
            current_table = []
            continue

        list_match = re.match(numbered_list_pattern_nested, line)
        if list_match:
            indent = len(list_match.group(1))
            line = line[len(list_match.group(0)):]

            item = {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": process_inline_formatting(line)
                }
            }

            while indent < current_indent:
                # If the indentation is less than the current level, go back one level in the stack
                stack.pop()
                current_indent -= 1

            if indent == current_indent:
                # Same level of indentation, add to the current level of the stack
                stack[-1].append(item)
            else: # indent > current_indent
                # Nested item, add it as a child of the previous item
                if 'children' not in stack[-1][-1]['numbered_list_item']:
                    stack[-1][-1]['numbered_list_item']['children'] = []
                stack[-1][-1]['numbered_list_item']['children'].append(item)
                stack.append(stack[-1][-1]['numbered_list_item']['children']) # Add a new level to the stack
                current_indent += 1

            continue

        list_match = re.match(unordered_list_pattern_nested, line)
        if list_match:
            indent = len(list_match.group(1))
            line = line[len(list_match.group(0)):]

            item = {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": process_inline_formatting(line)
                }
            }

            while indent < current_indent:
                # If the indentation is less than the current level, go back one level in the stack
                stack.pop()
                current_indent -= 1

            if indent == current_indent:
                # Same level of indentation, add to the current level of the stack
                stack[-1].append(item)
            else: # indent > current_indent
                # Nested item, add it as a child of the previous item
                if 'children' not in stack[-1][-1]['bulleted_list_item']:
                    stack[-1][-1]['bulleted_list_item']['children'] = []
                stack[-1][-1]['bulleted_list_item']['children'].append(item)
                stack.append(stack[-1][-1]['bulleted_list_item']['children']) # Add a new level to the stack
                current_indent += 1

            continue

        if line.startswith('    '):  # Check if the line is indented
            indented_code_accumulator.append(line[4:])  # Remove the leading spaces
            continue
        else:
            if indented_code_accumulator:  # Check if there are accumulated lines
                code_block = '\n'.join(indented_code_accumulator)
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "language": "plain text",
                        "rich_text": [{"type": "text", "text": {"content": code_block}}]
                    }
                })
                # Clear the accumulator
                indented_code_accumulator = []

        # Check for headings and create appropriate heading blocks
        heading_match = re.match(heading_pattern, line)
        blockquote_match = re.match(blockquote_pattern, line)
        image_match = re.search(image_pattern, line)

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

        # Check for horizontal line and create divider blocks
        elif re.match(horizontal_line_pattern, line):
            blocks.append({
                "divider": {},
                "type": "divider"
            })

        # Check for blockquote and create blockquote blocks
        elif blockquote_match:
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": process_inline_formatting(blockquote_match.group(1))
                }
            })

        # Check for code blocks and create code blocks
        elif line.startswith("CODE_BLOCK_"):
            code_block_index = int(line[len("CODE_BLOCK_"):])
            language, code_block = code_blocks[code_block_index]
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "language": language,
                    "rich_text": [{"type": "text", "text": {"content": code_block}}]
                }
            })

        # Check for katex blocks
        elif line.startswith("LATEX_BLOCK_"):
            latex_block_index = int(line[len("LATEX_BLOCK_"):])
            latex_content = latex_blocks[latex_block_index]
            blocks.append({
                "type": "equation",
                "equation": {
                    "expression": latex_content
                }
            })

        # Image blocks
        elif image_match:
            block = {
              "object": "block",
              "type": "image",
              "image": {
                "external":{
                    "url": image_match.group(2),
                }
              }
            }
            caption = image_match.group(1)
            if caption:
                block["image"]["caption"] = [
                  {
                    "type": "text",
                    "text": {
                      "content": caption,
                      "link": None
                    }
                  }
                ]
            blocks.append(block)

        # Create paragraph blocks for other lines
        elif line.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": process_inline_formatting(line)
                }
            })

    # If there's an unfinished table at the end of the lines, process it
    if in_table:
        table_str = "\n".join(current_table)
        latex_table = convert_markdown_table_to_latex(table_str)
        equation_block = {
            "type": "equation",
            "equation": {
                "expression": latex_table
            }
        }
        blocks.append(equation_block)

    # Add any remaining indented lines as a code block
    if indented_code_accumulator:
        code_block = '\n'.join(indented_code_accumulator)
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "language": "plain text",
                "rich_text": [{"type": "text", "text": {"content": code_block}}]
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
    # Parse the transformed Markdown to create Notion blocks
    return parse_markdown_to_notion_blocks(markdown_text.strip())


# helper function for batching -> helps to split words safely before pushing to notion
def split_text_safely(text, max_len=2000):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        if end == len(text):
            chunks.append(text[start:end])
            break
        
        split_at = text.rfind(" ", start, end)
        if split_at == -1:
            split_at = end  # if no spaces found then hard cut

        chunks.append(text[start:split_at])
        start = split_at + 1
    return chunks


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

    if cover_url != "":
        # Update the page with the title and cover (if provided)
        notion.pages.update(created_page["id"], properties={
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        cover = {
            "external": {
                # Example URL: https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg
                "url": cover_url
            }
        })
    else:
        # Update the page with the title and cover (if provided)
        notion.pages.update(created_page["id"], properties={
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        })


    # final blocks with splitting applied
    final_blocks = []

    for block in parse_md(markdown_text):
        if block["type"] == "paragraph":
            text = block["paragraph"]["rich_text"][0]["text"]["content"]
            if len(text) > 2000:
                chunks = split_text_safely(text, 2000)
                for chunk in chunks:
                    new_block = {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": chunk}
                            }]
                        }
                    }
                    final_blocks.append(new_block)
                continue  # skip adding original oversized block

        final_blocks.append(block)

    # Batch upload blocks (Notion API limit: max 100 children per request).
    batch = []
    for block in final_blocks:
        batch.append(block)
        if len(batch) == 100:
            notion.blocks.children.append(created_page["id"], children=batch)
            batch = []
    # Upload any remaining blocks
    if batch:
        notion.blocks.children.append(created_page["id"], children=batch)