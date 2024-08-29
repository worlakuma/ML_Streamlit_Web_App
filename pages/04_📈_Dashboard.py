import streamlit as st
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import plotly.express as px
import plotly.graph_objects as go
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

    st.title('Telco Churn Analysis')

    # Add selectbox to choose between EDA and KPIs
    selected_analysis = st.selectbox('Select Analysis Type', ['Exploratory Data Analysis (EDA)', 'Key Performance Indicators (KPIs)'])

    # Load Data
    @st.cache_data(persist=True)
    def load_data():
        df = pd.read_csv('./data/LP2_train_final.csv')
        return df

    df = load_data()

    if selected_analysis == 'Exploratory Data Analysis (EDA)':
        st.subheader("📊 Churn EDA Dashboard")
        st.write(
            "This dashboard provides an exploratory analysis of customer churn data. The visualizations help identify key demographic and account characteristics, correlations, and trends that can guide strategic decisions. Use the filters and plots to understand customer behavior and identify potential areas for improvement."
        )
        
        # Load Lottie animation
        display_lottie_on_page("Analytics Dashboard")

        # Sidebar options for data filtering
        st.sidebar.header("Filter Options")
        date_filter = st.sidebar.date_input("Select Date Range", [])

        # Adjust grid layout to 2x2 for better alignment
        st.subheader("Customer Demographic Analysis")
        st.write(
            "This section analyzes customer demographics to understand the distribution of key attributes such as gender, age, and relationships. By examining these factors, you can uncover patterns that might influence customer retention and acquisition."
        )
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                gender_plot = px.bar(df, x='Gender', title='Gender Distribution')
                st.plotly_chart(gender_plot, use_container_width=True)

            with col2:
                senior_citizen_plot = px.bar(df, x='SeniorCitizen', title='Senior Citizen Distribution')
                st.plotly_chart(senior_citizen_plot, use_container_width=True)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                partner_plot = px.bar(df, x='Partner', title='Partner Distribution')
                st.plotly_chart(partner_plot, use_container_width=True)
            
            with col2:
                dependents_plot = px.bar(df, x='Dependents', title='Dependents Distribution')
                st.plotly_chart(dependents_plot, use_container_width=True)

        st.subheader("Customer Account Analysis")
        st.write(
            "This section provides insights into customer account characteristics, including monthly and total charges, as well as tenure. The distributions and histograms reveal patterns in spending and account duration, which are crucial for understanding customer value and predicting churn."
        )
        with st.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce')
                monthly_charges_plot = px.histogram(df, x='MonthlyCharges', nbins=20, title='Monthly Charges Distribution')
                st.plotly_chart(monthly_charges_plot, use_container_width=True)

            with col2:
                df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
                total_charges_plot = px.histogram(df, x='TotalCharges', nbins=20, title='Total Charges Distribution')
                st.plotly_chart(total_charges_plot, use_container_width=True)

            with col3:
                df['Tenure'] = pd.to_numeric(df['Tenure'], errors='coerce')            
                tenure_plot = px.histogram(df, x='Tenure', nbins=20, title='Tenure Distribution')
                st.plotly_chart(tenure_plot, use_container_width=True)   

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Correlation Heatmap with Annotations 
                corr_matrix = df[["TotalCharges", "MonthlyCharges", "Tenure"]].dropna().corr()

                # Annotate the heatmap with correlation values
                heatmap = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale="RdBu",
                    text=corr_matrix.values,  
                    texttemplate="%{text:.2f}",  
                    showscale=True  
                ))

                heatmap.update_layout(
                    title="Correlation Matrix",
                    xaxis_nticks=36
                )

                st.plotly_chart(heatmap)
            
            with col2:
                # Pair Plot
                pairplot_fig = px.scatter_matrix(
                    df[["Churn", "Tenure", "MonthlyCharges", "TotalCharges"]],
                    dimensions=["TotalCharges", "Tenure", "MonthlyCharges"],
                    color="Churn",
                    title="Pairplot"
                )
                st.plotly_chart(pairplot_fig)

        st.subheader("Customer Contract Analysis")
        st.write(
            "This section examines customer contracts and payment methods. It provides an overview of contract types, payment methods, and billing preferences, which can offer insights into customer loyalty and potential areas for optimizing pricing strategies."
        )
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                contract_plot = px.bar(df, x='Contract', title='Contract Distribution')
                st.plotly_chart(contract_plot, use_container_width=True)

            with col2:
                payment_method_plot = px.bar(df, x='PaymentMethod', title='Payment Method Distribution')
                st.plotly_chart(payment_method_plot, use_container_width=True)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                paperless_billing_plot = px.bar(df, x='PaperlessBilling', title='Paperless Billing Distribution')
                st.plotly_chart(paperless_billing_plot, use_container_width=True)

    elif selected_analysis == 'Key Performance Indicators (KPIs)':
        st.subheader("📊 Churn KPI Dashboard")

        st.markdown("""
        This dashboard provides key performance indicators (KPIs) related to customer churn. It offers insights into:

        - **Total Customers:** Number of customers after applying filters.
        - **Total Customers Retained:** Number of customers retained, showing changes after filtering.
        - **Average Tenure:** Average duration customers stay, and how it has changed.
        - **Average Monthly Charges:** Changes in the average charges customers incur.
        - **Total Revenue:** How total revenue has shifted with applied filters.
        - **Churn Rate Gauge:** Visual representation of churn rate changes relative to the unfiltered data.

        Use this dashboard to analyze the impact of various filters on customer retention and overall business metrics.
        """)

        df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})

        # Ensure numerical columns are correctly typed
        df = df.apply(pd.to_numeric, errors='ignore')

        # Sidebar widgets
        st.sidebar.header("Filter Options")

        # Dynamically detect numerical columns
        numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        # Handle missing values
        numerical_imputer = SimpleImputer(strategy='median')
        df[numerical_columns] = numerical_imputer.fit_transform(df[numerical_columns])

        # Create a dictionary to hold slider values for numerical features
        slider_values = {}
        for column in numerical_columns:
            if df[column].dtype == 'int64':
                min_value = int(df[column].min())
                max_value = int(df[column].max())
            else:
                min_value = float(df[column].min())
                max_value = float(df[column].max())
            slider_values[column] = st.sidebar.slider(
                column,
                min_value,
                max_value,
                (min_value, max_value)
            )

        # Apply numerical filters to the data
        filtered_data = df.copy()
        for column, (min_val, max_val) in slider_values.items():
            filtered_data = filtered_data[
                (filtered_data[column] >= min_val) & (filtered_data[column] <= max_val)
            ]
  
        # Calculate unfiltered values
        unfiltered_total_customers = df.shape[0]
        unfiltered_total_customers_retained = len(df[df["Churn"] == 0])
        unfiltered_avg_tenure = df['Tenure'].mean()
        unfiltered_avg_monthly_charges = df['MonthlyCharges'].mean()
        unfiltered_total_revenue = df['TotalCharges'].sum()

        # Create a container to align metrics side by side
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                # KPI 1: Total Customers
                total_customers = filtered_data.shape[0]
                total_customers_delta = (total_customers - unfiltered_total_customers) / unfiltered_total_customers * 100
                st.metric(
                    label="Total Customers", 
                    value=f"{total_customers:,}", 
                    delta=f"{total_customers_delta:.2f}%", 
                    help="This percentage shows how the total number of customers has changed after applying the selected filters."
                )

            with col2:
                # KPI 2: Total Customers Retained
                total_customers_retained = len(filtered_data[filtered_data["Churn"] == 0])
                total_customers_retained_delta = (total_customers_retained - unfiltered_total_customers_retained) / unfiltered_total_customers_retained * 100
                st.metric(
                    label="Total Customers Retained", 
                    value=f"{total_customers_retained:,}", 
                    delta=f"{total_customers_retained_delta:.2f}%",
                    help="This percentage shows the change in the number of customers retained after applying the selected filters."
                )

            with col3:
                # KPI 3: Average Tenure
                avg_tenure = filtered_data['Tenure'].mean()
                avg_tenure_delta = (avg_tenure - unfiltered_avg_tenure) / unfiltered_avg_tenure * 100
                st.metric(
                    label="Avg. Tenure (Months)", 
                    value=f"{avg_tenure:.1f}", 
                    delta=f"{avg_tenure_delta:.2f}%",
                    help="This percentage shows how the average customer tenure has changed after applying the selected filters."
                )

            with col4:
                # KPI 4: Average Monthly Charges
                avg_monthly_charges = filtered_data['MonthlyCharges'].mean()
                avg_monthly_charges_delta = (avg_monthly_charges - unfiltered_avg_monthly_charges) / unfiltered_avg_monthly_charges * 100
                st.metric(
                    label="Avg. Monthly Charges", 
                    value=f"${avg_monthly_charges:.2f}", 
                    delta=f"{avg_monthly_charges_delta:.2f}%",
                    help="This percentage indicates how average monthly charges have changed after applying the selected filters."
                )

            with col5:
                # KPI 5: Total Revenue
                total_revenue = filtered_data['TotalCharges'].sum()
                total_revenue_delta = (total_revenue - unfiltered_total_revenue) / unfiltered_total_revenue * 100
                st.metric(
                    label="Total Revenue", 
                    value=f"${total_revenue/1e6:,.2f}M", 
                    delta=f"{total_revenue_delta:.2f}%",
                    help="This percentage shows how total revenue has shifted after applying the selected filters."
                )

        # Additional KPI: Churn Rate Gauge
        churn_rate = filtered_data['Churn'].mean() * 100
        unfiltered_churn_rate = df['Churn'].mean() * 100

        fig_churn_rate = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=churn_rate,
            number={'suffix': "%", 'valueformat': ".2f"},
            delta={
                'reference': unfiltered_churn_rate, 
                'relative': True, 
                'position': "top", 
                'valueformat': ".2f",
                'suffix': "%",  
                'increasing': {'color': "red"}, 
                'decreasing': {'color': "green"}  
            },
            title={'text': "Churn Rate"},
            gauge={
                "axis": {"range": [0, 100], "tickformat": ".2f%"},
                "bar": {"color": "blue"},
                "steps": [
                    {"range": [0, 30], "color": "green"},
                    {"range": [30, 70], "color": "yellow"},
                    {"range": [70, 100], "color": "red"}
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "thickness": 0.75,
                    "value": churn_rate
                }
            }
        ))

        # Display the gauge in Streamlit
        st.plotly_chart(fig_churn_rate)

        # Display a description or tooltip for the delta value in the gauge
        st.markdown("""
        **Churn Rate Gauge:** The delta value represents the percentage change in churn rate after applying your selected filters, compared to the overall churn rate without any filters. This percentage shows how much the churn rate has increased or decreased relative to the previous value.

        - **Positive Delta (in red):** Indicates that the churn rate has increased after filtering, meaning more customers are leaving.
        - **Negative Delta (in green):** Indicates that the churn rate has decreased after filtering, meaning fewer customers are leaving.

        In simpler terms, the gauge shows not just the current churn rate but also how the current rate compares to the rate before you applied the filters. For example, if the churn rate was 10% before filtering and now it’s 15%, a positive delta of 50% would show that the churn rate increased by half relative to the initial rate. This helps you see the impact of your filters on customer retention more clearly.
        """)

        # Section: Distributions
        st.markdown("#### 📈 Distribution of Features")
        st.markdown("""
        This section visualizes the distribution of key features in the dataset. It includes:
        - **Contract Distribution:** Shows the breakdown of customer contracts.
        - **Payment Method Distribution:** Displays how customers are distributed across different payment methods.
        """)

        # KPI: Contract Distribution
        contract_distribution = filtered_data['Contract'].value_counts()
        fig_contract = px.pie(contract_distribution, values=contract_distribution.values, names=contract_distribution.index, hole=0.3, title="Contract Distribution")
        st.plotly_chart(fig_contract)

        # KPI: Payment Method Distribution
        payment_method_distribution = filtered_data['PaymentMethod'].value_counts()
        fig_payment_method_distribution = px.pie(payment_method_distribution, values=payment_method_distribution.values, names=payment_method_distribution.index, hole=0.3, title="Payment Method Distribution")
        st.plotly_chart(fig_payment_method_distribution)

        # Section: Comparing Feature Parameters
        st.markdown("#### 🔍 Comparing Feature Parameters Based on Churn Rate")
        st.markdown("""
        This section provides insights into how different feature parameters relate to churn rates. It includes:
        - **Churn Rate by Gender:** Compares churn rates across different genders.
        - **Churn Rate by Contract Type:** Examines how churn rates vary with different contract types.
        - **Average Monthly Charges by Contract Type:** Analyzes average charges based on contract type.
        - **Churn Rate Over Tenure:** Shows how churn rate changes with customer tenure.
        """)
        
        # Plot: Churn Rate by Gender
        churn_by_gender = filtered_data.groupby('Gender')['Churn'].mean().reset_index()
        churn_by_gender['Churn'] = churn_by_gender['Churn'] * 100
        fig_gender_churn = px.bar(churn_by_gender, x='Gender', y='Churn', title='Churn Rate by Gender')
        st.plotly_chart(fig_gender_churn)

        # Plot: Churn Rate by Contract Type
        churn_by_contract = filtered_data.groupby('Contract')['Churn'].mean().reset_index()
        churn_by_contract['Churn'] = churn_by_contract['Churn'] * 100
        fig_contract_churn = px.bar(churn_by_contract, x='Contract', y='Churn', title='Churn Rate by Contract Type')
        st.plotly_chart(fig_contract_churn)

        # Plot: Average Monthly Charges by Contract Type
        charges_by_contract = filtered_data.groupby('Contract')['MonthlyCharges'].mean().reset_index()
        fig_contract_charges = px.bar(charges_by_contract, x='Contract', y='MonthlyCharges', title='Avg. Monthly Charges by Contract Type')
        st.plotly_chart(fig_contract_charges)

        # Plot: Line Chart for Churn Rate over Tenure
        churn_rate_by_tenure = filtered_data.groupby('Tenure')['Churn'].mean().reset_index()
        fig_churn_tenure = px.line(churn_rate_by_tenure, x='Tenure', y='Churn', title='Churn Rate over Tenure')
        st.plotly_chart(fig_churn_tenure)

        # Sample KPI data
        kpi_data = {
            'Metric': ['Total Customers', 'Total Customers Retained', 'Churn Rate', 'Avg. Tenure', 'Avg. Monthly Charges', 'Total Revenue'],
            'Value': [f"{total_customers:,}", f"{total_customers_retained:,}", f"{churn_rate:.2f}%", f"{avg_tenure:.1f} months", f"${avg_monthly_charges:.2f}", f"${total_revenue:,.2f}"]
        }

        # Create DataFrame
        kpi_df = pd.DataFrame(kpi_data)
        kpi_df.set_index('Metric', inplace=True)

        # Function to apply conditional formatting based on the value
        def color_metric_value(value):
            if '%' in value:
                percent_value = float(value.strip('%'))
                if percent_value < 30:
                    color = 'green'
                elif 30 <= percent_value < 70:
                    color = 'yellow'
                else:  # percent_value >= 70
                    color = 'red'
            else:
                color = 'lightblue'
            return f'color: {color}'


        # Function to apply conditional formatting
        def highlight_churn(index):
            color = 'background-color: #4B61F5' if index.name == 'Total Revenue' else ''
            return [color] * len(index)

        # Apply the color_negative_red function to the 'Value' column
        styled_df = kpi_df.style.applymap(color_metric_value, subset=['Value'])

        # Apply the highlight_churn function to the entire row
        styled_df = styled_df.apply(highlight_churn, axis=1)

        # Display the styled DataFrame in Streamlit
        st.markdown("#### Key Performance Indicators (KPIs)")
        st.table(styled_df)




 