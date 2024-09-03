import streamlit as st
import pandas as pd
import numpy as np
import base64
import os
import sqlite3
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
    username = st.session_state['username']

    st.title('Telco Churn Analysis')

    # Display Lottie animation for the data page
    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.write("""
            Welcome to the **Telco Churn Analysis** dashboard. This tool provides comprehensive insights into customer churn through two primary analysis types:

            1. **Exploratory Data Analysis (EDA):** Explore customer data through visualizations to identify key demographic and account trends that can influence churn.
            2. **Key Performance Indicators (KPIs):** Analyze critical metrics such as total customers, retention rates, and revenue, with the ability to filter and compare data.

            Select the type of analysis you wish to conduct from the dropdown menu and dive into the data to uncover actionable insights that can drive strategic decisions for customer retention and growth.
            """)
        with right_column:
            display_lottie_on_page("Analytics Dashboard")

    # Add selectbox to choose between EDA and KPIs
    selected_analysis = st.selectbox('Select Analysis Type', ['', '🔍 Exploratory Data Analysis (EDA)', '📊 Key Performance Indicators (KPIs)'], index=0)
    
    # Load the initial data from a local file
    @st.cache_data(persist=True, show_spinner=False)
    def load_initial_data():
        df = pd.read_csv('./data/LP2_train_final.csv')
        return df
    
    initial_df = load_initial_data()
    data_source = 'initial'  # Flag to identify the source of the DataFrame

    def load_most_recent_table(username):
        # Define the path for the user's SQLite database
        db_path = f"./data/{username}/{username}.db"

        if not os.path.exists(db_path):
            st.error("No database found for the user. Please ensure a file has been uploaded on the data overview page.")
            return None, None

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)

        # Get the list of tables and their creation order
        tables_query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY tbl_name DESC LIMIT 1;
        """
        try:
            most_recent_table = conn.execute(tables_query).fetchone()

            if most_recent_table:
                table_name = most_recent_table[0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                global data_sourc
                data_source = 'uploaded'  # Update flag to indicate data is from upload
            else:
                st.error("No tables found in the database.")
                return None, None
        except Exception as e:
            st.error(f"An error occurred while loading the table: {e}")
            return None, None
        finally:
            conn.close()

        return df, table_name

    # Load data from the uploaded file or use the initial data
    if st.button("Preview Template Dataset"):
        st.session_state['data_source'] = 'initial'
        df = initial_df

    else:
        uploaded_df, table_name = load_most_recent_table(username)
        df = uploaded_df if uploaded_df is not None else initial_df

    if df is not None:
        st.write(f"Most recent table: {table_name}" if data_source == 'uploaded' else "Using initial data")

    # Ensure numerical columns are correctly typed
    df = df.apply(pd.to_numeric, errors='ignore')

    # Define the list of specific columns to check and coerce
    columns_to_coerce = ['Tenure', 'MonthlyCharges', 'TotalCharges', 'AvgMonthlyCharges', 'MonthlyChargesToTotalChargesRatio']

    try:
        # Ensure numerical columns are correctly typed for specific columns
        for column in columns_to_coerce:
            if column in df.columns and df[column].dtype == 'object':
                df[column] = pd.to_numeric(df[column], errors='coerce')
    except Exception as e:
        st.error(f"An error occurred while processing the column '{column}': {e}")
        st.warning(
            """
            Please refer to the Data Overview page to apply the correct data structure, 
            ensuring numerical columns have strictly numeric values and categorical columns have strictly categorical values.
            """
        )
        st.stop()  

    # Handle missing values
    numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    numerical_imputer = SimpleImputer(strategy='median')
    df[numerical_columns] = numerical_imputer.fit_transform(df[numerical_columns])

    # Create a function to apply filters
    def apply_filters(df):
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

        filtered_data = df.copy()
        for column, (min_val, max_val) in slider_values.items():
            filtered_data = filtered_data[
                (filtered_data[column] >= min_val) & (filtered_data[column] <= max_val)
            ]
        return filtered_data

    # Apply filters to the data
    filtered_data = apply_filters(df)

    if selected_analysis == '':
        st.write("Please select an analysis type to begin.")

    elif selected_analysis == '🔍 Exploratory Data Analysis (EDA)':
        st.subheader("🕵🏾‍♂️ Churn EDA Dashboard")
        st.write(
            "This dashboard provides an exploratory analysis of customer churn data. The visualizations help identify key demographic and account characteristics, correlations, and trends that can guide strategic decisions. Use the filters and plots to understand customer behavior and identify potential areas for improvement."
        )
        
        # Adjust grid layout to 2x2 for better alignment
        st.markdown("#### Customer Demographic Analysis")
        st.write(
            "This section analyzes customer demographics to understand the distribution of key attributes such as gender, age, and relationships. By examining these factors, you can uncover patterns that might influence customer retention and acquisition."
        )
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                gender_plot = px.histogram(filtered_data, x="Gender", color="Churn", barmode="group", title="Gender Distribution")
                st.plotly_chart(gender_plot, use_container_width=True)

            with col2:
                senior_citizen_plot = px.histogram(filtered_data, x="SeniorCitizen", color="Churn", barmode="group", title="Senior Citizen Distribution")
                st.plotly_chart(senior_citizen_plot, use_container_width=True)
 
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                partner_plot = px.histogram(filtered_data, x="Partner", color="Churn", barmode="group", title="Partner Distribution")
                st.plotly_chart(partner_plot, use_container_width=True)
            
            with col2:
                dependents_plot = px.histogram(filtered_data, x="Dependents", color="Churn", barmode="group", title="Dependents Distribution")
                st.plotly_chart(dependents_plot, use_container_width=True)

        st.markdown("#### Customer Account Analysis")        
        st.write(
            "This section provides insights into customer account characteristics, including monthly and total charges, as well as tenure. The distributions and histograms reveal patterns in spending and account duration, which are crucial for understanding customer value and predicting churn."
        )
        with st.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                monthly_charges_plot = px.histogram(filtered_data, x='MonthlyCharges', nbins=20, color='Churn', title='Monthly Charges Distribution')
                st.plotly_chart(monthly_charges_plot, use_container_width=True)

            with col2:
                total_charges_plot = px.histogram(filtered_data, x='TotalCharges', nbins=20, color='Churn', title='Total Charges Distribution')
                st.plotly_chart(total_charges_plot, use_container_width=True)

            with col3:                         
                tenure_plot = px.histogram(filtered_data, x='Tenure', nbins=20, color='Churn', title='Tenure Distribution')
                st.plotly_chart(tenure_plot, use_container_width=True)   

        with st.container():
            filtered_data['Churn'] = filtered_data['Churn'].map({'Yes': 1, 'No': 0})
            col1, col2 = st.columns(2)

            with col1:
                # Correlation Heatmap
                corr_matrix = filtered_data[["Churn", "MonthlyCharges", "TotalCharges", "Tenure"]].dropna().corr()

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
                    filtered_data[["Churn", "Tenure", "MonthlyCharges", "TotalCharges"]],
                    dimensions=["TotalCharges", "Tenure", "MonthlyCharges"],
                    color="Churn",
                    title="Pairplot"
                )
                st.plotly_chart(pairplot_fig)

        st.markdown("#### Customer Contractual Analysis")
        st.write(
            "This section examines customer contracts and payment methods. It provides an overview of contract types, payment methods, and billing preferences, which can offer insights into customer loyalty and potential areas for optimizing pricing strategies."
        )
        with st.container():
            filtered_data['Churn'] = filtered_data['Churn'].map({1: 'Yes', 0: 'No'})
            col1, col2, col3 = st.columns(3)

            with col1:
                contract_plot = px.histogram(filtered_data, x="Contract", color="Churn", barmode="group", title="Contract Distribution")
                st.plotly_chart(contract_plot, use_container_width=True)

            with col2:
                payment_method_plot = px.histogram(filtered_data, x="PaymentMethod", color="Churn", barmode="group", title="Payment Method Distribution")
                st.plotly_chart(payment_method_plot, use_container_width=True)

            with col3:
                paperless_billing_plot = px.histogram(filtered_data, x="PaperlessBilling", color="Churn", barmode="group", title="Paperless Billing Distribution")
                st.plotly_chart(paperless_billing_plot, use_container_width=True)

        st.markdown("#### Customer Subscription Analysis")
        st.write(
            "This section explores customer service subscriptions, including phone, internet, and tech support services. It highlights the distribution of these services among customers and their relationship with churn behavior."
        )

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                phone_service_plot = px.histogram(filtered_data, x="PhoneService", color="Churn", barmode="group", title="Phone Service Distribution")
                st.plotly_chart(phone_service_plot, use_container_width=True)

            with col2:
                multiple_lines_plot = px.histogram(filtered_data, x="MultipleLines", color="Churn", barmode="group", title="Multiple Lines Distribution")
                st.plotly_chart(multiple_lines_plot, use_container_width=True)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                internet_service_plot = px.histogram(filtered_data, x="InternetService", color="Churn", barmode="group", title="Internet Service Distribution")
                st.plotly_chart(internet_service_plot, use_container_width=True)

            with col2:
                techsupport_plot = px.histogram(filtered_data, x="TechSupport", color="Churn", barmode="group", title="Tech Support Distribution")
                st.plotly_chart(techsupport_plot, use_container_width=True)

        if data_source == 'initial':
            st.markdown("""
            #### Key Business Insights

            ##### 1. Customer Demographic Analysis
            - Churn rates are consistent across genders, indicating that gender is not a major factor in predicting churn.
            - Senior citizens show higher churn rates, suggesting they might have unique needs or challenges with the service.
            - Customers with partners are less likely to churn, hinting at a correlation between relationship stability and customer loyalty.
            - Customers with dependents also exhibit lower churn rates, possibly due to family responsibilities influencing their decision to stay.

            ##### 2. Customer Account Analysis
            - Higher monthly charges are associated with increased churn, indicating cost as a significant factor in customer retention.
            - Total charges over time don’t strongly correlate with churn, suggesting that long-term cost might be less impactful than expected.
            - Churn is more common among customers with shorter tenure, highlighting the need for early engagement strategies to boost retention.

            ##### 3. Customer Contractual Analysis
            - Month-to-month contracts have a significantly higher churn rate compared to one-year or two-year contracts, suggesting that encouraging longer-term commitments could reduce churn.
            - Customers using electronic checks are more likely to churn, potentially indicating dissatisfaction with this payment method.
            - Customers who opt for paperless billing tend to have higher churn rates, which could imply that these customers, being more digitally savvy, are more open to exploring other service options.

            ##### 4. Customer Subscription Analysis
            - Most customers use phone services, and while churn is significant, a larger portion of these customers do not churn. Customers without phone service show lower churn rates overall.
            - Most customers do not have multiple lines. The churn rate is almost the same for customers with and without multiple lines, but in both cases, the number of customers who do not churn is significantly higher than those who do.
            - Fiber optic internet service users have higher churn rates compared to DSL users, which may point to dissatisfaction with the value or quality of fiber optic service.
            - The lack of tech support is strongly linked to higher churn, emphasizing the importance of providing reliable tech support to retain customers.
            """)


    elif selected_analysis == '📊 Key Performance Indicators (KPIs)':
        st.subheader("📈 Churn KPI Dashboard")

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

        # Apply a map to the data frame for the chun column
        df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
        filtered_data['Churn'] = filtered_data['Churn'].map({'Yes': 1, 'No': 0})
  
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
        st.markdown("#### Distribution of Features")
        st.markdown("""
        This section visualizes the distribution of key features in the dataset. It includes:
        - **Contract Distribution:** Shows the breakdown of customer contracts.
        - **Payment Method Distribution:** Displays how customers are distributed across different payment methods.
        - **Internet Service Distribution:** Illustrates how customers are distributed across various internet service types.
        - **Phone Service Distribution:** Demonstrates the distribution of customers based on their phone service options.
        """)

        # Distribution plots
        col1, col2 = st.columns(2)

        with col1:
            # Plot: Contract Distribution
            contract_distribution = filtered_data['Contract'].value_counts()
            fig_contract = px.pie(contract_distribution, values=contract_distribution.values, names=contract_distribution.index, hole=0.3, title="Contract Distribution")
            st.plotly_chart(fig_contract, use_container_width=True)

            # Plot: Internet Service Distribution
            internet_service_distribution = filtered_data['InternetService'].value_counts()
            fig_internet_service_distribution = px.pie(internet_service_distribution, values=internet_service_distribution.values, names=internet_service_distribution.index, hole=0.3, title="Internet Service Distribution")
            st.plotly_chart(fig_internet_service_distribution, use_container_width=True)

        with col2:
            # Plot: Payment Method Distribution
            payment_method_distribution = filtered_data['PaymentMethod'].value_counts()
            fig_payment_method_distribution = px.pie(payment_method_distribution, values=payment_method_distribution.values, names=payment_method_distribution.index, hole=0.3, title="Payment Method Distribution")
            st.plotly_chart(fig_payment_method_distribution, use_container_width=True)

            # Plot: Phone Service Distribution
            phone_service_distribution = filtered_data['PhoneService'].value_counts()
            fig_phone_service_distribution = px.pie(phone_service_distribution, values=phone_service_distribution.values, names=phone_service_distribution.index, hole=0.3, title="Phone Service Distribution")
            st.plotly_chart(fig_phone_service_distribution, use_container_width=True)


        # Section: Comparing Feature Parameters
        st.markdown("#### Comparing Feature Parameters Based on Churn Rate")
        st.markdown("""
        This section provides insights into how different feature parameters relate to churn rates. It includes:
        - **Churn Rate by Gender:** Compares churn rates across different genders.
        - **Churn Rate Over Tenure:** Shows how churn rate changes with customer tenure.
        - **Churn Rate by Contract Type:** Examines how churn rates vary with different contract types.
        - **Churn Rate by Payment Method:** Investigates churn rates based on different payment methods.
        - **Average Monthly Charges by Contract Type:** Analyzes average charges based on contract type.
        - **Total Monthly Charges by Contract Type:** Displays total monthly charges for each contract type.
        - **Churn Rate by Internet Service:** Looks at how internet service type affects churn rates.
        - **Churn Rate by Phone Service:** Analyzes churn rates based on whether customers have phone service.
        """)

        # Comparing Feature Parameters Plot
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Plot: Churn Rate by Gender
                churn_by_gender = filtered_data.groupby('Gender')['Churn'].mean().reset_index()
                churn_by_gender['Churn'] = churn_by_gender['Churn'] * 100
                fig_gender_churn = px.bar(churn_by_gender, x='Gender', y='Churn', title='Churn Rate by Gender')
                st.plotly_chart(fig_gender_churn, use_container_width=True)

            with col2:
                # Plot: Line Chart for Churn Rate over Tenure
                churn_rate_by_tenure = filtered_data.groupby('Tenure')['Churn'].mean().reset_index()
                fig_churn_tenure = px.line(churn_rate_by_tenure, x='Tenure', y='Churn', title='Churn Rate over Tenure')
                st.plotly_chart(fig_churn_tenure, use_container_width=True)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Plot: Churn Rate by Contract Type
                churn_by_contract = filtered_data.groupby('Contract')['Churn'].mean().reset_index()
                churn_by_contract['Churn'] = churn_by_contract['Churn'] * 100
                fig_contract_churn = px.bar(churn_by_contract, x='Contract', y='Churn', title='Churn Rate by Contract Type')
                st.plotly_chart(fig_contract_churn, use_container_width=True)

            with col2:
                # Plot: Churn Rate by Payment Method
                churn_by_payment_method = filtered_data.groupby('PaymentMethod')['Churn'].mean().reset_index()
                churn_by_payment_method['Churn'] = churn_by_payment_method['Churn'] * 100
                fig_churn_by_payment_method = px.bar(churn_by_payment_method, x='PaymentMethod', y='Churn', title='Churn Rate by Payment Method')
                st.plotly_chart(fig_churn_by_payment_method, use_container_width=True)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Plot: Average Monthly Charges by Contract Type
                avg_charges_by_contract = filtered_data.groupby('Contract')['MonthlyCharges'].mean().reset_index()
                fig_avg_contract_charges = px.bar(avg_charges_by_contract, x='Contract', y='MonthlyCharges', title='Avg. Monthly Charges by Contract Type')
                st.plotly_chart(fig_avg_contract_charges)

            with col2:
                # Plot: Total Monthly Charges by Contract Type
                total_charges_by_contract = filtered_data.groupby('Contract')['TotalCharges'].mean().reset_index()
                fig_total_contract_charges = px.bar(total_charges_by_contract, x='Contract', y='TotalCharges', title='Total Monthly Charges by Contract Type')
                st.plotly_chart(fig_total_contract_charges)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:           
                # Plot: Churn Rate by Internet Service
                churn_by_internet_service = filtered_data.groupby('InternetService')['Churn'].mean().reset_index()
                churn_by_internet_service['Churn'] = churn_by_internet_service['Churn'] * 100
                fig_churn_by_internet_service = px.bar(churn_by_internet_service, x='InternetService', y='Churn', title='Churn Rate by Internet Service')
                st.plotly_chart(fig_churn_by_internet_service)

            with col2:
                # Plot: Churn Rate by Phone Service
                churn_by_phone_service = filtered_data.groupby('PhoneService')['Churn'].mean().reset_index()
                churn_by_phone_service['Churn'] = churn_by_phone_service['Churn'] * 100
                fig_churn_by_phone_service = px.bar(churn_by_phone_service, x='PhoneService', y='Churn', title='Churn Rate by Phone Service')
                st.plotly_chart(fig_churn_by_phone_service)

        # Sample KPI data
        kpi_data = {
            'KPI': ['Total Customers', 'Total Customers Retained', 'Churn Rate', 'Avg. Tenure', 'Avg. Monthly Charges', 'Total Revenue'],
            'Value': [f"{total_customers:,}", f"{total_customers_retained:,}", f"{churn_rate:.2f}%", f"{avg_tenure:.1f} months", f"${avg_monthly_charges:.2f}", f"${total_revenue:,.2f}"]
        }

        # Create DataFrame
        kpi_df = pd.DataFrame(kpi_data)
        kpi_df.set_index('KPI', inplace=True)

        # Function to apply conditional formatting based on the value
        def color_kpi_value(value):
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
        styled_df = kpi_df.style.applymap(color_kpi_value, subset=['Value'])

        # Apply the highlight_churn function to the entire row
        styled_df = styled_df.apply(highlight_churn, axis=1)

        # Display the styled DataFrame in Streamlit
        st.markdown("#### Key Performance Indicators (KPIs)")
        st.table(styled_df)
else:
    st.warning("Please login to access this page.")


# Function to convert an image to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Image paths
image_paths = ["./assets/favicon.png"]

# Convert images to base64
image_b64 = [image_to_base64(img) for img in image_paths]

# Need Help Section
st.markdown("Need help? Contact support at [sdi@azubiafrica.org](mailto:sdi@azubiafrica.org)")

st.write("---")

# Contact Information Section
st.markdown(
f"""
<div style="display: flex; justify-content: space-between; align-items: center;">
    <div style="flex: 1;">
        <h2>Contact Us</h2>
        <p>For inquiries, please reach out to us:</p>
        <p>📍 Address: Accra, Ghana</p>
        <p>📞 Phone: +233 123 456 789</p>
        <p>📧 Email: sdi@azubiafrica.org</p>
    </div>
    <div style="flex: 0 0 auto;">
        <img src="data:image/png;base64,{image_b64[0]}" style="width:100%";" />
    </div>
