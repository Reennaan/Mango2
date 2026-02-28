import webview
from bs4 import BeautifulSoup
import cloudscraper
import pprint
import json
from pathlib import Path



class Api:

    def fetch(self):
        baseurl = "https://www.anime-planet.com/"
        url = "https://www.anime-planet.com/manga/read-online/"

        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)

        #print("Status:", response.status_code)
        #print(response.text[:500])
        soup = BeautifulSoup(response.text, 'html.parser')
        grid = soup.find("ul", class_="cardDeck")
        #pprint.pprint(grid)


        #names = grid.select("h3", class_="cardName")
        gimgs = grid.select("ul > li.card > a.tooltip > div.crop > img")
        gref = grid.select("ul > li.card > a.tooltip")

        for i in range(0,10):
            #print(names[i].text)
            imgUrl = gimgs[i]["data-src"]
            fullHref = baseurl + gref[i]["href"].lstrip('/') 
            title = gimgs[i]["alt"]
            #print(imgUrl)
            #self.buildMangaInfo(title,imgUrl,fullHref)
            window.evaluate_js(f"""window.buildMangaInfo({json.dumps(title)},{json.dumps(imgUrl)},{json.dumps(fullHref)})""")

            
    def mangaDownloadPage(self,imgUrl,url):
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        chapter = soup.find_all("h3", class_="cardName")
        pprint.pprint(chapter)




api = Api()
base = Path(__file__).resolve().parent.parent
index_file = base / "assets" / "index.html"
window = webview.create_window("Mango", index_file.as_uri(), js_api=api)
webview.start()

