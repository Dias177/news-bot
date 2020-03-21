from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


def most_liquid():
    url = 'http://kase.kz/ru/shares/'
    lst = []
    i = 0

    soup = BeautifulSoup(urlopen(url), 'html.parser')

    tickers = soup.find_all(href=re.compile("/ru/shares/show/"))

    for x in tickers:
        x = x.text.strip()
        lst.append(x)
        i = i + 1
        if (i == 10):
            break
    return lst
