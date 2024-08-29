import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import LoginError, RegisterError
from streamlit_lottie import st_lottie
from utils.lottie import display_lottie_on_page

# Set up the page configuration
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
    with open('./config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file not found.")
    st.stop()
except yaml.YAMLError as e:
    st.error(f"Error loading YAML file: {e}")
    st.stop()

# Hashing all plain text passwords once
# Hasher.hash_passwords(config['credentials'])

# Creating the authenticator object and storing it in session state
if 'authenticator' not in st.session_state:
    st.session_state['authenticator'] = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
        # False
    )

authenticator = st.session_state['authenticator']

# Login page content
if not st.session_state.get("authentication_status"):
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

    account_page = st.Page(
        page="pages/02_🧑🏾‍💻_Account.py",
        title="Account",
        icon="🧑🏾‍💻"
    )

    data_page = st.Page(
        page="pages/03_📊_Data.py",
        title="Data Overview",
        icon="📊"
    )

    dashboard_page = st.Page(
        page="pages/04_📈_Dashboard.py",
        title="Analytics Dashboard",
        icon="📈"
    )

    history_page = st.Page(
        page="pages/05_🕰️_History.py",
        title="Historical Insights",
        icon="🕰️"
    )

    prediction_page = st.Page(
        page="pages/06_🔮_Prediction.py",
        title="Future Projections",
        icon="🔮"
    )

    # Show authenticated pages
    pg = st.navigation(
        {
            "User Interaction": [home_page, account_page],
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

# --- SHARED ON ALL PAGES ---
st.sidebar.text("Powered by Team Switzerland 💡🌍")