import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
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

st.session_state.main_df = tool.get_params_df(cur)
if len(st.session_state.main_df)>0:
    st.session_state.main_df = st.session_state.main_df[st.session_state.main_df['user'] == st.session_state["name"]]
    st.session_state.main_df = st.session_state.main_df[['title', 'date_of_deal', 'body_of_credit', 'raid', 'number_of_periods', 'last_payment', 'monthly_payment']]
    
    credit_name = st.selectbox('Выберете кредит:', options = st.session_state.main_df['title'].unique())
    type_payment = st.selectbox('Выберете тип платежа:', options = ['Уменьшение суммы ежемесячного платежа', 'Уменьшение срока кредита'])

    params_df = st.session_state.main_df[st.session_state.main_df['title'] == 'credit_name']
    data_df = tool.get_data_df(credit_name, cur)