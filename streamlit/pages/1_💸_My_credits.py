import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import datetime as dt
from inspect import getsourcefile
from os.path import abspath
import sys
import streamlit_tools as tool

path = str(abspath(getsourcefile(lambda:0)))
main_path = path.split('pages')[0]
con = sqlite3.connect(f'{main_path}/DB/Credit.db')
cur = con.cursor()

st.set_page_config(page_title='Home')
if "authentication_status" in st.session_state:
        if st.session_state["authentication_status"]:
                st.title("Мои кредиты")

                
                st.session_state.main_df = tool.get_params_df(cur, st.session_state["name"])
                if len(st.session_state.main_df)>0:
                        credit_name = st.selectbox('Выберете кредит:', options = st.session_state.main_df['title'].unique())

                        st.session_state.credit_df = tool.get_data_df(credit_name, cur)
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

                        del_cred = st.button('Удалить кредит')
                        if del_cred:
                                cur.execute(f"DROP TABLE {credit_name}")
                                cur.execute(f"DELETE FROM credits WHERE title = '{credit_name}'")
                                con.commit()
                                st.experimental_rerun()

                else:
                        st.subheader('Вы еще не добавили ни одного кредита.')
                        st.write('Вы можете добавить кредиты на вкладке - "New credit".')
