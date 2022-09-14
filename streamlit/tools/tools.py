import streamlit as st
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import *
import pandas as pd

def calc(begin, body_of_credit, raid, number_of_periods):
    last_payment = begin + relativedelta(months=+number_of_periods)
    monthly_raid = raid / 12 / 100
    general_raid = (1 + monthly_raid) ** number_of_periods
    monthly_payment = round((body_of_credit * monthly_raid * general_raid / (general_raid - 1)), 2)
    return last_payment, monthly_payment

def cals_monthly_payments(date_now, body_credit, monthly_payment, raid, number_of_periods):
    df = []
    for month in range(0, number_of_periods):
        begin = dt.datetime(date_now.year, date_now.month, 5) + relativedelta(months=+month)
        intermediate_date = dt.datetime(date_now.year, date_now.month, 1) + relativedelta(months=+(month+1)) - relativedelta(days = 1)
        end = dt.datetime(date_now.year, date_now.month, 5) + relativedelta(months=+(month+1))
        
        number_of_days1 = (intermediate_date - begin).days
        number_of_days2 = (end - intermediate_date).days
        number_of_days_in_year1 = (dt.datetime(int(begin.year)+1, 1, 1) - dt.datetime(begin.year, 1, 1)).days
        number_of_days_in_year2 = (dt.datetime(int(end.year)+1, 1, 1) - dt.datetime(end.year, 1, 1)).days
        percent_part = (body_credit * raid * number_of_days1)/(100*number_of_days_in_year1) + (body_credit * raid * number_of_days2)/(100*number_of_days_in_year2)
        general_part = monthly_payment - percent_part
        if body_credit - general_part <0:
            general_part = body_credit
            body_credit = 0
        else:
            body_credit -= general_part
        
        df.append([end, percent_part, general_part, body_credit, number_of_days1+number_of_days2])
    df = pd.DataFrame(df, columns = ['date_payment', 'percent_part', 'general_part', 'body_of_credit', 'days'])
    return df

def insert_to_db(cur, con, tuples):
    str_to_insert = f"INSERT INTO credits VALUES {tuples} "
    cur.execute(str_to_insert)
    con.commit()