</div>
""",
unsafe_allow_html=True
)






# st.subheader("Business Insights")
# st.markdown("""
# - **Gender and Churn Rate**: The churn rate is consistent across both male and female customers, indicating that gender is not a significant factor in predicting churn.
# - **Senior Citizens and Churn**: A lower percentage of senior citizens are customers, but those who are tend to have a higher churn rate, suggesting the need for targeted retention strategies for this group.
# - **Partner and Dependent Influence**: Customers with partners or dependents are less likely to churn, which could indicate that these customers have more stable relationships with the service.
# - **Monthly Charges and Churn**: Customers with higher monthly charges tend to have a higher churn rate. This suggests that customers may feel the service is not providing sufficient value for the cost, highlighting a potential area for pricing strategy adjustments.
# - **Tenure and Churn**: Customers with shorter tenure are more likely to churn, indicating that early-stage customers need more engagement or incentives to continue with the service.
# - **Contract Type and Churn**: Month-to-month contract customers show a significantly higher churn rate compared to those on longer-term contracts. This suggests that encouraging customers to commit to longer-term contracts could reduce churn.
# - **Payment Method and Churn**: Electronic check payment method users exhibit a higher churn rate, which could imply dissatisfaction with the payment process or related services.
# - **Paperless Billing and Churn**: Customers with paperless billing have a higher churn rate, which might indicate that these customers are more tech-savvy and have higher service expectations or a greater tendency to explore competitors.
# """)


