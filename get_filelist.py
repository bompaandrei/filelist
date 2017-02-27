"""
### Work in progress ###
Script that will get everything from filelist. Torrent names, IDs for downloads,
time of upload... and will do a lot of automatic tasks.
TO DO:
    - Get ID, torrent name and time / date without using regex [DONE]
    - Get Seeders and Leechers
    - Use a temporary file for filelist data
    - Sort the torrents by time / date
    - Search for best torrent that could be used to increase the ratio
    - Search and auto download wanted torrents
    - Send e-mails with new torrents
"""
import requests
import json
from bs4 import BeautifulSoup


class RetrieveFilelist(object):
    """
    Class used for getting data from Filelist.ro
    """

    def __init__(self):
        self.credentials = json.load(open("credentials"))
        self.session = requests.Session()
        self.torrents = {}

    def do_login(self):
        """
        Method that will do the login on filelist.ro
        """
        self.session.headers.update({"User-Agent": \
            "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"})
        self.session.get("http://filelist.ro")
        set_cookie = self.session.cookies.get_dict()
        uid = "__cfduid={}".format(set_cookie['__cfduid'])
        phpsession = "PHPSESSID={}".format(set_cookie['PHPSESSID'])
        cookie = "{}; {}".format(uid, phpsession)
        self.session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        self.session.headers.update({"Cookie": cookie})
        self.session.post("http://filelist.ro/takelogin.php", self.credentials)

    def get_torrents_data(self):
        """
        Method that will browse the pages (first 20 pages).
        This method will get the torrent names, IDs and upload time / date
        """
        for page in range(0, 1):
            if page == 0:
                url = "http://filelist.ro/browse.php"
            elif page > 0:
                url = "http://filelist.ro/browse.php?page={}".format(page)
            browse_page = self.session.get(url)
            soup = BeautifulSoup(browse_page.content, "html.parser")
            for main_div in soup.find_all("div", class_="torrentrow"):
                soup = BeautifulSoup(str(main_div), "html.parser")
                torrent_tables = [torrenttable for div in soup.find_all('div') for torrenttable in
                                  div.find_all(class_="torrenttable")]
                for content in torrent_tables[1].find_all('a'):
                    title = content.get('title')
                for content in torrent_tables[3].find_all('a'):
                    download_uri = content.get('href')
                    torrent_id = download_uri.split("=")[1].strip()
                for content in torrent_tables[5].find_all(class_="small"):
                    time_date = content.get_text()
                for content in torrent_tables[6].find_all(class_="small"):
                    size = content.get_text()
                self.torrents.update({torrent_id: {"name": title, "download_uri": download_uri, \
                                                   "upload_time": time_date, "torrent_size": size}})
        print json.dumps(self.torrents, indent=4)

TEST_CLASS = RetrieveFilelist()
TEST_CLASS.do_login()
TEST_CLASS.get_torrents_data()