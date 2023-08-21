from inspect import getsourcefile
from os.path import abspath


# print('/'.join(abspath(getsourcefile(lambda:0)).split('/')[:-1]))

import pandas as pd
import sqlite3
from functions.sql_functions import sql_connect
import logging

logger = logging.getLogger(__name__)
sql_con = sql_connect('orders', logger)

# import datetime as dt

df = sql_con.get_all_orders()
# # df = df[df['stage']=='accepted_deliverman']
# # df['last_change'] = pd.to_datetime(df['last_change'])
# # df['current_time'] = dt.datetime.now()
# # df['time_delta'] = df['current_time'] - df['last_change']
# # df['time_delta'] = df['time_delta'].apply(lambda x: x.seconds)
# # df = df[df['time_delta'] > 10]
# # records = df.to_dict('records')
# # records
df.to_csv('test.csv')

# con = sqlite3.connect(f'database/orders.db')
# cur = con.cursor()
# # # query = "DELETE FROM orders WHERE track_num = 'qq';"
# # # # query = "SELECT count(*)  FROM orders WHERE track_num = 'qq';"
# # # cur.execute(query)

# query = "SELECT track_num  FROM orders WHERE track_num = 'qq';"
# # query = "DELETE FROM orders WHERE track_num = 'qq';"
# data = cur.execute(query)
# [print(row) for row in cur.fetchall()]

# cur.close()

#test50 test56 test57 test58


# conn=sqlite3.connect('database/orders.db')
# curs=conn.cursor()
# curs.execute("DELETE  FROM orders WHERE track_num = 'test58';")
# conn.commit()
# conn.close()