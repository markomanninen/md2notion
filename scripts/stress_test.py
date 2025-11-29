
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from md2notionpage import md2notionpage

# Load environment variables
load_dotenv()

def generate_long_critical_content():
    """
    Generates a markdown string that tests:
    1. Splitting logic (paragraphs > 2000 chars)
    2. Formatting preservation across splits
    3. Batching logic (> 100 blocks)
    """
    prefix = "START " + "a" * 1900
    # The critical section is around the 2000 char mark
    critical_section = "**CRITICAL_BOLD_SECTION_THAT_CROSSES_THE_BOUNDARY**" 
    suffix = "b" * 1000 + " END"
    
    long_paragraph = f"{prefix} {critical_section} {suffix}"
    
    many_blocks = []
    for i in range(150):
        many_blocks.append(f"- Batch Item {i+1}: This is a list item to test the 100-block batching limit.")
    
    many_blocks_str = "\n".join(many_blocks)
    
    markdown = f"""
# Validation: Splitting and Batching

## 1. Long Paragraph Splitting Test

The following paragraph is over 3000 characters long. It contains a bold section around the 2000-character mark.
Notion has a 2000-character limit per text block. This test verifies that the content is split correctly and the bold text is preserved (or at least readable).

{long_paragraph}

## 2. Batching Test (150 blocks)

The following list contains 150 items. Notion API allows max 100 children per request. 
This test verifies that the library correctly batches these into multiple requests.

{many_blocks_str}

## 3. End of Test

If you see this, the upload completed successfully.
"""
    return markdown

def main():
    # Check for API key
    if not os.getenv("NOTION_SECRET"):
        print("Error: NOTION_SECRET not found in environment variables.")
        print("Please create a .env file with NOTION_SECRET and NOTION_PARENT_PAGE_ID.")
        sys.exit(1)

    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    if not parent_page_id:
        print("Error: NOTION_PARENT_PAGE_ID not found in environment variables.")
        sys.exit(1)

    print(f"Target Parent Page ID: {parent_page_id}")
    print("\n--- Uploading Long Critical Content (Splitting & Batching) ---")
    
    try:
        long_md = generate_long_critical_content()
        title = f"Stress Test {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        url = md2notionpage(long_md, title, parent_page_id)
        print(f"Success! Page created at: {url}")
        print("Please check the Notion page to verify:")
        print("1. The long paragraph is split into multiple blocks.")
        print("2. The bold text 'CRITICAL_BOLD_SECTION...' is present.")
        print("3. All 150 list items are present.")
    except Exception as e:
        print(f"Failed to upload stress test: {e}")

if __name__ == "__main__":
    main()
