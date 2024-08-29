import streamlit as st
import pandas as pd
import numpy as np
import joblib
import datetime
import os
from utils.login import invoke_login_widget

# st.set_page_config(
#     page_title='Predictions',
#     layout='wide',
# )    

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
    @st.cache_resource()
    def load_forest():
        return joblib.load('./models/RF.joblib')

    @st.cache_resource()
    def load_xb():
        return joblib.load('./models/XB.joblib')



    # Model selection function
    def select_model():
        st.selectbox('Select a Model', options=['Random Forest', 'XGB'], key='selected_model')
        pipeline = load_forest() if st.session_state['selected_model'] == 'Random Forest' else load_xb()
        encoder = joblib.load('./models/encoder.joblib')
        return pipeline, encoder  


    # Prediction function
    def make_prediction(pipeline, encoder):
        gender_map = {'Male': 0, 'Female': 1}
        yes_no_map = {'Yes': 1, 'No': 0}
        contract_map = {'Month-to-month': 0, 'One year': 1, 'Two years': 2}
        payment_map = {'Mailed check': 0, 'Electronic Check': 1, 'Bank Transfer (automatic)': 2, 'Credit Card(automatic)': 3}
        internet_map = {'DSL': 0, 'Fiber optic': 1, 'No': 2}

        data = [[
            gender_map[st.session_state['gender']],
            yes_no_map[st.session_state['senior_citizen']],
            yes_no_map[st.session_state['partner']],
            yes_no_map[st.session_state['dependents']],
            st.session_state['tenure'],
            yes_no_map[st.session_state['phone_service']],
            yes_no_map[st.session_state['multiple_lines']],
            internet_map[st.session_state['internet_service']],
            yes_no_map[st.session_state['online_security']],
            yes_no_map[st.session_state['online_backup']],
            yes_no_map[st.session_state['device_protection']],
            yes_no_map[st.session_state['tech_support']],
            yes_no_map[st.session_state['streaming_movies']],
            yes_no_map[st.session_state['streaming_tv']],
            contract_map[st.session_state['contract']],
            payment_map[st.session_state['payment_method']],
            st.session_state['monthly_charges'],
            st.session_state['total_charges'],
            st.session_state['avg_monthly_charges'],
            st.session_state['monthly_Charges_to_total_charges_ratio'],
            yes_no_map[st.session_state['paperless_billing']]
        ]]
        
        columns = [
            'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure',
            'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity',
            'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV',
            'StreamingMovies', 'Contract', 'PaperlessBilling', 'PaymentMethod',
            'MonthlyCharges', 'TotalCharges', 'AvgMonthlyCharges',
            'MonthlyChargesToTotalChargesRatio'
        ]

        df = pd.DataFrame(data=data, columns=columns)
        
        # Make predictions
        pred = pipeline.predict(df)
        probability = pipeline.predict_proba(df)
        prediction = encoder.inverse_transform([pred])
        prediction_labels = "Yes" if pred == 1 else "No"

        st.write(f'Predicted Churn: {prediction_labels}')
        
        # Copy the original dataframe to the new dataframe
        hist_df = df.copy()

        def inverse_prediction(hist_df):
            # Inverse mappings
            inverse_gender_map = {0: 'Male', 1: 'Female'}
            inverse_yes_no_map = {1: 'Yes', 0: 'No'}
            inverse_contract_map = {0: 'Month-to-month', 1: 'One year', 2: 'Two years'}
            inverse_payment_map = {0: 'Mailed check', 1: 'Electronic Check', 2: 'Bank Transfer (automatic)', 3: 'Credit Card(automatic)'}
            inverse_internet_map = {0: 'DSL', 1: 'Fiber optic', 2: 'No'}

            # Updated column names
            inverted_data = pd.DataFrame({
                'gender': hist_df['gender'].map(inverse_gender_map),
                'SeniorCitizen': hist_df['SeniorCitizen'].map(inverse_yes_no_map),
                'Partner': hist_df['Partner'].map(inverse_yes_no_map),
                'Dependents': hist_df['Dependents'].map(inverse_yes_no_map),
                'tenure': hist_df['tenure'],
                'PhoneService': hist_df['PhoneService'].map(inverse_yes_no_map),
                'MultipleLines': hist_df['MultipleLines'].map(inverse_yes_no_map),
                'InternetService': hist_df['InternetService'].map(inverse_internet_map),
                'OnlineSecurity': hist_df['OnlineSecurity'].map(inverse_yes_no_map),
                'OnlineBackup': hist_df['OnlineBackup'].map(inverse_yes_no_map),
                'DeviceProtection': hist_df['DeviceProtection'].map(inverse_yes_no_map),
                'TechSupport': hist_df['TechSupport'].map(inverse_yes_no_map),
                'StreamingTV': hist_df['StreamingTV'].map(inverse_yes_no_map),
                'StreamingMovies': hist_df['StreamingMovies'].map(inverse_yes_no_map),
                'Contract': hist_df['Contract'].map(inverse_contract_map),
                'PaperlessBilling': hist_df['PaperlessBilling'].map(inverse_yes_no_map),
                'PaymentMethod': hist_df['PaymentMethod'].map(inverse_payment_map),
                'MonthlyCharges': hist_df['MonthlyCharges'],
                'TotalCharges': hist_df['TotalCharges'],
                'AvgMonthlyCharges': hist_df['AvgMonthlyCharges'],
                'MonthlyChargesToTotalChargesRatio': hist_df['MonthlyChargesToTotalChargesRatio']
            })

            return inverted_data

        history_df = inverse_prediction(hist_df)
        history_df['PredictionTime'] = datetime.date.today()
        history_df['ModelUsed'] = st.session_state['selected_model']
        
        history_df['Probability'] = np.where(pred==1,np.round(probability[:,1]*100,2), np.round(probability[:,0]*100,2))
            
        # # Save the history dataframe to a CSV file
        history_df.to_csv('./data/history.csv', mode='a', header=not os.path.exists('./data/history.csv'), index=False)
        
        st.session_state['prediction'] = prediction
        st.session_state['probability'] = probability
        st.session_state['prediction_labels'] = prediction_labels
        return prediction, probability, prediction_labels

    # Initialize session state keys if they don't exist
    if 'avg_monthly_charges' not in st.session_state:
        st.session_state['avg_monthly_charges'] = 0.00
    if 'monthly_Charges_to_total_charges_ratio' not in st.session_state:
        st.session_state['monthly_Charges_to_total_charges_ratio'] = 0.00
    # Input form function
    def input_form():
        pipeline, encoder = select_model()
        
        with st.form('input_features', clear_on_submit=True):
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
                st.selectbox('Select payment method', options=[
                    'Mailed check', 'Electronic Check', 'Bank Transfer (automatic)', 'Credit Card(automatic)'], key='payment_method')
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
                def calculate_features(inputs):
                        tenure = inputs['tenure']
                        MonthlyCharges = inputs['monthly_charges']  
                        TotalCharges = inputs['total_charges']
                        
                        if tenure > 0:
                            AvgMonthlyCharges = TotalCharges / tenure  
                            monthly_charges_to_total_charges_ratio = MonthlyCharges / TotalCharges if TotalCharges != 0 else 0
                        else:
                            AvgMonthlyCharges = 0
                            monthly_charges_to_total_charges_ratio = 0
                        
                        return AvgMonthlyCharges, monthly_charges_to_total_charges_ratio

                AvgMonthlyCharges, monthly_charges_to_total_charges_ratio = calculate_features(st.session_state)
            submitted = st.form_submit_button('Make Prediction', on_click=make_prediction, kwargs=dict(pipeline=pipeline, encoder=encoder))
            

    # Execute the form function directly
    # if _name_ == '_main_':
    input_form()

    # Display prediction results
    prediction = st.session_state['prediction']
    probability = st.session_state['probability']

    if not prediction:
        st.markdown('### Prediction will show here')
    elif prediction == "YES":
        probability_of_yes = probability[0][1]*100
        st.markdown(f'### The employee will leave the company with a probability of {round(probability_of_yes, 2)}%')
    else:
        probability_of_no = probability[0][0] * 100
        st.markdown(f'### The employee will not leave the company with a probability of {round(probability_of_no, 2)}%')    
    # st.write(st.session_state)