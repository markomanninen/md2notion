# md2notion - Claude Code Guide

## Creating Notion pages from Markdown files

Use the installed CLI tool in the venv. It auto-loads `.env` (NOTION_SECRET, NOTION_PARENT_PAGE_ID) via python-dotenv.

```bash
# Basic usage (title defaults to filename)
venv/bin/md2notionpage /path/to/file.md

# With custom title
venv/bin/md2notionpage /path/to/file.md --title "My Title"

# With cover image
venv/bin/md2notionpage /path/to/file.md --cover_url "https://..."

# To a specific parent page (overrides .env)
venv/bin/md2notionpage /path/to/file.md PARENT_PAGE_ID

# To a database (title property defaults to "Name")
venv/bin/md2notionpage /path/to/file.md DATABASE_ID --parent_type database --title_property_name "Title"

# Append to an existing block instead of creating a page
# (block URL from Notion's "Copy link to block", i.e. a URL with a #<block id> fragment)
venv/bin/md2notionpage /path/to/file.md "https://www.notion.so/Page-abc123...#<block id>"
```

`--print_page_info` prints details of the created page.

## Environment

- Python venv at `venv/` — always use `venv/bin/python3` or `venv/bin/md2notionpage`
- `.env` file contains `NOTION_SECRET` and `NOTION_PARENT_PAGE_ID`
- Do NOT use system python — `notion_client` is only installed in the venv
- The package is installed in editable mode, so the CLI runs the code of whatever branch is checked out. Reinstall with `venv/bin/pip install -e ".[dev]"` (also installs pytest)

## Code layout

- `md2notionpage/core.py` — Markdown parsing (mistune 3 tokens → Notion blocks in `NotionBlockConverter`), rich text splitting/batching for Notion's limits, and the page/block API calls
- `md2notionpage/cli.py` — the `md2notionpage` command
- Inline math uses a custom `INLINE_MATH_PATTERN` (closing `$` must not follow whitespace) so dollar amounts like `$5` stay as text
- Markdown tables become native Notion `table` blocks
- Nested children are placed inside the type object (e.g. `bulleted_list_item.children`), as the Notion API expects

## Running tests

```bash
venv/bin/python3 -m pytest -v
```

Tests mock the Notion client. `test_database_live.py` is a separate script that hits the real Notion API (`venv/bin/python3 test_database_live.py`) and creates/cleans up test databases.
