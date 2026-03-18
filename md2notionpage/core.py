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
    - mistune: Markdown parser.
    - re: Regular expressions module.
    - os: Operating system interfaces module.
    - json: JSON encoder and decoder module.

Environment Variables:
    - NOTION_SECRET: Authentication token for the Notion API.
"""

import os, re, glob, base64, json, pprint
import mistune
from mistune.plugins.math import math
from mistune.plugins.table import table
from mistune.plugins.formatting import strikethrough
from mistune.plugins.task_lists import task_lists
from notion_client import Client
from os import environ
from copy import deepcopy

# Initialize the Notion client (lazy initialization)
notion = None

class NotionBlockConverter:
    def __init__(self):
        # Create a mistune Markdown instance with plugins
        self.md = mistune.create_markdown(
            renderer=None,
            plugins=[math, table, strikethrough, task_lists]
        )

    def parse(self, markdown):
        # mistune 3.x returns (tokens, state)
        tokens, _ = self.md.parse(markdown)
        return self.render_blocks(tokens)

    def render_blocks(self, tokens):
        blocks = []
        for token in tokens:
            rendered = self.render_block(token)
            if rendered:
                if isinstance(rendered, list):
                    blocks.extend(rendered)
                else:
                    blocks.append(rendered)
        return blocks

    def render_block(self, token):
        token_type = token['type']

        if token_type == 'heading':
            level = token['attrs']['level']
            # Notion only supports heading_1, heading_2, heading_3
            level = min(max(level, 1), 3)
            block_type = f"heading_{level}"
            return {
                "object": "block",
                "type": block_type,
                block_type: {
                    "rich_text": self.render_inlines(token.get('children', []))
                }
            }

        elif token_type == 'paragraph':
            children = token.get('children', [])
            # If paragraph contains ONLY an image (or image + whitespace), render it as an image block
            # This is common in standalone image lines
            inlines_only_image = [t for t in children if t['type'] != 'text' or t['raw'].strip()]
            if len(inlines_only_image) == 1 and inlines_only_image[0]['type'] == 'image':
                img_token = inlines_only_image[0]
                return {
                    "object": "block",
                    "type": "image",
                    "image": {
                        "external": {"url": img_token['attrs']['url']},
                        "caption": self.render_inlines(img_token.get('children', []))
                    }
                }
            
            return {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": self.render_inlines(children)
                }
            }

        elif token_type == 'list':
            # Mistune groups list items into a 'list' token
            items = []
            is_ordered = token['attrs'].get('ordered', False)
            for child in token.get('children', []):
                rendered_item = self.render_block(child)
                if rendered_item and isinstance(rendered_item, dict):
                    if rendered_item.get('type') == 'list_item':
                        if is_ordered:
                            rendered_item['type'] = 'numbered_list_item'
                            rendered_item['numbered_list_item'] = rendered_item.pop('list_item')
                        else:
                            rendered_item['type'] = 'bulleted_list_item'
                            rendered_item['bulleted_list_item'] = rendered_item.pop('list_item')
                    items.append(rendered_item)
            return items

        elif token_type in ('list_item', 'task_list_item'):
            children_tokens = token.get('children', [])
            
            rich_text = []
            nested_blocks = []
            
            for i, child in enumerate(children_tokens):
                if i == 0 and child['type'] in ('text', 'paragraph', 'block_text'):
                    if child['type'] in ('paragraph', 'block_text'):
                        rich_text = self.render_inlines(child.get('children', []))
                    else:
                        rich_text = self.render_inlines([child])
                else:
                    rendered = self.render_block(child)
                    if rendered:
                        if isinstance(rendered, list):
                            nested_blocks.extend(rendered)
                        else:
                            nested_blocks.append(rendered)

            if token_type == 'task_list_item':
                checked = token['attrs'].get('checked', False)
                block = {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": rich_text,
                        "checked": checked
                    }
                }
                if nested_blocks:
                    block["to_do"]["children"] = nested_blocks
                return block
            else:
                block = {
                    "object": "block",
                    "type": "list_item", # Placeholder
                    "list_item": {
                        "rich_text": rich_text
                    }
                }
                if nested_blocks:
                    block["list_item"]["children"] = nested_blocks
                return block

        elif token_type == 'block_quote':
            return {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": self.render_inlines(token.get('children', []))
                }
            }

        elif token_type == 'block_code':
            language = token['attrs'].get('info', 'plain text')
            if not language:
                language = 'plain text'
            # Notion language map (approximate)
            lang_map = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'md': 'markdown'
            }
            language = lang_map.get(language.lower(), language.lower())
            
            return {
                "object": "block",
                "type": "code",
                "code": {
                    "language": language,
                    "rich_text": [{"type": "text", "text": {"content": token['raw'].strip()}}]
                }
            }

        elif token_type == 'thematic_break':
            return {
                "object": "block",
                "type": "divider",
                "divider": {}
            }

        elif token_type == 'block_math':
            return {
                "type": "equation",
                "equation": {
                    "expression": token['raw'].strip()
                }
            }

        elif token_type == 'table':
            latex_table = self.convert_table_token_to_latex(token)
            return {
                "type": "equation",
                "equation": {
                    "expression": latex_table
                }
            }

        elif token_type == 'image':
            return {
                "object": "block",
                "type": "image",
                "image": {
                    "external": {"url": token['attrs']['url']},
                    "caption": self.render_inlines(token.get('children', []))
                }
            }

        return None

    def render_inlines(self, tokens):
        rich_texts = []
        for token in tokens:
            rendered = self.render_inline(token)
            if rendered:
                if isinstance(rendered, list):
                    rich_texts.extend(rendered)
                else:
                    rich_texts.append(rendered)
        return rich_texts

    def render_inline(self, token):
        token_type = token['type']
        
        if token_type == 'text':
            return {
                "type": "text",
                "text": {"content": token['raw'], "link": None},
                "annotations": self.get_empty_annotations(),
                "plain_text": token['raw'],
                "href": None
            }
        
        elif token_type == 'softbreak':
            return {
                "type": "text",
                "text": {"content": " ", "link": None},
                "annotations": self.get_empty_annotations(),
                "plain_text": " ",
                "href": None
            }

        elif token_type == 'strong':
            content = self.render_inlines(token.get('children', []))
            for item in content:
                if 'annotations' in item:
                    item['annotations']['bold'] = True
            return content

        elif token_type == 'emphasis':
            content = self.render_inlines(token.get('children', []))
            for item in content:
                if 'annotations' in item:
                    item['annotations']['italic'] = True
            return content

        elif token_type == 'strikethrough':
            content = self.render_inlines(token.get('children', []))
            for item in content:
                if 'annotations' in item:
                    item['annotations']['strikethrough'] = True
            return content

        elif token_type == 'codespan':
            return {
                "type": "text",
                "text": {"content": token['raw'], "link": None},
                "annotations": {**self.get_empty_annotations(), "code": True},
                "plain_text": token['raw'],
                "href": None
            }

        elif token_type == 'link':
            content = self.render_inlines(token.get('children', []))
            url = token['attrs']['url']
            for item in content:
                if item['type'] == 'text':
                    item.setdefault('text', {})
                    item['text']['link'] = {"url": url}
                    item['href'] = url
            return content

        elif token_type == 'inline_math':
            return {
                "type": "equation",
                "equation": {
                    "expression": token['raw'].strip()
                }
            }
        
        elif token_type == 'image':
            alt = token['attrs'].get('alt', 'image')
            url = token['attrs']['url']
            return {
                "type": "text",
                "text": {"content": f"![{alt}]({url})", "link": None},
                "annotations": self.get_empty_annotations(),
                "plain_text": f"![{alt}]({url})",
                "href": None
            }

        return None

    def get_empty_annotations(self):
        return {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default"
        }

    def convert_table_token_to_latex(self, token):
        header = None
        body = []
        for child in token.get('children', []):
            if child['type'] == 'table_head':
                header = child
            elif child['type'] == 'table_body':
                body = child

        latex_rows = []
        
        def get_cell_text(cell_token):
            text = ""
            for child in cell_token.get('children', []):
                if 'raw' in child:
                    text += child['raw']
                elif 'children' in child:
                    text += get_cell_text(child)
            return text.strip()

        if header:
            for row in header.get('children', []):
                cells = []
                for cell in row.get('children', []):
                    txt = get_cell_text(cell)
                    cells.append(f"\\textsf{{\\textbf{{{txt}}}}}")
                latex_rows.append(" & ".join(cells) + " \\\\\\hline")

        if body:
            for row in body.get('children', []):
                cells = []
                for cell in row.get('children', []):
                    txt = get_cell_text(cell)
                    cells.append(f"\\textsf{{{txt}}}")
                latex_rows.append(" & ".join(cells) + " \\\\\\hline")

        if not latex_rows:
            return ""

        col_count = 0
        if header and header.get('children'):
            col_count = len(header['children'][0].get('children', []))
        elif body and body.get('children'):
            col_count = len(body['children'][0].get('children', []))
        
        table_column = "|c" * col_count
        table_content = "\n".join(latex_rows)
        return f"\\def\\arraystretch{{1.4}}\\begin{{array}}{{{table_column}|}}\\hline\n{table_content}\\end{{array}}"

# --- Replacement Functions ---

def process_inline_formatting(text):
    converter = NotionBlockConverter()
    tokens, _ = converter.md.parse(text)
    if tokens and tokens[0]['type'] == 'paragraph':
        return converter.render_inlines(tokens[0].get('children', []))
    return converter.render_inlines(tokens)

def parse_markdown_to_notion_blocks(markdown):
    converter = NotionBlockConverter()
    return converter.parse(markdown)

def parse_md(markdown_text):
    return parse_markdown_to_notion_blocks(markdown_text.strip())

# --- Utilities ---

def split_rich_text(rich_text_list, max_len=2000):
    if not rich_text_list:
        return []

    def visible_text_of_segment(seg):
        t = seg.get("type")
        if t == "text":
            return seg.get("text", {}).get("content", "") or seg.get("plain_text", "")
        if t == "equation":
            return seg.get("equation", {}).get("expression", "") or seg.get("plain_text", "")
        if t == "mention":
            return seg.get("plain_text", "") or ""
        return seg.get("plain_text", "") or ""

    def make_slice(seg, start_idx, end_idx):
        new_seg = deepcopy(seg)
        if new_seg.get("type") == "text":
            new_seg.setdefault("text", {})
            original = seg.get("text", {}).get("content", "")
            new_seg["text"]["content"] = original[start_idx:end_idx]
            if "plain_text" in new_seg:
                new_seg["plain_text"] = new_seg["text"]["content"]
        return new_seg

    def tokenize(text):
        if text == "":
            return [""]
        tokens = re.findall(r'\S+\s*', text)
        return tokens or [text]

    chunks = []
    current = []
    current_len = 0

    for seg in rich_text_list:
        seg_type = seg.get("type", "text")
        seg_text = visible_text_of_segment(seg)
        seg_len = len(seg_text)

        if seg_type in ("equation", "mention"):
            if current_len + seg_len <= max_len:
                current.append(deepcopy(seg))
                current_len += seg_len
            else:
                if current:
                    chunks.append(current)
                chunks.append([deepcopy(seg)])
                current = []
                current_len = 0
            continue

        if seg_type == "text":
            text_content = seg.get("text", {}).get("content", "") or ""
            tokens = tokenize(text_content)

            current_pos = 0
            for token in tokens:
                t_len = len(token)
                start_idx = text_content.find(token, current_pos)
                if start_idx == -1: # Fallback
                     start_idx = current_pos
                
                if t_len > max_len:
                    if current:
                        chunks.append(current)
                        current = []
                        current_len = 0
                    start = 0
                    while start < t_len:
                        end = min(start + max_len, t_len)
                        chunks.append([make_slice(seg, start_idx + start, start_idx + end)])
                        start = end
                    current_pos = start_idx + t_len
                    continue

                if current_len + t_len <= max_len:
                    current.append(make_slice(seg, start_idx, start_idx + len(token)))
                    current_len += t_len
                    current_pos = start_idx + t_len
                    continue

                if current:
                    chunks.append(current)
                    current = []
                    current_len = 0

                current.append(make_slice(seg, start_idx, start_idx + len(token)))
                current_len += t_len
                current_pos = start_idx + t_len
            continue

        if current_len + seg_len <= max_len:
            current.append(deepcopy(seg))
            current_len += seg_len
        else:
            if current:
                chunks.append(current)
            chunks.append([deepcopy(seg)])
            current = []
            current_len = 0

    if current:
        chunks.append(current)
    return chunks

def create_notion_page_from_md(markdown_text, title, parent_page_id, cover_url='', parent_type='page', properties=None, title_property_name='Name', print_page_info=False):
    global notion
    if notion is None:
        notion = Client(auth=environ.get("NOTION_SECRET"))

    if parent_type == 'page':
        created_page = notion.pages.create(parent={
            "type": "page_id",
            "page_id": parent_page_id
        }, properties={}, children=[])
    elif parent_type == 'database':
        if properties is None:
            properties = {
                title_property_name: {
                    "title": [{"text": {"content": title}}]
                }
            }
        created_page = notion.pages.create(
            parent={"database_id": parent_page_id},
            properties=properties
        )
    else:
        raise ValueError(f"Unrecognized parent_type: {parent_type!r}. Expected 'page' or 'database'.")

    update_props = {
        "title": {
            "title": [{"type": "text", "text": {"content": title}}]
        }
    }
    update_payload = {"properties": update_props}
    if cover_url:
        update_payload["cover"] = {"external": {"url": cover_url}}
    
    notion.pages.update(created_page["id"], **update_payload)

    final_blocks = []
    for block in parse_md(markdown_text):
        block_type = block.get("type")
        if block_type in ("paragraph", "heading_1", "heading_2", "heading_3", "quote", "bulleted_list_item", "numbered_list_item", "to_do"):
            rich_text_list = block[block_type].get("rich_text", [])
            total_visible = sum(
                len(
                    rt.get("text", {}).get("content", "")
                    if rt.get("type") == "text"
                    else rt.get("equation", {}).get("expression", "")
                    if rt.get("type") == "equation"
                    else rt.get("plain_text", "")
                )
                for rt in rich_text_list
            )

            if total_visible > 2000:
                chunks = split_rich_text(rich_text_list, 2000)
                for rich_chunk in chunks:
                    new_block = deepcopy(block)
                    new_block[block_type]["rich_text"] = rich_chunk
                    final_blocks.append(new_block)
                continue
        final_blocks.append(block)

    batch = []
    for block in final_blocks:
        if "object" not in block:
            block["object"] = "block"
        batch.append(block)
        if len(batch) == 100:
            notion.blocks.children.append(created_page["id"], children=batch)
            batch = []

    if batch:
        notion.blocks.children.append(created_page["id"], children=batch)

    if print_page_info:
        pprint.pprint(created_page)

    return created_page["url"]
