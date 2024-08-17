import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
from utils.login import invoke_login_widget
from utils.lottie import display_lottie_on_page

# Invoke the login form
invoke_login_widget('Analytics Dashboard')

# Fetch the authenticator from session state
authenticator = st.session_state.get('authenticator')

if not authenticator:
    st.error("Authenticator not found. Please check the configuration.")
    st.stop()

# Check authentication status
if st.session_state.get("authentication_status"):

    st.title("Dashboard")

    # Load Lottie animation
    display_lottie_on_page("Analytics Dashboard")

    # Sidebar options for data filtering
    st.sidebar.header("Filter Options")
    date_filter = st.sidebar.date_input("Select Date Range", [])

    # Main Dashboard Content
    st.write("---")

    # Key Metrics Section
    st.subheader("Key Metrics")
    with st.container():
        left_column, middle_column, right_column = st.columns(3)
        
        with left_column:
            st.metric("Customer Retention Rate", "85%", delta="+3%")
        
        with middle_column:
            st.metric("Revenue Growth", "$1.2M", delta="+5%")
        
        with right_column:
            st.metric("Market Segment Performance", "Segment A: 40%", delta="-2%")

    st.write("---")

    # Load Data
    @st.cache_data(persist=True)
    def load_data():
        df = pd.read_excel('./data/LP2_train_final.xlsx')
        df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
        return df
    
    df = load_data()

    # Plot Layout in 3x3 Grid
    st.subheader("Interactive Visualizations")
    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            # Plot: Churn Rate by Contract Type
            churn_contract = df.groupby('Contract')['Churn'].mean().reset_index()
            churn_contract['Churn Rate'] = churn_contract['Churn'] * 100
            fig1 = px.pie(churn_contract, names='Contract', values='Churn Rate', title="Churn Rate by Contract Type",
                          labels={'Churn Rate': 'Churn Rate (%)'})
            fig1.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent')
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # Plot: Monthly Charges vs Churn
            fig2 = px.scatter(df, x='Churn', y='MonthlyCharges', color='Churn',
                              labels={'Churn': 'Churn (0 = No, 1 = Yes)', 'MonthlyCharges': 'Monthly Charges'},
                              title="Monthly Charges vs Churn")
            fig2.update_layout(xaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['No', 'Yes']))
            st.plotly_chart(fig2, use_container_width=True)

        with col3:
            # Plot: Customer Segmentation by Contract Type
            contract_proportion = df['Contract'].value_counts(normalize=True).reset_index()
            contract_proportion.columns = ['Contract', 'Proportion']
            contract_proportion['Proportion'] *= 100
            fig3 = px.bar(contract_proportion, x='Contract', y='Proportion', text='Proportion',
                          title="Customer Segmentation by Contract Type",
                          labels={'Proportion': 'Proportion (%)'})
            fig3.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)

    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            # Plot: Churn Rate by Tenure
            fig4 = px.histogram(df, x='tenure', y='Churn', histfunc='avg',
                                title="Churn Rate by Tenure",
                                labels={'Churn': 'Churn Rate', 'tenure': 'Tenure (Months)'})
            fig4.update_traces(marker_line_width=0, hoverinfo='x+y')
            st.plotly_chart(fig4, use_container_width=True)

        with col2:
            # Plot: Total Charges Distribution
            fig5 = px.histogram(df, x='TotalCharges', title="Total Charges Distribution",
                                labels={'TotalCharges': 'Total Charges'})
            st.plotly_chart(fig5, use_container_width=True)

        with col3:
            # Plot: Payment Method Distribution
            payment_method_counts = df['PaymentMethod'].value_counts().reset_index()
            payment_method_counts.columns = ['PaymentMethod', 'Count']  # Rename columns for clarity
            fig6 = px.bar(payment_method_counts, x='PaymentMethod', y='Count',
                        title="Payment Method Distribution",
                        labels={'PaymentMethod': 'Payment Method', 'Count': 'Count'})
            st.plotly_chart(fig6, use_container_width=True)


    # Business Insights
    st.subheader("Business Insights")
    st.write("This section provides actionable insights derived from customer data analysis to help identify key trends, behaviors, and opportunities for growth.")


   


# Load Lottie animation
    # lottie_dashboard = "https://assets1.lottiefiles.com/packages/lf20_o6spyjnc.json"

 # st_lottie(lottie_dashboard, height=300, key="dashboard")