# import streamlit as st
# import os
# import numpy as np
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go


# user_choice = st.sidebar.radio("Display a Dashboard", options = ["EDA Dashboard", "Analytical Dashboard"], key = "selected_dashboard")

# if st.session_state["selected_dashboard"] == "EDA Dashboard":
#     st.markdown("<h1 style='color: lightblue;'> 🔍 Exploratory Data Analysis</h1>", unsafe_allow_html=True)
#     # Load data
#     @st.cache_data(persist = True)
#     def load_data():
#         if os.path.exists("./data/LP2_train_final.csv"):
#             data = pd.read_csv("./data/LP2_train_final.csv")
#         else:
#             st.error("Data file not found.")
#         return data

#     df = load_data()
#     st.write(df.head())

#     # Left, Middle, Right Columns
#     left_column, middle_column, right_column = st.columns(3)

#     # Boxplot for MonthlyCharges
#     with left_column:
#         fig = px.box(df, y="MonthlyCharges", title="Boxplot of Monthly Charges", color_discrete_sequence=["#C70039"])
#         st.plotly_chart(fig)

#     # Boxplot for TotalCharges
#     with middle_column:
#         fig = px.box(df, y="TotalCharges", title="Boxplot of Total Charges", color_discrete_sequence=["#900C3F"])
#         st.plotly_chart(fig)

