
import unittest
from md2notionpage import md2notionpage
from dotenv import load_dotenv

class TestMd2NotionPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_create_notion_page_from_md(self):
      
        markdown_text = "# Otsikko 1\n## Alaotsikko 1.1\n### Alaotsikko 1.1.1\nTämä on tavallinen kappale, joka sisältää **lihavoitua** ja *kursivoitua* tekstiä.\n- Luettelomerkit\n  - Alaluettelo\n- Toinen kohta\n1. Numeroitu luettelo\n   1. Alaluettelo\n2. Toinen kohta\n[Linkki](https://www.example.com)\nTässä on koodiesimerkki:\n    def hello_world():\n        print('Hello, world!')\n> Lainaus\nTaulukko:\n| Sarake 1 | Sarake 2 | Sarake 3 |\n|----------|----------|----------|\n| Sisältö  | Sisältö  | Sisältö  |\n---\nVaakaviiva\n![Kuvateksti](https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg)\nTämä on monipuolinen esimerkki, joka sisältää useimmat yleiset Markdown-elementit."
        
        title = "Test Notion Page"
        
        parent_page_id = "f756bd310b5a458396e059fec9f58bda" # Replace with actual parent_page_id

        cover_url = "https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg"
        
        # Call the md2notionpage function
        notion_page_url = md2notionpage(markdown_text, title, parent_page_id, cover_url)

        # Check that the returned URL is valid (this depends on how the function is implemented)
        self.assertIsNotNone(notion_page_url)
        self.assertTrue(notion_page_url.startswith('https://www.notion.so/'))

if __name__ == '__main__':
    unittest.main()
