import requests
import streamlit as st
from streamlit_lottie import st_lottie

# Cache the Lottie animation data with persistence across sessions
@st.cache_data(show_spinner=False, persist=True)
def load_lottie_animation(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load Lottie animation: {e}")
        return None

# Example of how to use this in a page
def display_lottie_on_page(page_name):
    lottie_urls = {
        "Login": "https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json",
        "Home": "https://lottie.host/f3734960-8bd5-4e1e-94c7-57787a497ac7/dXSGaeZhUf.json",
        "Data Overview": "https://assets5.lottiefiles.com/private_files/lf30_5ttqPi.json",
        "Analytics Dashboard": "https://assets1.lottiefiles.com/packages/lf20_o6spyjnc.json",
        "Historical Insights": "https://assets7.lottiefiles.com/packages/lf20_jcikwtux.json",
        "Future Projections": "https://lottie.host/f62700df-68f9-4858-a0e5-c3896fad8bec/zw3ny4manX.json"        
    }

    if page_name in lottie_urls:
        animation_data = load_lottie_animation(lottie_urls[page_name])
        if animation_data:
            st_lottie(animation_data, height=300, key=page_name)
    else:
        st.error("No Lottie animation available for this page.")
