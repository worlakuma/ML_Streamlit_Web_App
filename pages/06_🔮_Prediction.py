import streamlit as st
import pandas as pd
import numpy as np
import joblib
import datetime
import os
from utils.login import invoke_login_widget

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


    # Load models
    @st.cache_resource(show_spinner='Models Loading')
    def models():
        rf_model = joblib.load('./models/RF.joblib')
        gb_model = joblib.load('./models/GB.joblib')
        xgb_model = joblib.load('./models/XB.joblib')
        return rf_model, gb_model, xgb_model

    RF, GB, XB = models()

    # Initialize session state for selected model
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = 'Random Forest'

    # Select model 
    col1, col2 = st.columns(2)
    with col1:
        selected_model = st.selectbox('Select a Model', options=['Random Forest', 'GBoost', 'XGBoost'], 
                                    key='selected_model',
                                    index=['Random Forest', 'GBoost', 'XGBoost'].index(st.session_state.selected_model))
    
    # Get the selected model
    @st.cache_resource(show_spinner='Loading models...')
    def get_model(selected_model):
        if selected_model == 'Random Forest':
            pipeline = RF
        elif selected_model == 'GBoost':
            pipeline = GB
        else:
            pipeline = XB
        encoder = joblib.load('./models/encoder.joblib')
        return pipeline, encoder  

    # Initialize session state for predictions and probabilities
    if 'prediction' not in st.session_state:
        st.session_state['prediction'] = None
    if 'probability' not in st.session_state:
        st.session_state['probability'] = None

    # Prediction function
    def make_prediction(pipeline, encoder):
        # Collect user input from session state
        user_input = {
            'gender': st.session_state['gender'],
            'SeniorCitizen': st.session_state['senior_citizen'],
            'Partner': st.session_state['partner'],
            'Dependents': st.session_state['dependents'],
            'tenure': st.session_state['tenure'],
            'PhoneService': st.session_state['phone_service'],
            'MultipleLines': st.session_state['multiple_lines'],
            'InternetService': st.session_state['internet_service'],
            'OnlineSecurity': st.session_state['online_security'],
            'OnlineBackup': st.session_state['online_backup'],
            'DeviceProtection': st.session_state['device_protection'],
            'TechSupport': st.session_state['tech_support'],
            'StreamingTV': st.session_state['streaming_tv'],
            'StreamingMovies': st.session_state['streaming_movies'],
            'Contract': st.session_state['contract'],
            'PaperlessBilling': st.session_state['paperless_billing'],
            'PaymentMethod': st.session_state['payment_method'],
            'MonthlyCharges': st.session_state['monthly_charges'],
            'TotalCharges': st.session_state['total_charges'],
        }

        # Convert the input data to a DataFrame
        df = pd.DataFrame(user_input, index=[0])   
        
        # Make predictions
        pred = pipeline.predict(df) 
        pred_int = int(pred[0])   
        prediction = encoder.inverse_transform([[pred_int]])[0]

        # Calculate the probability of churn
        probability = pipeline.predict_proba(df)
        prediction_labels = "Churn" if pred == 1 else "No Churn"

        st.write(f'Predicted Churn: {prediction_labels}')
        
        # Update the session state with the prediction and probabilities
        st.session_state['prediction'] = prediction
        st.session_state['probability'] = probability
        st.session_state['prediction_labels'] = prediction_labels

        # Copy the original dataframe to the new dataframe
        hist_df = df.copy()
        hist_df['PredictionTime'] = datetime.date.today()
        hist_df['ModelUsed'] = st.session_state['selected_model']
        hist_df['Prediction'] = prediction
        hist_df['Probability'] = np.where(pred == 1, np.round(probability[:, 1] * 100, 2), np.round(probability[:, 0] * 100, 2))
        
        # Save the history dataframe to a CSV file
        hist_df.to_csv('./data/history.csv', mode='a', header=not os.path.exists('./data/history.csv'), index=False)

        return prediction, probability, prediction_labels

    def get_user_input():
        pipeline, encoder = get_model(selected_model)

        with st.form('input-feature', clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write('### Subscriber Demographic')
                st.selectbox('Gender', options=['Male', 'Female'], key='gender')
                st.selectbox('Senior Citizen', options=['No', 'Yes'], key='senior_citizen')
                st.selectbox('Dependents', options=['No', 'Yes'], key='dependents')
                st.selectbox('Partner?', options=['Yes', 'No'], key='partner')
            
            with col2:
                st.write('### Subscriber Account Details')
                st.number_input('Key in tenure', min_value=0.00, max_value=72.00, step=0.10, key='tenure')
                st.number_input('Key in monthly charges', min_value=0.00, max_value=200.00, step=0.10, key='monthly_charges')
                st.number_input('Key in total charges per year', min_value=0.00, max_value=100000.00, step=0.10, key='total_charges')
                st.selectbox('Select payment method', options=['Mailed check', 'Electronic Check', 'Bank Transfer (automatic)', 'Credit Card(automatic)'], key='payment_method')
                st.selectbox('Select contract type', options=['Month-to-month', 'One year', 'Two years'], key='contract')
                st.selectbox('Paperless Billing', options=['Yes', 'No'], key='paperless_billing')
            
            with col3:
                st.write('### Subscriptions')
                st.selectbox('Phone Service', options=['Yes', 'No'], key='phone_service')
                st.selectbox('Multiple Lines', options=['Yes', 'No'], key='multiple_lines')
                st.selectbox('Internet Service', options=['DSL', 'Fiber optic', 'No'], key='internet_service')
                st.selectbox('Online Security', options=['Yes', 'No'], key='online_security')
                st.selectbox('Online Backup', options=['Yes', 'No'], key='online_backup')
                st.selectbox('Device Protection', options=['Yes', 'No'], key='device_protection')
                st.selectbox('Tech Support', options=['Yes', 'No'], key='tech_support')
                st.selectbox('Streaming TV', options=['Yes', 'No'], key='streaming_tv')
                st.selectbox('Streaming movies', options=['Yes', 'No'], key='streaming_movies')
            submit = st.form_submit_button('Make Prediction', on_click=make_prediction, kwargs=dict(pipeline=pipeline, encoder=encoder))
            
    # if __name__ == "__main__":
    get_user_input()

    # Display prediction results
    prediction = st.session_state['prediction']
    probability = st.session_state['probability']

    if prediction is None:
        st.markdown('### Prediction will show here')
    elif prediction == "YES":
        probability_of_yes = probability[0][1] * 100
        st.markdown(f'### The employee will leave the company with a probability of {round(probability_of_yes, 2)}%')
    else:
        probability_of_no = probability[0][0] * 100
        st.markdown(f'### The employee will not leave the company with a probability of {round(probability_of_no, 2)}%')

    # Sidebar for prediction input
    st.sidebar.header("Prediction Input")
    uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file for prediction", type=["csv", "xlsx"])
    st.sidebar.markdown(
            """
            **Note:** The uploaded CSV or Excel file should have the following columns:
            - `gender`
            - `SeniorCitizen`
            - `Partner`
            - `Dependents`
            - `tenure`
            - `PhoneService`
            - `MultipleLines`
            - `InternetService`
            - `OnlineSecurity`
            - `OnlineBackup`
            - `DeviceProtection`
            - `TechSupport`
            - `StreamingTV`
            - `StreamingMovies`
            - `Contract`
            - `PaperlessBilling`
            - `PaymentMethod`
            - `MonthlyCharges`
            - `TotalCharges`
            """
        )
    def load_data(uploaded_file):
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    dfp = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(".xlsx"):
                    dfp = pd.read_excel(uploaded_file)
                return dfp
            except Exception as e:
                st.error(f"Error: {e}")
                return None
        else:
            return None

    dfp = load_data(uploaded_file)

    if dfp is not None:
        st.dataframe(dfp.head(3))
        if st.button("Predict on Uploaded Dataset"):
            pipeline, encoder = get_model(selected_model)
            
            # Convert 'TotalCharges' to numeric, coercing errors to NaN
            dfp['TotalCharges'] = pd.to_numeric(dfp['TotalCharges'], errors='coerce')
            
            # Drop 'customerID' column
            dfp = dfp.drop('customerID', axis=1)
            
            # Ensure 'tenure' has no zero or missing values
            dfp['tenure'] = dfp['tenure'].replace(0, 1)
            
            # Ensure 'TotalCharges' has no zero or missing values
            dfp['TotalCharges'] = dfp['TotalCharges'].replace(0, 1)
            
            # Identify object columns to convert to category datatype
            object_columns_to_convert = dfp.select_dtypes(include=['object']).columns
            
            # Convert object columns to category datatype
            dfp[object_columns_to_convert] = dfp[object_columns_to_convert].astype('category')
            
            # Make predictions
            predictions = pipeline.predict(dfp)
            probabilities = pipeline.predict_proba(dfp)
            prediction_labels = encoder.inverse_transform(predictions)
            dfp['Predicted Churn'] = prediction_labels
            
            # Update the session state with the prediction and probabilities
            st.session_state['predictions'] = predictions
            st.session_state['probability'] = probabilities
            st.session_state['prediction_labels'] = prediction_labels

                # Copy the original dataframe to the new dataframe
            his_df = dfp.copy()
            his_df['PredictionTime'] = datetime.date.today()
            his_df['ModelUsed'] = st.session_state['selected_model']
            his_df['Prediction'] = predictions
            his_df['Probability'] = np.where(predictions == 1, np.round(probabilities[:, 1] * 100, 2), np.round(probabilities[:, 0] * 100, 2))
        
            # Save the history dataframe to a CSV file
            # his_df.to_csv('./data/History.csv', mode='a', header=not os.path.exists('./data/History.csv'), index=False)            
            #Display the predictions
            # st.dataframe(dfp)
            st.dataframe(his_df)  # or st.write("### Uploaded Dataset for Prediction", df) 