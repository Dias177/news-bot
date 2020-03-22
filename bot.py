import telebot
import lst
import yfinance as yf
import requests
import json
from stock import Stock
from news import News
from constants import BOT_TOKEN, WEATHER_ID, WEATHER_URL, CURRENCY_URL, CORONA_URL, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from datetime import date, datetime
import mysql.connector

bot = telebot.TeleBot(BOT_TOKEN)
today = date.today()
today_modified = today.strftime("%B %d, %Y")

@bot.message_handler(commands=['start'])
def send_start(message):
    user_id = message.chat.id
    
    msg = "Hey! I'm NewsBot.\n\nI'm here to help you keep up to date with the latest events (news, stocks, COVID-19, etc.)\
 in the world and in Kazakhstan.\n\nPlease refer to /help to see the list of all available commands.\n\n"
    inline_markup = telebot.types.InlineKeyboardMarkup()

    mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            database=DB_NAME
    )
    mycursor = mydb.cursor()

    mycursor.execute(f'SELECT * FROM user WHERE user_id={user_id}')
    res = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    if not res:
        itembtnyes = telebot.types.InlineKeyboardButton('Yes', callback_data='start_yes')
        itembtnno = telebot.types.InlineKeyboardButton('No', callback_data='start_no')
        inline_markup.row(itembtnyes, itembtnno)
        msg = f'{msg}Would you like to receive daily reports?'
    else:
        msg = f'{msg}Take care!'
    
    bot.send_message(message.chat.id, msg, reply_markup=inline_markup)

@bot.callback_query_handler(lambda query: query.data in ['start_yes', 'start_no'])
def notification_handler(query):
    user_id = query.from_user.id
    first_name = query.from_user.first_name
    last_name = query.from_user.last_name
    username = query.from_user.username
    registration_date = datetime.now()
    send = 0 if query.data == 'start_no' else 1

    mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            database=DB_NAME
    )
    mycursor = mydb.cursor()
    sql = "INSERT INTO user (user_id, first_name, last_name, username, registration_date, send, send_at)\
        VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (user_id, first_name, last_name, username, registration_date, send, 'NULL')
    mycursor.execute(sql, values)
    mydb.commit()
    mycursor.close()
    mydb.close()

    new_msg = query.message.text
    new_msg = '\n\n'.join(new_msg.split('\n\n')[:-1])
    new_msg = f'{new_msg}\n\nTake care!'
    bot.edit_message_text(text=new_msg, chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=None)

    bot.answer_callback_query(query.id, 'Your preference is saved.')

@bot.message_handler(commands=['help'])
def send_help(message):
    msg = "<b>List of available commands</b>\n\n/stocks - get stock prices from KASE, NASDAQ and NYSE\n\
/news - get main news\n/weather - get current temperature\n/currency - get exchange rates\n\
/corona - get stats about COVID-19\n/settings - change your settings"
    bot.send_message(message.chat.id, msg, parse_mode='HTML')

@bot.message_handler(commands=['settings'])
def send_settings(message):
    rep = "<b>Your Settings</b>\n\n"
    user_id = message.chat.id
    mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            database=DB_NAME
    )
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT * FROM user WHERE user_id={user_id}')
    res = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    send = 'Yes' if res[-2] == 1 else 'No'
    rep += f'Send daily reports? <b>{send}</b>\n\nWould you like to change your current settings?'
    inline_markup = telebot.types.InlineKeyboardMarkup()
    itembtnyes = telebot.types.InlineKeyboardButton('Yes', callback_data='settings_yes')
    itembtnno = telebot.types.InlineKeyboardButton('No', callback_data='settings_no')
    inline_markup.row(itembtnyes, itembtnno)
    bot.send_message(message.chat.id, rep, parse_mode='HTML', reply_markup=inline_markup)

