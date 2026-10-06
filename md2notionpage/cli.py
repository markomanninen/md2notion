
import argparse
import os
import sys
import urllib.parse
from dotenv import load_dotenv
load_dotenv()

from notion_client.errors import APIResponseError
from .core import create_notion_page_from_md as md2notionpage
from .core import append_md_to_notion_block

def main():
    parser = argparse.ArgumentParser(description='Convert a Markdown file to a Notion page.')
    parser.add_argument('markdown_file', type=str, help='Path to the Markdown file to convert.')
    parser.add_argument('parent_page_id', nargs='?', help='ID of the parent Notion page or a block URL. If not provided, uses NOTION_PARENT_PAGE_ID env var.')
    parser.add_argument('--title', type=str, help='Title for the Notion page (optional).')
    parser.add_argument('--title_property_name', type=str, default='Name', help='The name of the title property in the database (used with --parent_type database). Defaults to "Name". (optional).')
    parser.add_argument('--cover_url', type=str, default='', help='Cover URL for the Notion page (optional).')
    parser.add_argument('--parent_type', type=str.lower, choices=['page', 'database'], default='page', help='"page" or "database"')
    parser.add_argument('--print_page_info', action='store_true', help='Print info about the newly created page')

    args = parser.parse_args()

    # Determine Parent Page ID or Block URL
    parent_input = args.parent_page_id or os.getenv("NOTION_PARENT_PAGE_ID")
    if not parent_input:
        print("❌ Error: Parent Page ID or Block URL not provided and NOTION_PARENT_PAGE_ID not set.")
        print("\n💡 Hint: Set NOTION_PARENT_PAGE_ID in your .env file or pass it as an argument.")
        print("\n⚠️  Don't forget: After setting up your integration, you must:")
        print("   1. Open the parent page in Notion")
        print("   2. Click '...' → 'Add connections'")
        print("   3. Select your integration to grant access")
        sys.exit(1)

    try:
        # Read the Markdown content from the file
        if not os.path.exists(args.markdown_file):
            print(f"Error: File {args.markdown_file} not found.")
            sys.exit(1)
            
        with open(args.markdown_file, 'r', encoding='utf-8') as file:
            markdown_content = file.read()

        # If title is not given, take it from the file base name
        title = args.title if args.title else os.path.splitext(os.path.basename(args.markdown_file))[0]

        target_block_id = None
        if parent_input and ("http://" in parent_input or "https://" in parent_input):
            parsed = urllib.parse.urlparse(parent_input)
            if parsed.fragment and len(parsed.fragment) >= 32:
                target_block_id = parsed.fragment

        if target_block_id:
            notion_url = append_md_to_notion_block(markdown_content, target_block_id, print_page_info=args.print_page_info)
            print(f'Markdown content appended to Notion block: {notion_url}')
        else:
            # Create the Notion page
            notion_url = md2notionpage(markdown_content, title, parent_input, cover_url=args.cover_url, parent_type=args.parent_type, 
                                            print_page_info=args.print_page_info, title_property_name=args.title_property_name)
            print(f'Notion page created: {notion_url}')

    except APIResponseError as e:
        error_code = getattr(e, 'code', None)
        error_msg = str(e)
        
        if error_code == 'unauthorized' or "API token is invalid" in error_msg:
            print(f"\n❌ Error: {error_msg}")
            print("\n💡 Hint: Your Notion API token seems to be invalid or missing.")
            print("1. Check your .env file for NOTION_SECRET.")
            print("2. Ensure you have created an integration at https://www.notion.so/my-integrations")
            print("3. Make sure you have shared the parent page with your integration.")
        
        elif "body failed validation" in error_msg and "should be a valid uuid" in error_msg:
            print(f"\n❌ Error: Invalid Parent Page ID or Block ID")
            print(f"\nThe ID you provided is not valid: {parent_input}")
            print("\n💡 How to find your Notion Page ID:")
            print("1. Open the page in Notion")
            print("2. Click 'Share' and 'Copy link'")
            print("3. The page ID is the 32-character code in the URL")
            print("   Example: https://notion.so/My-Page-abc123def456...")
            print("   Page ID: abc123def456...")
            print("\n4. Update NOTION_PARENT_PAGE_ID in your .env file with this ID")
        
        elif error_code == 'object_not_found':
            print(f"\n❌ Error: Page or Block not found")
            print(f"\nThe ID '{parent_input}' does not exist or is not accessible.")
            print("\n💡 Possible solutions:")
            print("1. Verify the page ID is correct")
            print("2. Make sure you've shared the page with your integration")
            print("3. Check that the page hasn't been deleted")
        
        elif error_code == 'restricted_resource':
            print(f"\n❌ Error: Access denied")
            print(f"\nYour integration doesn't have access to this page.")
            print("\n💡 To fix this:")
            print("1. Open the parent page in Notion")
            print("2. Click '...' (more options) → 'Add connections'")
            print("3. Select your integration from the list")
        
        elif "Invalid page cover URL" in error_msg or "cover" in error_msg.lower():
            print(f"\n❌ Error: Invalid cover image URL")
            print(f"\nThe cover URL you provided is not valid or accessible.")
            print("\n💡 Cover URL requirements:")
            print("1. Must be a valid HTTP or HTTPS URL")
            print("2. Must be publicly accessible (no authentication required)")
            print("3. Should be an image file (jpg, png, gif, etc.)")
            print("4. Example: https://images.unsplash.com/photo-123456...")
            print("\n💡 Tip: Leave --cover_url empty to create a page without a cover")
        
        else:
            print(f'\n❌ Notion API Error: {e}')
        
        sys.exit(1)

    except Exception as e:
        print(f'\nAn error occurred: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()
