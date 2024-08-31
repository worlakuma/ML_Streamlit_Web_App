import requests
from streamlit_lottie import st_lottie
import streamlit as st
from utils.login import invoke_login_widget
from utils.lottie import display_lottie_on_page
import pandas as pd
import plotly.express as px
import joblib
import os

# Invoke the login form
invoke_login_widget('Historical Insights')

# Fetch the authenticator from session state
authenticator = st.session_state.get('authenticator')

if not authenticator:
    st.error("Authenticator not found. Please check the configuration.")
    st.stop()

# Check authentication status
if st.session_state.get("authentication_status"):

    st.title("Company History")

    # Display the history page content
    with st.container():
        st.write("---")
        
        left_column, right_column = st.columns(2)

        with left_column:
            st.header("Our Journey")
            st.write(
                """
                Our company has been at the forefront of innovation for over a decade.
                Here’s a look at some of the milestones we’ve achieved along the way.
                """
            )
            st.subheader("Milestones")
            st.markdown(
                """
                - **2009:** Founded with the mission to revolutionize the tech industry.
                - **2012:** Launched our first major product.
                - **2015:** Expanded internationally.
                - **2020:** Surpassed 10 million users.
                - **2023:** Named one of the most innovative companies in the world.
                """
            )
        with right_column:
            display_lottie_on_page("Historical Insights")

    st.write("---")

    # Business Insights Section
    st.subheader("Business Insights")
    st.write("This section provides actionable insights derived from customer data analysis to help identify key trends, behaviors, and opportunities for growth.")

    # Load Historical Data (Assuming a CSV without dates)
    
    data = pd.read_csv('./data/history.csv') # Replace with your

    # # Drop the Avg column and Mothlycharges
    # data.drop('AvgMonthlyCharges', axis=1, inplace=True)
    # data.drop('MonthlyChargesToTotalChargesRatio', axis=1, inplace=True)

    st.dataframe(data) # Replace with your actual data path
    # @st.cache_data(persist=True)
    # def load_historical_data():
    #     if os.path.exists('./data/history.csv'):
    #         df = pd.read_csv('./data/history.csv')  # Replace with your actual data path
    #     else:
    #         st.error("No historical data found.")
            
    #     return df
    # df = load_historical_data()

    # st.dataframe(df)

    
    # # Inspect the dataset (comment out after use)
    # st.write("Columns in the dataset:", df.columns.tolist())  # Display all column names

    # Key Metrics Section
    # st.subheader("Key Metrics Overview")
    # with st.container():
    #     left_col, middle_col, right_col = st.columns(3)

    #     # Use correct column names based on the dataset
    #     if 'CustomerID' in data.columns:
    #         with left_col:
    #             st.metric("Total Customers", data['CustomerID'].nunique())  # Replace with actual customer count column
    #     else:
    #         st.warning("Column 'CustomerID' not found in the dataset.")

    #     if 'Revenue' in data.columns:
    #         with middle_col:
    #             st.metric("Average Revenue per User", f"${data['Revenue'].mean():.2f}")  # Replace with actual revenue column
    #     else:
    #         st.warning("Column 'Revenue' not found in the dataset.")

    #     if 'SatisfactionRate' in data.columns:
    #         with right_col:
    #             st.metric("Customer Satisfaction Rate", f"{data['SatisfactionRate'].mean():.2f}%")  # Replace with actual satisfaction column
    #     else:
    #         st.warning("Column 'SatisfactionRate' not found in the dataset.")

    # st.write("---")

    # # Historical Analysis Section
    # st.subheader("Historical Trends Analysis")
    # st.write("This section visualizes key trends over time, highlighting customer behavior and revenue generation.")

    # # Sample Visualization: Revenue over time (even without dates, can use index or other columns)
    # if 'Revenue' in df.columns:
    #     fig1 = px.line(df, x=df.index, y='Revenue', title='Revenue Over Time', labels={'x': 'Index', 'Revenue': 'Revenue'})
    #     st.plotly_chart(fig1, use_container_width=True)

    # # Additional Visualizations
    # if 'CustomerSegment' in df.columns:
    #     customer_segment_counts = df['CustomerSegment'].value_counts().reset_index()
    #     customer_segment_counts.columns = ['Customer Segment', 'Count']
    #     fig2 = px.bar(customer_segment_counts, x='Customer Segment', y='Count', title='Customer Segmentation Distribution')
    #     st.plotly_chart(fig2, use_container_width=True)

    # st.write("---")



    # Replace with an existing Lottie animation URL
    # lottie_history = "https://assets7.lottiefiles.com/packages/lf20_jcikwtux.json" 

    # st_lottie(lottie_history, height=300, key="history")