#     # Correlation Heatmap with Annotations and No Color Bar
#     with right_column:
#         corr_matrix = df[["TotalCharges", "MonthlyCharges", "Tenure"]].dropna().corr()

#         # Annotate the heatmap with correlation values
#         heatmap = go.Figure(data=go.Heatmap(
#             z=corr_matrix.values,
#             x=corr_matrix.columns,
#             y=corr_matrix.columns,
#             colorscale="RdBu",
#             text=corr_matrix.values,  # Add the correlation values as text
#             texttemplate="%{text:.2f}",  # Format the text to 2 decimal places
#             showscale=True  # Remove the color bar
#         ))

#         heatmap.update_layout(
#             title="Correlation Matrix",
#             xaxis_nticks=36
#         )
    
#         st.plotly_chart(heatmap)

#     # Pair Plot
#     pairplot_fig = px.scatter_matrix(
#         df[["Churn", "TotalCharges", "Tenure", "MonthlyCharges"]],
#         dimensions=["TotalCharges", "Tenure", "MonthlyCharges"],
#         color="Churn",
#         title="Pairplot"
#     )
#     st.plotly_chart(pairplot_fig)

#     # Left, Middle, Right Columns for Countplots
#     left, middle, right = st.columns(3)

#     # Countplot for SeniorCitizen
#     with left:
#         countplot_fig = px.histogram(df, x="Gender", color="Churn", barmode="group", title="Distribution of SeniorCitizen")
#         st.plotly_chart(countplot_fig)

