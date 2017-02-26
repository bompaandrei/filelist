'''
### Work in progress ###
Script that will get everything from filelist. Torrent names, IDs for downloads,
time of upload... and will do a lot of automatic tasks.
TO DO:
    - Get ID, torrent name and time / date without using regex
    - Use a temporary file for filelist data
    - Sort the torrents by time / date
    - Search for best torrent that could be used to increase the ratio
    - Search and auto download wanted torrents
    - Send e-mails with new torrents
'''
import requests
import json
import re
from bs4 import BeautifulSoup


class RetrieveFilelist(object):
    '''
    Class used for getting data from Filelist.ro
    '''

    def __init__(self):
        self.credentials = json.load(open("credentials"))
        self.session = requests.Session()
        self.torrents = {}

    def do_login(self):
        '''
        Methot that will do the login on filelist.ro
        '''
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
        '''
        Method that will browse the pages (first 20 pages).
        This method will get the torrent names, IDs and upload time / date
        '''
        for page in range(0, 20):
            if page == 0:
                url = "http://filelist.ro/browse.php"
            elif page > 0:
                url = "http://filelist.ro/browse.php?page={}".format(page)
            browse_page = self.session.get(url)
            soup = BeautifulSoup(browse_page.content, "html.parser")
            for a_href in soup.find_all("div", class_="torrentrow"):
                a_href = str(a_href)
                title = re.findall("title=(.*?)>", a_href)[0][1:-1]
                torrent_id = re.findall("details.php\?id=(.*?)title", a_href)[0][:-2]
                time_and_date = re.findall("><nobr><font class=\"small\">(.*?)</font", a_href)[0]
                self.torrents.update({torrent_id: {"name": title, "upload_time": str(time_and_date)\
                    .replace("<br/>", " ")}})

        print json.dumps(self.torrents, indent=4)

TEST_CLASS = RetrieveFilelist()
TEST_CLASS.do_login()
TEST_CLASS.get_torrents_data()

