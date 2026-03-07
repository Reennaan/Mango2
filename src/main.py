import webview
from bs4 import BeautifulSoup
import cloudscraper
import pprint
import json
from pathlib import Path
import os
import re
import time
import sys
import img2pdf
from ebooklib import epub
from providers.weebcentral import WeebCentral
from providers.animeplanet import AnimePlanet

baseurl = "https://www.anime-planet.com/"
scraper = cloudscraper.create_scraper()
currentFolder = "../downloads"
downloadFormat = "JPG"
if getattr(sys, "frozen", False):
    RESOURCE_BASE = Path(getattr(sys, "_MEIPASS"))
    APP_BASE = Path(sys.executable).resolve().parent
else:
    RESOURCE_BASE = Path(__file__).resolve().parent.parent
    APP_BASE = RESOURCE_BASE


class Api:
    def __init__(self):
        self.pending_download = None
        self.currentFolder = currentFolder
        self.downloadFormat = downloadFormat   
        self.settings_file = APP_BASE / ".settings.json"
        self.providers ={
            "Weeb Central": WeebCentral(),
            "Anime Planet": AnimePlanet()
        }
        
        self.currentProvider = self.providers["Weeb Central"]
        self._load_settings()

    def _load_settings(self):
        if not self.settings_file.exists():
            return
        try:
            data = json.loads(self.settings_file.read_text(encoding="utf-8"))
            saved_folder = data.get("currentFolder")
            if isinstance(saved_folder, str) and saved_folder.strip():
                self.currentFolder = saved_folder
        except Exception as e:
            print(f"failed to load settings: {e}")

    def _save_settings(self):
        try:
            data = {"currentFolder": self.currentFolder}
            self.settings_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"failed to save settings: {e}")


    def changeProvider(self, name):
        if  name in self.providers:
            self.currentProvider = self.providers[f"{name}"]

    def changeFormat(self,name):
            self.downloadFormat = name 

    def genericFetch(self):
        mangas = self.currentProvider.fetch_home()
        for i in range(0,10):
            jsCall = f"window.buildMangaInfo({json.dumps(mangas[i]['title'])},{json.dumps(mangas[i]['cover'])},{json.dumps(mangas[i]['link'])})"
            window.evaluate_js(jsCall)

    def search_mango(self,name):
        mangas = self.currentProvider.search_mango(name)
        print(len(mangas))
        for item in mangas:
            jsCall = f"window.buildMangaInfo({json.dumps(item['title'])},{json.dumps(item['cover'])},{json.dumps(item['link'])}), changeShowText('Results:')"
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
        pageList = self.currentProvider.get_pages(chapterLink);
        


        headers = {
        "Referer": chapterLink, 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

        local_scraper = cloudscraper.create_scraper()

        filterChar = r'[<>:"/\\|?*]'
        filteredName = re.sub(filterChar, "_",name)
        filteredChapter = re.sub(filterChar, "_", chapter)


        basePath = self.currentFolder
        folderName = f"{filteredName}{filteredChapter}"
        fullPath = os.path.join(basePath,folderName)

        os.makedirs(fullPath, exist_ok=True)

        if self.downloadFormat == "PDF":
            self.downloadPDF(headers,folderName,fullPath,pageList)
        elif self.downloadFormat == "EPUB":
            self.downloadEPUB(headers,folderName,fullPath,pageList)
        else:
            for i, item in enumerate(pageList):
                print(f"baixando pagina {i}")
                images = local_scraper.get(item, headers=headers)
                filePath = os.path.join(fullPath,f"{i+1}.jpg")
                time.sleep(1)
                with open(filePath, "wb") as f:
                    f.write(images.content)

            return ""
    

    def downloadPDF(self, headers,folderName, fullPath, pageList):
        local_scraper = cloudscraper.create_scraper()
        imageBytes = []

        for i, item in enumerate(pageList):
            print(f"baixando pagina {i} PDF")
            images = local_scraper.get(item, headers=headers)
            time.sleep(1)
            imageBytes.append(images.content)

        with open(os.path.join(fullPath,f"{folderName}.pdf"), "wb") as f:
            f.write(img2pdf.convert(*imageBytes))

        return "baixei em pdf"

    def downloadEPUB(self, headers, folderName, fullPath, pageList):
        local_scraper = cloudscraper.create_scraper()

        book = epub.EpubBook()
        book.set_identifier(folderName)
        book.set_title(folderName)
        book.set_language("pt-BR")
        chapter = epub.EpubHtml(title=folderName, file_name="chapter.xhtml", lang="pt-BR")
        chapterContent = [f"<h1>{folderName}</h1>"]

        for i, item in enumerate(pageList):
            print(f"baixando pagina {i} EPUB")
            images = local_scraper.get(item, headers=headers)
            imgName = f"image_{i+1}.jpg"
            img = epub.EpubItem(
                uid=f"img_{i+1}",
                file_name=imgName,
                media_type="image/jpeg",
                content=images.content
            )
            book.add_item(img)
            chapterContent.append(f'<p><img src="{imgName}" alt="page {i+1}" /></p>')
            time.sleep(1)

        chapter.content = "".join(chapterContent)
        book.add_item(chapter)
        book.toc = (epub.Link("chapter.xhtml", folderName, "chapter"),)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ["nav", chapter]

        epub.write_epub(os.path.join(fullPath, f"{folderName}.epub"), book, {})

        return "baixei em EPUB"    


    def getPendingDownloadData(self):
        return self.pending_download
        
    
 

    def selectFolder(self):
        
        folder = window.create_file_dialog(webview.FileDialog.FOLDER)
        if folder:
            self.currentFolder = folder[0] if isinstance(folder, (list, tuple)) else folder
            self._save_settings()
            print(f"current folder: {self.currentFolder}")
            return self.currentFolder
        return None     
    




api = Api()
index_file = RESOURCE_BASE / "assets" / "index.html"
icon_file = RESOURCE_BASE / "img" / "icon.jpg"
window = webview.create_window("Mango", index_file.as_uri(), js_api=api, width=1280 ,height=720) 
webview.start(getattr(sys, "frozen", False), icon=str(icon_file), debug=True)
