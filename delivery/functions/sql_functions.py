import sqlite3
import pandas as pd
from aiogram.types.user import User
from datetime import datetime

class sql_connect:
    def __init__(self, db_name, logger) -> None:
        self.con = sqlite3.connect(f'database/{db_name}.db')
        self.cur = self.con.cursor()
        self.logger = logger
        self.create_orders_table()
        

    def create_orders_table(self) -> None:
        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS orders(
            track_num TEXT PRIMARY KEY,
            country TEXT,
            address TEXT,
            pass TEXT,
            descriprion TEXT,
            price TEXT,
            path_image TEXT,
            stage TEXT,
            last_change TEXT,
            manager_id TEXT,
            manager_name TEXT,
            warehouser_id TEXT,
            warehouser_name TEXT,
            warehouse_messageid TEXT,
            delivery_group_messageid TEXT,
            deliveryman_id TEXT,
            deliveryman_name TEXT,
            delivery_private_messageid);
            """)
        self.con.commit()

    def add_new_order(self, data: tuple) -> None:
        # print("DATA", data)
        self.cur.execute("INSERT INTO orders (track_num, country , address , pass , descriprion , price , path_image, stage, last_change, manager_id, manager_name) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", data)
        self.con.commit()


        # message.from_user.username 
        #message.from_user.first_name + '_' + (message.from_user.last_name if message.from_user.last_name != None else '')
        


    def get_order(self, track: str) -> tuple:
        res = self.cur.execute(f"SELECT * FROM orders WHERE track_num = '{track}'")
        res = res.fetchone()
        if res != None:
            order = {}
            for n, name in enumerate(self.table_names('orders')):
                order[name] = res[n]
            return order
        else:
            return res

    def modify_order(self, track: str, col:str, val: str) -> None:
        query = f"UPDATE orders SET {col} = '{val}' WHERE track_num = '{track}';"
        self.cur.execute(query)
        self.con.commit()
        query = f"UPDATE orders SET last_change = '{str(datetime.now())}' WHERE track_num = '{track}';"
        self.cur.execute(query)
        self.con.commit()
        

    def add_cat_to_user(self, user: str, cat: str) -> None:
        query = f"UPDATE users SET category = '{cat}' WHERE userid = {user};"
        self.cur.execute(query)
        self.con.commit()

    def table_names(self, table:str) -> list:
        res = self.cur.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{table}');")
        names = []
        for t in res.fetchall():
            names.append(t[0])
        return names
    
    def get_all_orders(self) -> pd.DataFrame:
        res = self.cur.execute(f"SELECT * FROM orders")# WHERE userid = {user_id}
        res = res.fetchall()
        df = pd.DataFrame.from_records(res)
        df.columns = self.table_names('orders')
        return df