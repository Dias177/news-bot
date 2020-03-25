from urllib.request import urlopen
from bs4 import BeautifulSoup

main_url = "https://www.zakon.kz/"
page = urlopen(main_url)
soup = BeautifulSoup(page, "html.parser")

class News:

    def __init__(self):
        self.title = "No title"
        self.url = "No URL"

    def find_supermain(self):
        title = soup.find("div", attrs={"class": "super_main"})
        title = title.text.strip()

        url = main_url + soup.find("div", attrs={"class": "super_main"}).find_all('a')[0].get('href')

        self.url = url
        self.title = title

    def find_main(self, i):

        title = soup.find("div", attrs={"class": "main_list"}).find_all('a')[i]
        title = title.text.strip()

        while title[-1] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            title = title[:-1]

        url = main_url + soup.find("div", attrs={"class": "main_list"}).find_all('a')[i].get('href')

        self.url = url
        self.title = title

    def find_news(self, i):
        last_feed = soup.find("div", attrs={"class": "last_feed"})
        all_a = last_feed.find_all('a')
        if i < len(all_a):
            title = all_a[i].get_text()[5:]
            while title[-1] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                title = title[:-1]
            url = main_url + all_a[i].get('href')
            self.title = title
            self.url = url
        return None

    def __repr__(self):
        return f"{self.title} {self.url}"

    def __str__(self):
        return f"Title: {self.title}\nURL: {str(self.url)}"