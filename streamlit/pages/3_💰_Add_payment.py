import streamlit as st
import sqlite3
import pandas as pd
import datetime as dt
from inspect import getsourcefile
from os.path import abspath
import streamlit_tools as tool

path = str(abspath(getsourcefile(lambda:0)))
main_path = path.split('pages')[0]
con = sqlite3.connect(f'{main_path}/DB/Credit.db')
cur = con.cursor()


st.set_page_config(page_title='Add_payment')

st.title("Внести досрочный платеж")

st.session_state.main_df = tool.get_params_df(cur, st.session_state["name"])
if len(st.session_state.main_df)>0:
    date_now = dt.datetime.now()
    credit_name = st.selectbox('Выберете кредит:', options = st.session_state.main_df['title'].unique())
    type_payment = st.selectbox('Выберете тип платежа:', options = ['Уменьшение суммы ежемесячного платежа', 'Уменьшение срока кредита'])
    sum_payment = st.number_input('Введите сумму платежа')

    data_df = tool.get_data_df(credit_name, cur)
    data_df = data_df[data_df['date_payment']<=date_now]

    params_df = st.session_state.main_df[st.session_state.main_df['title'] == credit_name]
    params_df['date_of_deal'] = pd.to_datetime(params_df['date_of_deal'], errors='coerce')
    params = {}
    
    for col in params_df.columns:
        params[col] = params_df.iloc[0][col]

    date_of_deal = dt.datetime(date_now.year, date_now.month, params['date_of_deal'].day)
    body_of_credit = params['body_of_credit'] - sum_payment-data_df['general_part'].sum()
    number_of_periods = params['number_of_periods'] - data_df['date_payment'].nunique()
    _, monthly_payment = tool.calc(date_of_deal, body_of_credit, params['raid'], number_of_periods)
    st.write(monthly_payment)
    post_pay_df = tool.cals_monthly_payments(date_of_deal, body_of_credit, monthly_payment, params['raid'], params['number_of_periods'])
    

    st.dataframe(pd.concat([data_df, post_pay_df]))

    