#     # Countplot for InternetService
#     with middle:
#         countplot_fig = px.histogram(df, x="InternetService", color="Churn", barmode="group", title="Distribution of InternetService")
#         st.plotly_chart(countplot_fig)

#     # Countplot for Contract
#     with right:
#         countplot_fig = px.histogram(df, x="Contract", color="Churn", barmode="group", title="Distribution of Contract")
#         st.plotly_chart(countplot_fig)



# if st.session_state["selected_dashboard"] == "Analytical Dashboard":

#     # Title of dashboard
#     st.markdown("<h1 style='color: lightblue;'> 💡 Churn Indicator Dashboard</h1>", unsafe_allow_html=True)

#     @st.cache_data(persist = True)
#     def load_data():
#         if os.path.exists("./data/LP2_train_final.csv"):
#             data = pd.read_csv("./data/LP2_train_final.csv")
#         else:
#             st.error("Data file not found.")
#         return data

#     df = load_data()

#     # Sidebar widgets
#     st.sidebar.header("Filter Options")

#     # Tenure slider
#     tenure = st.sidebar.slider("Tenure", 0, int(df["Tenure"].max()), (0, int(df["Tenure"].max())))

#     # Total Charges range slider
#     total_charges = st.sidebar.slider("Total Charges", float(df["TotalCharges"].min()), float(df["TotalCharges"].max()), (float(df["TotalCharges"].min()), float(df["TotalCharges"].max())))

