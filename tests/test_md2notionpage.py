
import unittest
from md2notionpage import md2notionpage
import os

class TestMd2NotionPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['NOTION_SECRET'] = 'your-secret-token'

    def test_create_notion_page_from_md(self):
        markdown_text = "# Otsikko 1\n## Alaotsikko 1.1\n### Alaotsikko 1.1.1\nTämä on tavallinen kappale, joka sisältää **lihavoitua** ja *kursivoitua* tekstiä.\n- Luettelomerkit\n  - Alaluettelo\n- Toinen kohta\n1. Numeroitu luettelo\n   1. Alaluettelo\n2. Toinen kohta\n[Linkki](https://www.example.com)\nTässä on koodiesimerkki:\n    def hello_world():\n        print("Hello, world!")\n> Lainaus\nTaulukko:\n| Sarake 1 | Sarake 2 | Sarake 3 |\n|----------|----------|----------|\n| Sisältö  | Sisältö  | Sisältö  |\n---\nVaakaviiva\n![Kuvateksti](https://www.example.com/image.jpg)\nTämä on monipuolinen esimerkki, joka sisältää useimmat yleiset Markdown-elementit."
        title = "Test Notion Page"
        parent_page_id = "YOUR_PARENT_PAGE_ID" # Replace with actual parent_page_id

        # Call the md2notionpage function
        notion_page_url = md2notionpage(markdown_text, title, parent_page_id)

        # Check that the returned URL is valid (this depends on how the function is implemented)
        self.assertIsNotNone(notion_page_url)
        self.assertTrue(notion_page_url.startswith('https://www.notion.so/'))

if __name__ == '__main__':
    unittest.main()
