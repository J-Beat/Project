import streamlit as st
import streamlit_authenticator as stauth
import yaml
from os.path import abspath
from inspect import getsourcefile


# hashed_passwords = stauth.Hasher(['123', '456']).generate()
# print(hashed_passwords)


path = str(abspath(getsourcefile(lambda:0)))
main_path = path.split(path.split('/')[-1])[0]

with open('/home/ivan/Projects/git/Project/streamlit/users.yaml') as file:
    config = yaml.load(file, Loader=stauth.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

with st.sidebar:
    authenticator.logout('Logout', 'main')

if st.session_state["authentication_status"] == None:

    tabsign, tabregs = st.tabs(["Вход", "Регистрация"])

    with tabsign:
        name, authentication_status, username = authenticator.login('Login', 'main')
        # if st.session_state["authentication_status"]:  
        if st.session_state["authentication_status"] == False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] == None:
            st.warning('Please enter your username and password')

    with tabregs:
        try:
            if authenticator.register_user('Register user', preauthorization=False):
                st.success('User registered successfully')
                with open('/home/ivan/Projects/git/Project/streamlit/users.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)

else:
    st.title("### 🏘 Ипотечный калькулятор")
    st.image(f'{main_path}/images/bird-cher-rech.jpg')
    st.subheader(f'Здравствуйте *{st.session_state["name"]}*')
    st.write('Здесь вы можете рассчитать кредит, следить за изменением своих кредитов и рассчитывать досрочное погашение.')            



# reg = st.button('Регистрация')
# if reg:
#     # authenticator.register_user('Register user', preauthorization=False)
#     st.success('User registered successfully')
    # if authenticator.register_user('Register user', preauthorization=False):
    #     st.success('User registered successfully')
    # try:
    #     if authenticator.register_user('Register user', preauthorization=False):
    #         st.success('User registered successfully')
    # except Exception as e:
    #     st.error(e)