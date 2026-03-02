import requests
import webview
from bs4 import BeautifulSoup
import cloudscraper
import pprint
import json
from pathlib import Path
import os

baseurl = "https://www.anime-planet.com/"
scraper = cloudscraper.create_scraper()
currentFolder = "../downloads"


class Api:
    def __init__(self):
        self.pending_download = None

    def fetch(self):
        url = "https://www.anime-planet.com/manga/read-online/"

        
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

    def downloadFile(self,slug,chapter):
        uiUrl = f"https://www.anime-planet.com/manga/{slug}/chapters/{chapter}"
        scraper.get(uiUrl)

        
        url = f"https://www.anime-planet.com/api/manga/chapter/{slug}/{chapter}"
        #print(url)
        response = scraper.get(url)
        dados = response.json()
        imagesUrl = dados["data"]["images"]
        #print(imagesUrl)

        basePath = currentFolder
        folderName = f"{slug}-Chapter-{chapter}"
        fullPath = os.path.join(basePath,folderName)

        os.makedirs(fullPath, exist_ok=True)

        
        for i, item in enumerate(imagesUrl):
            print(f"baixando pagina {i}")
            images = scraper.get(item, headers={"Referer":uiUrl})
            filePath = os.path.join(fullPath,f"{i+1}.jpg")
            with open(filePath, "wb") as f:
                f.write(images.content)

        #print(dados["data"]["images"])
        
    def selectFolder():
        folder = window.create_file_dialog(webview.FOLDER_DIALOG)
        currentFolder = folder        



api = Api()
base = Path(__file__).resolve().parent.parent
index_file = base / "assets" / "index.html"
download_file = base / "assets" / "download.html"
window = webview.create_window("Mango", index_file.as_uri(), js_api=api, width=1280 ,height=720)
webview.start(api.fetch,debug=True)

