import webview
from bs4 import BeautifulSoup
import cloudscraper
import pprint
import json
from pathlib import Path

baseurl = "https://www.anime-planet.com/"


class Api:
    def __init__(self):
        self.pending_download = None

    def fetch(self):
        url = "https://www.anime-planet.com/manga/read-online/"

        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        grid = soup.find("ul", class_="cardDeck")

        gimgs = grid.select("ul > li.card > a.tooltip > div.crop > img")
        gref = grid.select("ul > li.card > a.tooltip")

        for i in range(0, 10):
            imgUrl = gimgs[i]["data-src"]
            fullHref = baseurl + gref[i]["href"].lstrip('/')
            title = gimgs[i]["alt"]
            jsCall = f"window.buildMangaInfo({json.dumps(title)},{json.dumps(imgUrl)},{json.dumps(fullHref)})"
            window.evaluate_js(jsCall)

    def getChapters(self, imgUrl, url, mangaName):
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        grid = soup.find("ul", class_="cardDeck")
        chapter = soup.find_all("h3", class_="cardName")
        chapterNames = [item.get_text(strip=True) for item in chapter]

        hrefs = grid.select("ul > li.card > a")
        downloadLinks = [item.get("href") for item in hrefs]

        #guarda os dados temporariamente os dados para que a próxima página "download.html" obtenha eles com segurança
        self.pending_download = {
            "chapters": chapterNames,
            "img": imgUrl,
            "title": mangaName,
            "downloadLinks": downloadLinks,
        }

        return download_file.as_uri()#agora a mudança de pagina é feita através do js

    def getPendingDownloadData(self):
        return self.pending_download

    def downloadFile(self,link):
        print(link)


api = Api()
base = Path(__file__).resolve().parent.parent
index_file = base / "assets" / "index.html"
download_file = base / "assets" / "download.html"
window = webview.create_window("Mango", index_file.as_uri(), js_api=api)
webview.start()