@bot.callback_query_handler(lambda query: query.data in ['settings_yes', 'settings_no'])
def settings_handler(query):
    if query.data == 'settings_yes':
        user_id = query.from_user.id

        mydb = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                passwd=DB_PASSWORD,
                database=DB_NAME
        )
        mycursor = mydb.cursor()

        mycursor.execute(f'SELECT * FROM user WHERE user_id={user_id}')
        res = mycursor.fetchone()
        send_old = res[-2]
        send_new = 0 if send_old == 1 else 1

        sql = "UPDATE user SET send = %s WHERE user_id = %s"
        values = (send_new, user_id)
        mycursor.execute(sql, values)
        mydb.commit()
        mycursor.close()
        mydb.close()

        bot.answer_callback_query(query.id, 'Your settings are updated.')
        new_msg = "<b>Your Settings</b>\n\n"
        send = 'Yes' if send_new == 1 else 'No'
        new_msg += f'Send daily reports? <b>{send}</b>'
        bot.edit_message_text(text=new_msg, chat_id=query.message.chat.id, message_id=query.message.message_id, parse_mode='HTML')
    else:
        bot.answer_callback_query(query.id, 'Your settings are updated.')

@bot.message_handler(commands=['stocks'])
def send_stocks(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    
    itembtnkz = telebot.types.KeyboardButton('Kazakhstan Stock Exchange (KASE)')
    itembtnus = telebot.types.KeyboardButton('American Stock Markets (NYSE, NASDAQ, etc.)')
    markup.row(itembtnkz, itembtnus)
    msg = bot.send_message(message.chat.id, "Please choose", reply_markup=markup)
    bot.register_next_step_handler(msg, stocks_handler)

@bot.message_handler(commands=['news'])
def send_news(message):
    news = News()
    news.find_supermain()
    msg = f"<b>Main News on <a href=\"https://www.zakon.kz/\">zakon.kz</a> for {today_modified}</b>\n\n"
    msg += f'<a href="{news.url}">{news.title}</a>\n\n'
    for i in range(4):
        news.find_main(i)
        msg += f"<a href=\"{news.url}\">{news.title}</a>\n\n"
    bot.send_message(message.chat.id, msg, parse_mode='HTML')

@bot.message_handler(commands=['weather'])
def send_weather(message):
    msg = bot.send_message(message.chat.id, "Please enter a city")
    bot.register_next_step_handler(msg, weather_handler)

@bot.message_handler(commands=['currency'])
def send_currency(message):
    response = requests.get(CURRENCY_URL)
    if response.status_code == 200:
        data = response.json()
        msg = f"<b>Exchange Rates as of {today_modified}</b>\n\n"
        msg += f"USD: {data['USD']}\nEUR: {data['EURO']}\nRUB: {data['RUB']}"
        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Cannot get data')

@bot.message_handler(commands=['corona'])
def send_corona(message):
    response = requests.get(CORONA_URL)
    if response.status_code == 200:
        data = response.json()
        msg = f'<b>Statistics as of {today_modified}</b>\n\n'
        msg += f'Global cases: {data["cases_global"]}\n'
        msg += f'Global deaths: {data["deaths_global"]}\n'
        msg += f'Global recovered: {data["recovered_global"]}\n\n'
        msg += f'Kazakhstan cases: {data["cases_kz"]}\n'
        msg += f'Kazakhstan deaths: {data["deaths_kz"]}\n'
        msg += f'Kazakhstan recovered: {data["recovered_kz"]}'
        bot.send_message(message.chat.id, msg, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Cannot get data')

@bot.message_handler(func=lambda message: True)
def send_any(message):
    bot.send_message(message.chat.id, 'Unrecognized command. Please refer to /help')

def stocks_handler(message):
    if message.text == 'Kazakhstan Stock Exchange (KASE)':
        top_ten_stocks = lst.most_liquid()
        stocks = []
        for stock in top_ten_stocks:
            temp = Stock(stock)
            temp.find_price()
            stocks.append(str(temp))

        temp = '\n'.join(stocks)
        msg = f"<b>Top 10 Most Liquid Shares on KASE for {today_modified}</b>\n\n" + temp
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
        temp = response_json['main']['temp']
        bot.send_message(message.chat.id, f'Current temperature in {message.text.capitalize()}: {temp}°C')
    else:
        bot.send_message(message.chat.id, 'Cannot find weather for this city!')
    
bot.polling()