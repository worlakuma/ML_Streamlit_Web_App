import streamlit as st
import pandas as pd
import joblib  # For loading the trained model
from streamlit_lottie import st_lottie
import requests
from utils.login import invoke_login_widget
from utils.lottie import display_lottie_on_page

# Invoke the login form
invoke_login_widget('Future Projections')

# Fetch the authenticator from session state
authenticator = st.session_state.get('authenticator')

if not authenticator:
    st.error("Authenticator not found. Please check the configuration.")
    st.stop()

# Check authentication status
if st.session_state.get("authentication_status"):

    st.title("Predictive Analytics")

    # Sidebar for prediction input
    st.sidebar.header("Prediction Input")
    uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file for prediction", type=["csv", "xlsx"])

    def load_data(uploaded_file):
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_file)
                return df
            except Exception as e:
                st.error(f"Error: {e}")
                return None
        else:
            return None

    df = load_data(uploaded_file)

    if df is not None:
        st.write("### Uploaded Dataset for Prediction", df)
        st.dataframe(df)

        # Load the trained model (update the model path accordingly)
        model = joblib.load('./models/churn_model.pkl')  # Replace with your actual model path

        # Placeholder for running predictions
        st.write("### Prediction Results")
        
        # Preprocess the data as needed for your model
        # Example: 
        # Assuming the model expects a specific set of features
        features = ['Feature1', 'Feature2', 'Feature3']  # Replace with actual feature names
        if all(feature in df.columns for feature in features):
            input_data = df[features]

            # Run predictions
            predictions = model.predict(input_data)
            df['Churn Prediction'] = predictions

            st.write("#### Churn Prediction Results")
            st.dataframe(df[['Churn Prediction'] + features])  # Display predictions alongside features

        else:
            st.error("Uploaded data does not contain the required features for prediction.")

    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        
        with left_column:
            st.subheader("Prediction Overview")
            st.write("Upload your data and predict outcomes using our machine learning models.")
            st.markdown("""
            - Customer churn prediction
            - Sales forecasting
            - Risk assessment
            """)
        
        with right_column:
            display_lottie_on_page("Future Projections")


    # Use a reliable Lottie animation URL for predictive analysis
    # lottie_prediction = "https://lottie.host/f62700df-68f9-4858-a0e5-c3896fad8bec/zw3ny4manX.json"

    # st_lottie(lottie_prediction, height=300, key="prediction")
