import telebot
import lst
import yfinance as yf
import requests
import json
from stock import Stock
from news import News
from constants import BOT_TOKEN, WEATHER_ID, WEATHER_URL, CURRENCY_URL, CORONA_URL
from datetime import date

bot = telebot.TeleBot(BOT_TOKEN)
today = date.today().strftime("%B %d, %Y")

@bot.message_handler(commands=['stocks'])
def send_stocks(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    itembtnkz = telebot.types.KeyboardButton('Kazakhstan Stock Exchange (KASE)')
    itembtnus = telebot.types.KeyboardButton('American Stock Markets (NYSE, NASDAQ, etc.)')
    markup.row(itembtnkz, itembtnus)
    msg = bot.reply_to(message, "Please choose", reply_markup=markup)
    bot.register_next_step_handler(msg, stocks_handler)

@bot.message_handler(commands=['news'])
def send_news(message):
    news = News()
    news.find_supermain()
    msg = f"<b>Main News on <a href=\"https://www.zakon.kz/\">zakon.kz</a> for {today}</b>\n\n"
    msg += f'<a href="{news.url}">{news.title}</a>\n\n'
    for i in range(4):
        news.find_main(i)
        msg += f"<a href=\"{news.url}\">{news.title}</a>\n\n"
    bot.reply_to(message, msg, parse_mode='HTML')

@bot.message_handler(commands=['weather'])
def send_weather(message):
    msg = bot.reply_to(message, "Please enter a city")
    bot.register_next_step_handler(msg, weather_handler)

@bot.message_handler(commands=['currency'])
def send_currency(message):
    response = requests.get(CURRENCY_URL)
    if response.status_code == 200:
        data = response.json()
        msg = f"<b>Exchange Rates as of {today}</b>\n\n"
        msg += f"USD: {data['USD']}\nEUR: {data['EURO']}\nRUB: {data['RUB']}"
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, 'Cannot get data')

@bot.message_handler(commands=['corona'])
def send_corona(message):
    response = requests.get(CORONA_URL)
    if response.status_code == 200:
        data = response.json()
        msg = f'<b>Statistics as of {today}</b>\n\n'
        msg += f'Global cases: {data["cases_global"]}\n'
        msg += f'Global deaths: {data["deaths_global"]}\n'
        msg += f'Global recovered: {data["recovered_global"]}\n\n'
        msg += f'Kazakhstan cases: {data["cases_kz"]}\n'
        msg += f'Kazakhstan deaths: {data["deaths_kz"]}\n'
        msg += f'Kazakhstan recovered: {data["recovered_kz"]}\n'
        bot.reply_to(message, msg, parse_mode='HTML')
    else:
        bot.reply_to(message, 'Cannot get data')

@bot.message_handler(func=lambda message: True)
def send_any(message):
    bot.reply_to(message, 'Unrecognized command. Please refer to /help')

def stocks_handler(message):
    if message.text == 'Kazakhstan Stock Exchange (KASE)':
        top_ten_stocks = lst.most_liquid()
        stocks = []
        for stock in top_ten_stocks:
            temp = Stock(stock)
            temp.find_price()
            stocks.append(str(temp))

        temp = '\n'.join(stocks)
        msg = f"<b>Top 10 Most Liquid Shares on KASE for {today}</b>\n\n" + temp
        bot.send_message(message.chat.id, msg, parse_mode='HTML')

    elif message.text == 'American Stock Markets (NYSE, NASDAQ, etc.)':
        tickers = ['^GSPC', '^DJI', 'AAPL', 'AMZN', 'MSFT', 'TSLA', 'FB', 'GOOGL', 'BABA', 'DIS', 'JPM', 'BA']
        stocks = []
        for ticker in tickers:
            temp = yf.Ticker(ticker)
            stocks.append(f'{ticker}: {temp.history()["Close"][-1]} USD')

        temp = '\n'.join(stocks)
        bot.send_message(message.chat.id, temp)

    else:
        bot.send_message(message.chat.id, 'Unexpected input. Try again!')

def weather_handler(message):
    response = requests.get(f'{WEATHER_URL}?q={message.text}&appid={WEATHER_ID}&units=metric')
    response_json = response.json()
    if response_json['cod'] == 200:
        bot.send_message(message.chat.id, response_json['main']['temp'])
    else:
        bot.send_message(message.chat.id, 'Cannot find weather for this city!')

bot.polling()