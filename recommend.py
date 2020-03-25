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

def recommend(user_id):
    data = get_data(user_id)
    corpus, y = [], []
    for row in data:
        news_title = row[1]
        is_interested = row[-2]
        preprocessed_news_title = preprocess_text(news_title)
        corpus.append(preprocessed_news_title)
        y.append(is_interested)
    
    cv = CountVectorizer(max_features = 1500)
    X = cv.fit_transform(corpus).toarray()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 0)

    classifier = GaussianNB()
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

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