import csv
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

class Stock:

    def __init__(self, ticker):
        self.ticker = ticker
        self.price = -1

    def find_price(self):

        url = "http://kase.kz/en/shares/show/" + self.ticker + "/"
        page = urlopen(url)
        soup = BeautifulSoup(page, "html.parser")

        ticker = soup.find("h1", attrs={"style": "text-transform: none;"})
        ticker = ticker.text.strip()


        price = soup.find("div", attrs={"class": "h1-block__indicator"})
        price = price.text.strip()

        self.price = price

    def append_data(self):
        with open("stock.csv", 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([self.ticker, self.price, datetime.now()])

    def __repr__(self):
        return "{} {} kzt".format(self.ticker, self.price)

    def __str__(self):
        return f"{self.ticker}: {str(self.price)} KZT"
