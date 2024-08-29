import streamlit as st
import pandas as pd
import base64
from utils.login import invoke_login_widget
from utils.lottie import display_lottie_on_page

# Invoke the login form
invoke_login_widget('Data Overview')

# Fetch the authenticator from session state
authenticator = st.session_state.get('authenticator')

if not authenticator:
    st.error("Authenticator not found. Please check the configuration.")
    st.stop()

# Check authentication status
if st.session_state.get("authentication_status"):
    st.title("Data Navigator")

    # Display Lottie animation for the data page
    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.write(
                """
                The Data Navigator page allows you to upload, view, and analyze datasets. 
                Start by exploring a template dataset or uploading yours. Detailed column descriptions 
                are provided to help you understand the structure and content required for your dataset. 
                Additionally, you can interactively filter the data and review a summary of the displayed dataset.
                """
            )
        with right_column:
            display_lottie_on_page("Data Overview")

    # Load the initial data from a local file
    @st.cache_data(persist=True, show_spinner=False)
    def load_initial_data():
        df = pd.read_csv('./data/LP2_train_final.csv')
        return df
    
    initial_df = load_initial_data()
    
    st.sidebar.header("Data Upload")
    uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

    def load_uploaded_data(file):
        if file is not None:
            try:
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                elif file.name.endswith(".xlsx"):
                    df = pd.read_excel(file)
                return df
            except Exception as e:
                st.error(f"Error: {e}")
                return None
        return None

    # Load data from the uploaded file or use the initial data
    uploaded_df = load_uploaded_data(uploaded_file)
    df = uploaded_df if uploaded_df is not None else initial_df


    # Check if the dataset is the initial one or an uploaded one
    if uploaded_file is None:
        st.subheader("Template Dataset")
        st.write(
            """
            Displays the template dataset as a reference. 
            This section serves as the starting point for data exploration, 
            providing a visual representation of the data structure.
            """
        )
    else:
        st.subheader("Uploaded Dataset")
        st.write(
            """
            Displays the dataset uploaded by the user. 
            This section serves as the starting point for data exploration, 
            providing a visual representation of the data structure.
            """
        )
    
    # Ensure 'customer_id' is set as the index
    df.set_index('customerID', inplace=True)

    # Ensure numerical columns are correctly typed
    df = df.apply(pd.to_numeric, errors='ignore')

    # Sidebar widgets for numerical filters
    st.sidebar.header("Numerical Filter Options")

    if df is not None:
        # Display the DataFrame
        st.dataframe(df)

        st.subheader("Data Summary")
        st.write(
            """
            Offers a quick statistical overview of the dataset. 
            This summary provides key insights into the data, such as mean, median, 
            and distribution, helping users understand the general characteristics of their data.
            """
        )

        # Summary for numerical features
        numeric_summary_df = df.describe().T.reset_index()
        numeric_summary_df.rename(columns={'index': 'Feature'}, inplace=True)
        st.write("##### Numerical Features Summary")
        st.dataframe(numeric_summary_df.set_index('Feature'))

        # Summary for categorical features
        categorical_summary = df.select_dtypes(include=['object']).describe().T
        categorical_summary['unique'] = df.select_dtypes(include=['object']).nunique()
        categorical_summary['top'] = df.select_dtypes(include=['object']).mode().iloc[0]
        categorical_summary['freq'] = df.select_dtypes(include=['object']).apply(pd.Series.value_counts).max()

        categorical_summary = categorical_summary.reset_index()
        categorical_summary.rename(columns={'index': 'Feature'}, inplace=True)
        
        st.write("##### Categorical Features Summary")
        st.dataframe(categorical_summary.set_index('Feature'))

        # Interactive filters
        st.subheader("Filter Data")
        st.write(
            """
            Enables interactive filtering of the dataset based on specific columns. 
            This tool allows users to drill down into the data, focusing on subsets of interest, 
            and making the exploration more targeted and efficient.
            """
        )

        # Dynamically detect numerical columns
        numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

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

        # First layer filter for categorical columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if categorical_columns:
            selected_column = st.selectbox("Select a categorical feature to filter by", categorical_columns)
            unique_values = df[selected_column].unique()
            selected_value = st.selectbox(f"Select a value from {selected_column}", unique_values)
            filtered_data = df[df[selected_column] == selected_value]

            # Apply numerical filters to the filtered data
            for column, (min_val, max_val) in slider_values.items():
                filtered_data = filtered_data[
                    (filtered_data[column] >= min_val) & (filtered_data[column] <= max_val)
                ]

            st.write(f"##### Filtered Data (showing rows where {selected_column} is {selected_value}):")
            st.dataframe(filtered_data)

            # Show summary for filtered data
            st.write("##### Numerical Features Summary for Filtered Data")
            numeric_filtered_summary_df = filtered_data.describe().T.reset_index()
            numeric_filtered_summary_df.rename(columns={'index': 'Feature'}, inplace=True)
            st.dataframe(numeric_filtered_summary_df.set_index('Feature'))

            categorical_filtered_summary = filtered_data.select_dtypes(include=['object']).describe().T
            categorical_filtered_summary['unique'] = filtered_data.select_dtypes(include=['object']).nunique()
            categorical_filtered_summary['top'] = filtered_data.select_dtypes(include=['object']).mode().iloc[0]
            categorical_filtered_summary['freq'] = filtered_data.select_dtypes(include=['object']).apply(pd.Series.value_counts).max()

            categorical_filtered_summary = categorical_filtered_summary.reset_index()
            categorical_filtered_summary.rename(columns={'index': 'Feature'}, inplace=True)
            
            st.write("##### Categorical Features Summary for Filtered Data")
            st.dataframe(categorical_filtered_summary.set_index('Feature'))

        else:
            st.write("No categorical columns available for filtering.")

        st.subheader("Column Description")
        st.write(
            """
            This section provides comprehensive descriptions of each column in the dataset, 
            helping users understand the required structure and content to ensure alignment 
            with analysis objectives. Consistency in data structure is critical, particularly 
            when users upload datasets for analysis on the prediction page. In the data 
            management section, missing values can be replaced with 'Unknown' for analysis. 
            However, when uploading data to the Future Projections page under the Insights 
            and Forecasting section, it is advisable to retain the original missing values 
            to ensure accuracy in forecasting models.
            """
        )

        descriptions = {
            'Gender': 'Whether the customer is male or female',
            'SeniorCitizen': 'Whether a customer is a senior citizen (Yes or No)',
            'Partner': 'Customer has a partner (Yes, No)',
            'Dependents': 'Customer has dependents (Yes, No)',
            'Tenure': 'Months the customer has stayed with the company',
            'PhoneService': 'Customer has phone service (Yes, No)',
            'MultipleLines': 'Customer has multiple lines (Yes, No phone service, No)',
            'InternetService': 'Internet service provider (DSL, Fiber Optic, No)',
            'OnlineSecurity': 'Customer has online security (Yes, No, No internet service)',
            'OnlineBackup': 'Customer has online backup (Yes, No, No internet service)',
            'DeviceProtection': 'Customer has device protection (Yes, No, No internet service)',
            'TechSupport': 'Customer has tech support (Yes, No, No internet service)',
            'StreamingTV': 'Customer has streaming TV (Yes, No, No internet service)',
            'StreamingMovies': 'Customer has streaming movies (Yes, No, No internet service)',
            'Contract': 'Contract term (Month-to-month, One year, Two year)',
            'PaperlessBilling': 'Customer has paperless billing (Yes, No)',
            'PaymentMethod': 'Payment method (Bank transfer (automatic), Credit card (automatic), Electronic check, Mailed check)',
            'MonthlyCharges': 'Monthly charge to the customer',
            'TotalCharges': 'Total charge to the customer',
            'Churn': 'Whether the customer churned (Yes, No)',
            'AvgMonthlyCharges': 'The average amount charged to the customer per month over their tenure.',
            'MonthlyChargesToTotalChargesRatio': 'The ratio of the monthly charges to the total charges, indicating the proportion of total cost that is paid monthly.'            
        }
        for col, desc in descriptions.items():
            st.write(f"- *{col}*: {desc}")

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
