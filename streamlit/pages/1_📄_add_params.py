import streamlit as st
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import *
import sys
# sys.path.append('/home/ivan/Projects/streamlit/tools')
import tools as tool
import sqlite3
from inspect import getsourcefile
from os.path import abspath


path = str(abspath(getsourcefile(lambda:0)))
main_path = path.split('pages')[0]
con = sqlite3.connect(f'{main_path}/DB/Credit.db')
cur = con.cursor()

st.set_page_config(page_title='Add_main_params')
st.header("### 💰 Добавить основные параметры")

# st.write(st.session_state)
if 'all_params_added' in st.session_state:
        st.subheader('Параметры кредита добавлены!')
        st.write('Вы молодец🙂')
else:
        with st.form('Добавьте параметры:'):
                name_of_credit = st.text_input('Название кредита', help = 'Введите название латиницей без пробелов')
                if ' ' in name_of_credit:
                        st.error('Неправильно введено имя кредита')
                begin = st.date_input('Дата заключения сделки', value=datetime.today())
                begin = datetime.combine(begin, datetime.min.time())
                body_of_credit = st.number_input('Общая сумма кредита', value = 1000000, step = 1)
                raid = st.number_input('Ставка по кредиту', value = 5.0, step = 0.1)
                number_of_periods = st.number_input('Количество платежей (месяцев)', value = 1, step = 1)
                submit_main_params = st.form_submit_button("Добавить")
                if submit_main_params:
                        st.session_state.last_payment, st.session_state.monthly_payment = tool.calc(begin, body_of_credit, raid, number_of_periods)
                        st.session_state.main_params_added = True

        if 'main_params_added' in st.session_state:                       
                with st.form('Проверьте параметры вашего кредита:'):
                        st.subheader('Проверьте параметры вашего кредита')
                        st.write(f'Название кредита: {name_of_credit}')
                        st.write(f'Дата заключения сделки: {begin}')
                        st.write(f'Последний платеж: {st.session_state.last_payment}')
                        st.write(f'Общая сумма кредита: {body_of_credit}')
                        st.write(f'Ставка по кредиту: {raid}')
                        st.write(f'Количество платежей (месяцев): {number_of_periods}')
                        st.write(f'Ежемесячный платеж: {st.session_state.monthly_payment}')
                        submit_all_params = st.form_submit_button("Верно")

                        if submit_all_params:
                                st.balloons()
                                st.session_state.all_params_added = True
                                data_to_insert = (name_of_credit, str(begin), body_of_credit, raid, number_of_periods, str(st.session_state.last_payment), st.session_state.monthly_payment)
                                tool.insert_to_db(cur, con, data_to_insert)
                                df_cred = tool.cals_monthly_payments(begin,  body_of_credit, st.session_state.monthly_payment, raid, number_of_periods)
                                df_cred .to_sql(name_of_credit, con, index=False)
                                st.experimental_rerun()
                                