#     # Monthly Charges range slider
#     monthly_charges = st.sidebar.slider("Monthly Charges", float(df["MonthlyCharges"].min()), float(df["MonthlyCharges"].max()), (float(df["MonthlyCharges"].min()), float(df["MonthlyCharges"].max())))

#     # Filter the data based on sidebar input
#     filtered_df = df[(df["Tenure"] >= tenure[0]) & (df["Tenure"] <= tenure[1]) &
#                     (df["TotalCharges"] >= total_charges[0]) & (df["TotalCharges"] <= total_charges[1]) &
#                     (df["MonthlyCharges"] >= monthly_charges[0]) & (df["MonthlyCharges"] <= monthly_charges[1])]


#     # Calculate deltas for metrics
#     total_monthly_charge = filtered_df["MonthlyCharges"].sum()
#     total_charge = filtered_df["TotalCharges"].sum()
#     total_customers_retained = len(filtered_df[filtered_df["Churn"] == "No"])
#     churn_rate = (len(filtered_df[filtered_df["Churn"] == "Yes"]) / len(filtered_df)) * 100

#     # Calculate unfiltered values
#     unfiltered_monthly_charge = df["MonthlyCharges"].sum()
#     unfiltered_total_charge = df["TotalCharges"].sum()
#     unfiltered_customers_retained = len(df[df["Churn"] == "No"])

