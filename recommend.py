import numpy as np
import re
import pandas as pd
import matplotlib.pyplot as plt
from constants import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
import mysql.connector

def recommend(user_id):
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
    X, y = [], []
    for r in res:
        X.append(r[1])
        y.append(r[3])
    print(X)
    print(y)

if __name__ == '__main__':
    user_id = 392971432
    recommend(user_id)


