import streamlit as st
from PIL import Image
import sqlite3
import pandas as pd
import plotly.express as px
import datetime as dt

con = sqlite3.connect("DB/Credit.db")
cur = con.cursor()

st.set_page_config(page_title='Home')
st.title("### 🏘 Ипотечный калькулятор")
# st.subheader('Основные параметры')
st.image('/home/ivan/Projects/streamlit/images/bird-cher-rech.jpg')

main_title = ['title', 'date_of_deal', 'body_of_credit', 'raid', 'number_of_periods', 'last_payment', 'monthly_payment']
st.session_state.main_df = pd.DataFrame(cur.execute("SELECT * FROM credits").fetchall(), columns = main_title)


st.title("Основные параметры")
credit_name = st.selectbox('Выберете кредит:', options = st.session_state.main_df['title'].unique())

credit_title = ['date_payment', 'percent_part', 'general_part', 'body_of_credit', 'days']
st.session_state.credit_df = pd.DataFrame(cur.execute(f"SELECT * FROM {credit_name}").fetchall(), columns = credit_title).sort_values('date_payment')
st.session_state.credit_df['date_payment'] = pd.to_datetime(st.session_state.credit_df['date_payment'], errors='coerce')
st.session_state.now_credit_df = st.session_state.credit_df[st.session_state.credit_df['date_payment']>=dt.datetime.now()]

col1, col2 = st.columns(2)

with col1:
        st.metric('Остаток основного долга', round(st.session_state.now_credit_df.iloc[0, 3]))
        st.metric('Следующий платеж', str(st.session_state.now_credit_df.iloc[0, 0])[:10])
        

with col2:
        st.metric('Осталось платежей', len(st.session_state.now_credit_df))


df_to_pie = st.session_state.now_credit_df[['percent_part', 'general_part']].head(1).transpose().reset_index()
df_to_pie.columns = ['names', 'values']
st.subheader(f'Соотношение погашения процентов в следующем платеже')
st.plotly_chart(px.pie(df_to_pie, names='names', values='values', color="names", color_discrete_sequence=['rgb(179, 205, 227)', 'rgb(179, 226, 205)'], width = 600, height=350, opacity=0.75, hole=0.5), use_container_width=False)

st.subheader(f'Соотношение погашения процентов и основного долга по месяцам')
st.plotly_chart(px.area(st.session_state.credit_df[['date_payment', 'percent_part', 'general_part']], x='date_payment', y=['percent_part', 'general_part'], color_discrete_sequence=['rgb(179, 205, 227)', 'rgb(179, 226, 205)'], width = 800, height=500))

with st.expander('Таблица платежей', expanded=False):
        st.dataframe(st.session_state.credit_df)
