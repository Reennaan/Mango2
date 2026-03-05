import webview
from bs4 import BeautifulSoup
import cloudscraper
import pprint
import json
from pathlib import Path
import os
import re
import time
from providers.weebcentral import WeebCentral
from providers.animeplanet import AnimePlanet

baseurl = "https://www.anime-planet.com/"
scraper = cloudscraper.create_scraper()
currentFolder = "../downloads"


class Api:
    def __init__(self):
        self.pending_download = None
        self.currentFolder = currentFolder
        self.providers ={
            "Weeb Central": WeebCentral(),
            "Anime Planet": AnimePlanet()
        }

        self.currentProvider = self.providers["Weeb Central"]


    def changeProvider(self, name):
        if  name in self.providers:
            self.currentProvider = self.providers[f"{name}"]



    def genericFetch(self):
        mangas = self.currentProvider.fetch_home()
        for i in range(0,10):
            jsCall = f"window.buildMangaInfo({json.dumps(mangas[i]['title'])},{json.dumps(mangas[i]['cover'])},{json.dumps(mangas[i]['link'])})"
            window.evaluate_js(jsCall)



    def genericGetDetails(self, img, mangalink, mangaName):
        details = self.currentProvider.get_details(mangalink)
        mangas = details[0] if details else {}
        
        self.pending_download = {
            "chapters": mangas.get("chapters", []),
            "img": img,
            "title": mangaName,
            "author": mangas.get("author", ""),
            "downloadLinks": mangas.get("chaptersLinks", []),
            "desc": mangas.get("desc", "")

        }
        #print(self.pending_download)
        return True
    

    def genericDownload(self,chapterLink,chapter,name):
        print(chapterLink)

        pageList = self.currentProvider.get_pages(chapterLink);
        
        #print(pageList)


        headers = {
        "Referer": chapterLink, 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

        local_scraper = cloudscraper.create_scraper()

        filterChar = r'[<>:"/\\|?*]'
        filteredName = re.sub(filterChar, "_",name)
        filteredChapter = re.sub(filterChar, "_", chapter)


        basePath = self.currentFolder
        folderName = f"{filteredName}-Chapter-{filteredChapter}"
        fullPath = os.path.join(basePath,folderName)

        os.makedirs(fullPath, exist_ok=True)

        for i, item in enumerate(pageList):
            print(f"baixando pagina {i}")
            images = local_scraper.get(item, headers=headers)
            filePath = os.path.join(fullPath,f"{i+1}.jpg")
            if self.currentProvider == "Anime Planet": time.sleep(1)
            with open(filePath, "wb") as f:
                f.write(images.content)


        return ""
    


    def getPendingDownloadData(self):
        return self.pending_download
        
    


    def selectFolder(self):
        
        folder = window.create_file_dialog(webview.FileDialog.FOLDER)
        if folder:
            self.currentFolder = folder[0] if isinstance(folder, (list, tuple)) else folder
            print(f"current foolder: {self.currentFolder}")
            return self.currentFolder
        return None     
    




api = Api()
base = Path(__file__).resolve().parent.parent
index_file = base / "assets" / "index.html"
download_file = base / "assets" / "download.html"
window = webview.create_window("Mango", index_file.as_uri(), js_api=api, width=1280 ,height=720)
webview.start(debug=True)
