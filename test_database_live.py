#!/usr/bin/env python
"""
Live test script for database functionality.
Requires:
- NOTION_SECRET environment variable (loaded from .env)
- NOTION_PARENT_PAGE_ID environment variable

Usage:
    python test_database_live.py
    
The script will create test databases automatically and clean up after.
"""

import sys
import os
from dotenv import load_dotenv
from md2notionpage import md2notionpage

# Load environment variables from .env file
load_dotenv()

def main():
    # Check for API key
    if not os.environ.get("NOTION_SECRET"):
        print("ERROR: NOTION_SECRET environment variable not set")
        sys.exit(1)
    
    if not os.environ.get("NOTION_PARENT_PAGE_ID"):
        print("ERROR: NOTION_PARENT_PAGE_ID environment variable not set")
        sys.exit(1)
    
    from notion_client import Client
    notion = Client(auth=os.environ.get("NOTION_SECRET"))
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID")
    
    print("=" * 60)
    print("LIVE DATABASE TESTS")
    print("=" * 60)
    
    # Check for existing Task DB (from previous run)
    print("\n[Setup] Setting up test databases...")
    
    # Search for existing Task DB
    task_db_id = None
    task_db_url = None
    existing_task_db = None
    
    # Get children of parent page to find existing Task DB
    children = notion.blocks.children.list(block_id=parent_page_id)
    for child in children.get('results', []):
        if child.get('type') == 'child_database':
            db_title = child.get('child_database', {}).get('title', '')
            if 'Task DB' in db_title:
                task_db_id = child['id']
                existing_task_db = notion.databases.retrieve(database_id=task_db_id)
                task_db_url = existing_task_db.get('url', f"https://www.notion.so/{task_db_id.replace('-', '')}")
                print(f"         ♻️  Found existing 'Task' database: {task_db_id}")
                break
    
    # Database 1: Default "Name" title property (always create fresh)
    name_db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "Live Test - Name DB"}}],
        properties={"Name": {"title": {}}}
    )
    name_db_id = name_db['id']
    print(f"         ✅ Created 'Name' database: {name_db_id}")
    
    # Database 2: Only create if not found
    if task_db_id is None:
        task_db = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "Live Test - Task DB (RENAME Name->Task)"}}],
            properties={"Name": {"title": {}}}
        )
        task_db_id = task_db['id']
        task_db_url = task_db['url']
        print(f"         ✅ Created 'Task' database: {task_db_id}")
    
    print(f"            URL: {task_db_url}")
    
    all_passed = True
    task_test_passed = False
    
    # Test 1: Default title property "Name"
    print("\n" + "-" * 60)
    print("[Test 1] Creating entry with title_property_name='Name' (default)...")
    try:
        url = md2notionpage(
            "# Name Entry\n\nThis uses default **Name** title property.",
            f"Test Entry Name - {__import__('datetime').datetime.now().strftime('%H:%M:%S')}",
            name_db_id,
            parent_type='database',
            title_property_name='Name'
        )
        print(f"✅ SUCCESS: {url[:60]}...")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        all_passed = False
    
    # Test 2: Custom properties
    print("\n" + "-" * 60)
    print("[Test 2] Creating entry with custom properties dict...")
    try:
        url = md2notionpage(
            "# Custom Props\n\nUsing full properties dict.",
            "This title will be ignored",
            name_db_id,
            parent_type='database',
            properties={
                "Name": {"title": [{"text": {"content": f"Custom Props - {__import__('datetime').datetime.now().strftime('%H:%M:%S')}"}}]}
            }
        )
        print(f"✅ SUCCESS: {url[:60]}...")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        all_passed = False
    
    # Test 3: Custom title property "Task"
    print("\n" + "-" * 60)
    print("[Test 3] Creating entry with title_property_name='Task'...")
    try:
        url = md2notionpage(
            "# Task Entry\n\nThis uses custom **Task** title property.",
            f"Test Entry Task - {__import__('datetime').datetime.now().strftime('%H:%M:%S')}",
            task_db_id,
            parent_type='database',
            title_property_name='Task'
        )
        print(f"✅ SUCCESS: {url[:60]}...")
        task_test_passed = True
    except Exception as e:
        print(f"⚠️  FAILED: {type(e).__name__}")
        print("\n" + "!" * 60)
        print("!!! MANUAL ACTION REQUIRED !!!")
        print("!" * 60)
        print(f"\n1. Open this database in Notion:")
        print(f"   {task_db_url}")
        print(f"\n2. Click the 'Name' column header → Edit property")
        print(f"   Rename 'Name' to 'Task'")
        print(f"\n3. Run this test again:")
        print(f"   python test_database_live.py")
        print("\n" + "!" * 60)
    
    # Test 4: Wrong property name (should fail)
    print("\n" + "-" * 60)
    print("[Test 4] Testing error handling with wrong property name...")
    try:
        url = md2notionpage(
            "# Test",
            "Should Fail",
            name_db_id,
            parent_type='database',
            title_property_name='NonExistent'
        )
        print("❌ FAILED: Should have raised error")
        all_passed = False
    except Exception as e:
        print(f"✅ SUCCESS: Correctly rejected wrong property name")
    
    # Test 5: Invalid parent_type
    print("\n" + "-" * 60)
    print("[Test 5] Testing error handling with invalid parent_type...")
    try:
        url = md2notionpage(
            "# Test",
            "Should Fail",
            name_db_id,
            parent_type='invalid'
        )
        print("❌ FAILED: Should have raised ValueError")
        all_passed = False
    except ValueError as e:
        print(f"✅ SUCCESS: Correctly raised ValueError")
    except Exception as e:
        print(f"❌ FAILED: Wrong exception: {type(e).__name__}")
        all_passed = False
    
    # Cleanup
    print("\n" + "-" * 60)
    print("[Cleanup] Removing test databases...")
    
    # Only delete Name DB, keep Task DB if test didn't pass
    notion.blocks.delete(block_id=name_db_id)
    print(f"         ✅ Deleted 'Name' database")
    
    if task_test_passed:
        notion.blocks.delete(block_id=task_db_id)
        print(f"         ✅ Deleted 'Task' database")
    else:
        print(f"         ⏭️  Keeping 'Task' database for manual rename")
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed and task_test_passed:
        print("✅ ALL LIVE TESTS PASSED!")
    elif all_passed and not task_test_passed:
        print("⚠️  TESTS PASSED (except Task title - needs manual rename)")
    else:
        print("❌ SOME TESTS FAILED")
    
    print("\n📋 Tested features:")
    print("   • parent_type='database' parameter")
    print(f"   • title_property_name='Name' (default): {'✅' if all_passed else '❌'}")
    print(f"   • title_property_name='Task' (custom): {'✅' if task_test_passed else '⚠️ PENDING'}")
    print("   • Custom properties parameter")
    print("   • Error handling for wrong property name")
    print("   • Error handling for invalid parent_type")

if __name__ == "__main__":
    main()
