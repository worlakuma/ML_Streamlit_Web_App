import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)
import requests
from streamlit_lottie import st_lottie
from utils.lottie import display_lottie_on_page

st.set_page_config(
    page_title="Churn Predictor",
    page_icon="assets/app_icon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SHARED ON ALL PAGES ---
st.logo("assets/team_logo.svg")
st.image("assets/team_logo.svg", width=200)

# Load configuration from YAML file
try:
    with open('./utils/config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file not found.")
    st.stop()
except yaml.YAMLError as e:
    st.error(f"Error loading YAML file: {e}")
    st.stop()

# Hashing all plain text passwords once
Hasher.hash_passwords(config['credentials'])

# Creating the authenticator object and storing it in session state
if 'authenticator' not in st.session_state:
    st.session_state['authenticator'] = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized'],
        False
    )

authenticator = st.session_state['authenticator']

# User selection menu
action = st.sidebar.selectbox(
    "Choose an action",
    ("Login", "Register", "Reset Password", "Forgot Password", "Forgot Username", "Update Details")
)

# Lottie animation for the login page
# lottie_login = "https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json"  

# Action: Login
if action == "Login":
    if not st.session_state.get("authentication_status"):
        # Display the login page content if not authenticated
        with st.container():
            st.write("---")
            st.title(" 🔐 Welcome to the Login Page")
            left_column, right_column = st.columns(2)

            with left_column:
                st.header("Secure Login")
                st.write(
                    """
                    Please enter your credentials to access your account.
                    Your information is safe with us, and we ensure top-notch security.
                    """
                )
                st.subheader("About the Churn Predictor App")
                st.write(
                    """
                    The Churn Predictor app is designed to analyze customer data and predict churn risk. 
                    It helps businesses identify customers who are likely to leave and take proactive measures to retain them.
                    """
                )
            with right_column:
                # st_lottie(lottie_login, height=300, key="login")
                display_lottie_on_page("Login")
    
    try:
        authenticator.login()
    except LoginError as e:
        st.error(e)

    if st.session_state.get("authentication_status"):
        authenticator.logout("Logout", "sidebar")
        st.sidebar.title(f'Welcome *{st.session_state["name"]}*')
        
        home_page = st.Page(
            page="pages/01_🏡_Home.py",
            title="Home",
            icon="🏡",
            default=True
        )

        data_page = st.Page(
            page="pages/02_📊_Data.py",
            title="Data Overview",
            icon="📊"
        )

        dashboard_page = st.Page(
            page="pages/03_📈_Dashboard.py",
            title="Analytics Dashboard",
            icon="📈"
        )

        history_page = st.Page(
            page="pages/04_🕰️_History.py",
            title="Historical Insights",
            icon="🕰️"
        )

        prediction_page = st.Page(
            page="pages/05_🔮_Prediction.py",
            title="Future Projections",
            icon="🔮"
        )

        # Show authenticated pages
        pg = st.navigation(
            {
                "User Interaction": [home_page],
                "Data Management": [data_page, dashboard_page],
                "Insights and Forecasting": [history_page, prediction_page],
            }
        )

        # --- NAVIGATION RUN ---
        pg.run()


            
    elif st.session_state.get("authentication_status") is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get("authentication_status") is None:
        st.warning('Please enter your username and password')

# Action: Register
elif action == "Register":
    try:
        (email_of_registered_user,
         username_of_registered_user,
         name_of_registered_user) = authenticator.register_user(pre_authorization=False)
        if email_of_registered_user:
            st.success('User registered successfully')
    except RegisterError as e:
        st.error(e)

# Action: Reset Password
elif action == "Reset Password" and st.session_state.get("authentication_status"):
    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success('Password modified successfully')
    except ResetError as e:
        st.error(e)
    except CredentialsError as e:
        st.error(e)

# Action: Forgot Password
elif action == "Forgot Password":
    try:
        (username_of_forgotten_password,
         email_of_forgotten_password,
         new_random_password) = authenticator.forgot_password()
        if username_of_forgotten_password:
            st.success('New password sent securely')
            # Random password to be transferred to the user securely
        elif not username_of_forgotten_password:
            st.error('Username not found')
    except ForgotError as e:
        st.error(e)

# Action: Forgot Username
elif action == "Forgot Username":
    try:
        (username_of_forgotten_username,
         email_of_forgotten_username) = authenticator.forgot_username()
        if username_of_forgotten_username:
            st.success('Username sent securely')
            # Username to be transferred to the user securely
        elif not username_of_forgotten_username:
            st.error('Email not found')
    except ForgotError as e:
        st.error(e)

# Action: Update User Details
elif action == "Update Details" and st.session_state.get("authentication_status"):
    try:
        if authenticator.update_user_details(st.session_state["username"]):
            st.success('Entries updated successfully')
    except UpdateError as e:
        st.error(e)

# Saving config file
with open('./utils/config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)

# --- SHARED ON ALL PAGES ---
# authenticator.logout("Logout", "sidebar")

st.sidebar.text("Powered by Team Switzerland 💡🌍") 


