import numpy as np
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation
import pandas as pd
import matplotlib.pyplot as plt
from constants import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
import mysql.connector
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from news import News

def recommend(user_id, news, num_news):
    data = get_data(user_id)
    if data:
        corpus, y = [], []
        for row in data:
            news_title = row[1]
            is_interested = row[-2]
            preprocessed_news_title = preprocess_text(news_title)
            corpus.append(preprocessed_news_title)
            y.append(is_interested)
        
        for n in news:
            preprocessed_news_title = preprocess_text(n)
            corpus.append(preprocessed_news_title)
        
        cv = CountVectorizer(max_features = 1000)
        X = cv.fit_transform(corpus).toarray()
        classifier = GaussianNB()
        classifier.fit(X[:-num_news], y)
        y_pred = classifier.predict(X[-num_news:])
        
        return y_pred
    else:
        return None

def preprocess_text(text):
    mystem = Mystem() 
    russian_stopwords = stopwords.words("russian")
    text = re.sub('[^а-яА-я]', ' ', text)
    tokens = mystem.lemmatize(text.lower())
    
    tokens = [token for token in tokens if token not in set(russian_stopwords)\
              and token != " " \
              and token.strip() not in punctuation]
    
    text = " ".join(tokens)
    return text

def get_data(user_id):
    try:
        mydb = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                passwd=DB_PASSWORD,
                database=DB_NAME
        )
        mycursor = mydb.cursor()

        mycursor.execute(f'SELECT * FROM news WHERE user_user_id={user_id}')
        res = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        return res
    except:
        return None