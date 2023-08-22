
import argparse
import os
from md2notionpage import md2notionpage

def main():
    parser = argparse.ArgumentParser(description='Convert a Markdown file to a Notion page.')
    parser.add_argument('markdown_file', type=str, help='Path to the Markdown file to convert.')
    parser.add_argument('parent_page_id', type=str, help='ID of the parent Notion page.')
    parser.add_argument('--title', type=str, help='Title for the Notion page (optional).')
    parser.add_argument('--cover_url', type=str, default='', help='Cover URL for the Notion page (optional).')
    args = parser.parse_args()

    # If title is not given, take it from the file base name
    title = args.title if args.title else os.path.splitext(os.path.basename(args.markdown_file))[0]

    try:
        # Read the Markdown content from the file
        with open(args.markdown_file, 'r') as file:
            markdown_content = file.read()

        # Create the Notion page
        notion_page_url = md2notionpage(markdown_content, title, args.parent_page_id, args.cover_url)
        print(f'Notion page created: {notion_page_url}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

if __name__ == '__main__':
    main()
