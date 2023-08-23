
import unittest
from md2notionpage import md2notionpage
from dotenv import load_dotenv, find_dotenv
from os import environ
from datetime import datetime

class TestMd2NotionPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv(find_dotenv())

    def test_create_notion_page_from_md(self):

        markdown_text = """
# Otsikko 1

## Alaotsikko 1.1

### Alaotsikko 1.1.1

## Tehosteet

Kappale, joka sisältää **lihavoitua** ja *kursivoitua* tekstiä.

Kappale, joka sisältää __lihavoitua__ ja _kursivoitua_ tekstiä.

Kappale, joka sisältää __*lihavoitua kursivoitua*__ tekstiä.

Kappale, joka sisältää yliviivattua ~tekstiä~ ja inline `koodia`.

Kappale, joka sisältää inline latex $x=y+1$ koodia.

## Latex

$$
x = \sqrt{y^2 + z^2}
$$

## Numeroimaton lista

- Ensimmäinen kohta
 - Alaluettelo
 - Toinen kohta
  - Ala-alaluettelo
  - Kolmas kohta
 - Neljäs kohta
- Viides kohta

## Numeroitu lista

1. Ensimmäinen kohta
 1. Alaluettelo
 2. Toinen kohta
  1. Ala-alaluettelo
  2. Kolmas kohta
 3. Neljäs kohta
2. Viides kohta

## Linkki

[https://www.example.com](https://www.example.com)

## Sisennys

Tässä on sisennetty koodiesimerkki (plain text):

    def hello_world():
        print("Hello, world!")

## Koodi

Tässä on toinen koodiesimerkki (Python):

```python
def hello_world2():
    print("Hello, world2!")
```

## Lainaus

> Lainausteksti

## Taulukko

Taulukko:

| Sarake 1 | Sarake 2 | Sarake 3 |
|----------|----------|----------|
| Sisältö  | Sisältö  | Sisältö  |

Taulukko ilman sarakenimiä:

| Sisältö 1.1 | Sisältö 2.1 | Sisältö 3.1 |
| Sisältö 1.2 | Sisältö 2.2 | Sisältö 3.2 |

## Vaakaviiva

---

## Kuva

![Kuvateksti](https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg)

![](https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg)

Tämä on monipuolinen esimerkki, joka sisältää useimmat yleiset Markdown-elementit.
"""

        # Get the current date and time
        current_time = datetime.now()

        # Format the timestamp as a string
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # Append the timestamp to the title
        title = "Test Notion Page " + timestamp_str

        parent_page_id = environ.get("NOTION_PARENT_PAGE_ID")

        cover_url = "https://raw.githubusercontent.com/markomanninen/md2notion/main/photo-1501504905252-473c47e087f8.jpeg"

        # Call the md2notionpage function
        notion_page_url = md2notionpage(markdown_text, title, parent_page_id, cover_url)

        # Check that the returned URL is valid (this depends on how the function is implemented)
        self.assertIsNotNone(notion_page_url)
        self.assertTrue(notion_page_url.startswith('https://www.notion.so/'))

if __name__ == '__main__':
    unittest.main()
