import unittest
from unittest.mock import MagicMock, patch
from md2notionpage.core import split_rich_text
from md2notionpage import md2notionpage
from copy import deepcopy


class TestSplittingAndBatching(unittest.TestCase):

    def make_text_seg(self, text):
        return {"type": "text", "text": {"content": text}}


    # 1) Paragraph >2000 chars should split correctly

    def test_paragraph_splitting(self):
        long_text = "a" * 5000
        seg = self.make_text_seg(long_text)

        chunks = split_rich_text([seg], 2000)

        # Expect 3 chunks: 2000 + 2000 + 1000
        self.assertEqual(len(chunks), 3)

        # Ensure chunk lengths conform
        for chunk in chunks:
            visible = "".join(
                rt["text"]["content"]
                for rt in chunk
                if rt["type"] == "text"
            )
            self.assertLessEqual(len(visible), 2000)


    # 2) Splitting must preserve formatting (bold/code/link are not lost)

    def test_preserves_annotations(self):
        seg = {
            "type": "text",
            "text": {"content": "hello world " * 200},
            "annotations": {"bold": True, "code": False, "italic": False},
        }

        chunks = split_rich_text([seg], 2000)

        # All chunks must contain the SAME annotations
        for chunk in chunks:
            for rt in chunk:
                if rt["type"] == "text":
                    self.assertTrue(rt.get("annotations", {}).get("bold"))


    # 3) Batching logic: more than 100 blocks triggers multiple append calls

    def test_batching_over_100_blocks(self):
        fake_notion = MagicMock()

        # Patch the global notion client inside the module
        with patch("md2notionpage.core.notion", fake_notion):
            # Create 250 simple paragraphs
            big_md = "\n".join("Line " + str(i) for i in range(250))

            md2notionpage(big_md, "batch-test", "parent123", "")

            # Notion allows max 100 children per call -> expect 3 calls:
            # 100 + 100 + 50
            self.assertEqual(
                fake_notion.blocks.children.append.call_count,
                3,
                "Batching should call append() 3 times for 250 blocks",
            )


    # 4) Function must still return correct URL (API contract)

    def test_returns_url(self):
        fake_notion = MagicMock()
        fake_notion.pages.create.return_value = {"id": "abc", "url": "https://www.notion.so/test-url"}

        with patch("md2notionpage.core.notion", fake_notion):
            url = md2notionpage("hello", "title", "parent123", "")

        self.assertTrue(url.startswith("https://www.notion.so/"))


if __name__ == "__main__":
    unittest.main()