#     # Calculate deltas
#     monthly_charge_delta = (total_monthly_charge - unfiltered_monthly_charge) / unfiltered_monthly_charge * 100
#     total_charge_delta = (total_charge - unfiltered_total_charge) / unfiltered_total_charge * 100
#     customers_retained_delta = (total_customers_retained - unfiltered_customers_retained) / unfiltered_customers_retained * 100


#     left_column, middle_column, right_column = st.columns(3)

#     with left_column:
#         st.metric("Total Monthly Charge", f"${total_monthly_charge/1e3:,.2f}K", delta=f"{monthly_charge_delta:.2f}%")

#     with middle_column:
#         st.metric("Total Charge", f"${total_charge/1e6:,.2f}M", delta=f"{total_charge_delta:.2f}%")

#     with right_column:
#         st.metric("Total Customers Retained", total_customers_retained, delta=f"{customers_retained_delta:.2f}%")


#     # Row 1: Churn Rate by Tenure and Churn Rate by InternetService
#     col1, col2 = st.columns(2)
#     with col1:
#         churn_by_tenure = filtered_df.groupby("Tenure")["Churn"].value_counts(normalize=True).unstack().fillna(0)
#         fig_tenure = px.line(churn_by_tenure, y="Yes", title="Churn Rate by Tenure", width=450, height=300)
#         st.plotly_chart(fig_tenure)

#     with col2:
#         gauge_fig = go.Figure(go.Indicator(
#             mode = "gauge+number",
#             value = churn_rate,
#             title = {"text": "Churn Rate (%)"},
#             gauge = {
#                 "axis": {"range": [0, 100]},
#                 "bar": {"color": "blue"},
#                 "steps": [
#                     {"range": [0, 30], "color": "green"},
#                     {"range": [30, 70], "color": "yellow"},
#                     {"range": [70, 100], "color": "red"}],
#                 "threshold": {
#                     "line": {"color": "black", "width": 4},
#                     "thickness": 0.75,
#                     "value": churn_rate}}))
#         gauge_fig.update_layout(width=450, height=300)
#         st.plotly_chart(gauge_fig)

#     # Row 2: Churn Rate by Gender and Churn Rate by Contract
#     col1, col2 = st.columns(2)
#     with col1:
#         churn_by_internet_service = filtered_df[filtered_df["Churn"] == "Yes"].groupby("InternetService").size()
#         fig_internet_service = px.pie(values=churn_by_internet_service, names=churn_by_internet_service.index, title="Churn Rate by InternetService", width=450, height=300)
#         st.plotly_chart(fig_internet_service)

#     with col2:
#         churn_by_contract = filtered_df[filtered_df["Churn"] == "Yes"].groupby("Contract").size()
#         fig_contract = px.bar(x=churn_by_contract.index, y=churn_by_contract.values, labels={"x":"Contract", "y":"Churn Rate (%)"}, title="Churn Rate by Contract", width=450, height=300)
#         st.plotly_chart(fig_contract)
 