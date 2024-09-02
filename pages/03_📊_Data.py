import os
import sqlite3
import streamlit as st
from io import BytesIO
import pandas as pd
import time
import base64
from sklearn.impute import SimpleImputer
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
    username = st.session_state['username']

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
                Download options are provided in Excel, Stata, HTML, and JSON formats for professional data handling and analysis.
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

    @st.cache_data(persist=True, show_spinner=False)
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
    
    # Function to save the uploaded file with a unique name
    def save_uploaded_file(file, username):
        # Ensure the directory exists
        save_dir = f"./data/{username}"
        os.makedirs(save_dir, exist_ok=True)

        # Determine the next file number
        existing_files = os.listdir(save_dir)
        file_count = len(existing_files) + 1

        # Save the file
        file_extension = 'csv' if file.name.endswith('.csv') else 'xlsx'
        save_path = os.path.join(save_dir, f"{username}_file{file_count}.{file_extension}")
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())

        return save_path
    
    def validate_data_structure(uploaded_df, template_df):
        # Compare column names
        if list(uploaded_df.columns) != list(template_df.columns):
            return False
        
        # Compare data types
        if uploaded_df.dtypes.tolist() != template_df.dtypes.tolist():
            return False
        
        return True
    
    def save_uploaded_file_as_sqlite(file, username):
        # Ensure the directory exists
        save_dir = f"./data/{username}"
        os.makedirs(save_dir, exist_ok=True)

        # Define the path for the user's SQLite database
        db_path = os.path.join(save_dir, f"{username}.db")

        # Connect to the SQLite database (it will be created if it doesn't exist)
        conn = sqlite3.connect(db_path)

        # Get existing tables and determine the next table number
        existing_tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        existing_tables = [table[0] for table in conn.execute(existing_tables_query).fetchall()]
        
        # Filter tables to find those that match the user's naming pattern
        user_tables = [table for table in existing_tables if table.startswith(f"{username}_table")]

        if user_tables:
            # Extract the numeric part, convert to integer, and find the max value
            max_table_num = max([int(table.split(f"{username}_table")[1]) for table in user_tables])
            next_table_num = max_table_num + 1
        else:
            next_table_num = 1

        # Determine the required padding based on the number of digits in next_table_num
        # Pad the table number with leading zeros based on the length of the highest table number
        pad_length = len(str(next_table_num))
        table_name = f"{username}_table{str(next_table_num).zfill(pad_length)}"

        # Save the DataFrame to the new table in the SQLite database
        try:
            file.seek(0)  # Reset file pointer to the start
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)

            if df is None or df.empty:
                st.error("The uploaded file is empty or improperly formatted. Please upload a valid file.")
                return None, None, None

            # Check if the uploaded data structure matches the template structure
            if not validate_data_structure(df, initial_df):
                st.error("""The structure of the uploaded file does not align with the expected template. 
                         Please review the column descriptions provided below to ensure that the column 
                         names and data types conform to the required specifications.
                         """)
                return None, None, None

            df.to_sql(table_name, conn, index=False, if_exists='replace')

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None, None, None
        finally:
            conn.close()

        return df, table_name, db_path
    
    def generate_download_buttons_original(df):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Download as Excel
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            st.download_button(
                label="Download as Excel",
                data=excel_buffer.getvalue(),
                file_name="data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="original_excel"
            )

        with col2:
            # Download as Stata
            stata_buffer = BytesIO()
            df.to_stata(stata_buffer, write_index=False)
            st.download_button(
                label="Download as Stata",
                data=stata_buffer.getvalue(),
                file_name="data.dta",
                mime="application/x-stata",
                key="original_stata"
            )

        with col3:
            # Download as HTML
            html = df.to_html(index=False).encode('utf-8')
            st.download_button(
                label="Download as HTML",
                data=html,
                file_name="data.html",
                mime="text/html",
                key="original_html"
            )

        with col4:
            # Download as JSON
            json = df.to_json(orient="records").encode('utf-8')
            st.download_button(
                label="Download as JSON",
                data=json,
                file_name="data.json",
                mime="application/json",
                key="original_json"
            )

    
    def generate_download_buttons_filtered(df):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Download as Excel
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            st.download_button(
                label="Download as Excel",
                data=excel_buffer.getvalue(),
                file_name="data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="filtered_excel"
            )

        with col2:
            # Download as Stata
            stata_buffer = BytesIO()
            df.to_stata(stata_buffer, write_index=False)
            st.download_button(
                label="Download as Stata",
                data=stata_buffer.getvalue(),
                file_name="data.dta",
                mime="application/x-stata",
                key="filtered_stata"
            )

        with col3:
            # Download as HTML
            html = df.to_html(index=False).encode('utf-8')
            st.download_button(
                label="Download as HTML",
                data=html,
                file_name="data.html",
                mime="text/html",
                key="filtered_html"
            )

        with col4:
            # Download as JSON
            json = df.to_json(orient="records").encode('utf-8')
            st.download_button(
                label="Download as JSON",
                data=json,
                file_name="data.json",
                mime="application/json",
                key="filtered_json"
            )


    # Load data from the uploaded file or use the initial data
    uploaded_df = load_uploaded_data(uploaded_file)
    df = uploaded_df if uploaded_df is not None else initial_df

    # Check if the dataset is the initial one or an uploaded one
    if uploaded_file is None:
        st.subheader("🧭 Template Dataset")
        st.write(
            """
            Displays the template dataset as a reference. 
            This section serves as the starting point for data exploration, 
            providing a visual representation of the data structure.
            """
        )
        # generate_download_buttons_original(initial_df)
    else:
        st.subheader("📂 Uploaded Dataset")
        st.write(
            """
            Displays the dataset uploaded by the user. 
            This section serves as the starting point for data exploration, 
            providing a visual representation of the data structure.
            """
        )

        # Save the uploaded dataset
        save_path = save_uploaded_file(uploaded_file, username)
        sqldf, table_name, db_path = save_uploaded_file_as_sqlite(uploaded_file, username)

        # Generate download buttons for different file formats
        # generate_download_buttons_original(sqldf)

        # Create a sidebar placeholder for the success message
        success_placeholder = st.sidebar.empty()

        # Show the success message
        success_placeholder.success(f"File successfully uploaded!")

        # Use a time delay to clear the message after 3 seconds
        time.sleep(3)

        # Clear the success message
        success_placeholder.empty()

        # Define the list of specific columns to check and coerce
        columns_to_coerce = ['Tenure', 'MonthlyCharges', 'TotalCharges', 'AvgMonthlyCharges', 'MonthlyChargesToTotalChargesRatio']

        try:
            df = df.apply(pd.to_numeric, errors='ignore') 
            # Ensure numerical columns are correctly typed for specific columns
            for column in columns_to_coerce:
                if column in df.columns and df[column].dtype == 'object':
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                    st.warning("""Although the data remains accessible for exploration, it is highly recommended to 
                               correct the file structure to ensure optimal performance on this page and to
                               guarantee accurate results on the analytics dashboard that truly reflect the
                               recently uploaded dataset.""")
        except Exception as e:
            st.error(f"An error occurred while processing the column '{column}': {e}")
            st.warning(
                """
                Please refer to the Data Overview page to apply the correct data structure, 
                ensuring numerical columns have strictly numeric values and categorical columns have strictly categorical values.
                """
            )
            st.stop() 
        
    # Ensure 'customer_id' is set as the index
    df.set_index('customerID', inplace=True)

    # Ensure numerical columns are correctly typed
    df = df.apply(pd.to_numeric, errors='ignore') 

    # Handle missing values
    numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    numerical_imputer = SimpleImputer(strategy='median')
    df[numerical_columns] = numerical_imputer.fit_transform(df[numerical_columns])

    # Sidebar widgets for numerical filters
    st.sidebar.header("Numerical Filter Options")

    if df is not None:
        # Display the DataFrame
        st.dataframe(df)

        with st.container():
            
            with st.expander("📊 Data Summary", expanded=False):
                st.write(
                """
                Displays a quick statistical overview of the dataset.
                This summary provides key insights into the data, such as mean, median,
                and distribution, helping users understand the general characteristics of their data at a glance. 
                """
                )
           
        # st.subheader("Data Summary")
        # st.write(
        #     """
        #     Offers a quick statistical overview of the dataset. 
        #     This summary provides key insights into the data, such as mean, median, 
        #     and distribution, helping users understand the general characteristics of their data.
        #     """
        # )

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

            with st.expander("🧹 Filter Data", expanded=False):
                st.write(
                    """
                    Enables interactive filtering of the dataset based on specific columns. 
                    This tool allows users to drill down into the data, focusing on subsets of interest,
                    and making the exploration more targeted and efficient.
                    """
                )

        # # Interactive filters
        # st.subheader("🧹 Filter Data")
        # st.write(
        #     """
        #     Enables interactive filtering of the dataset based on specific columns. 
        #     This tool allows users to drill down into the data, focusing on subsets of interest, 
        #     and making the exploration more targeted and efficient.            
        #     """
        # )

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
                unique_customer_ids = df.index.unique()

                if categorical_columns:
                    selected_column = st.selectbox("Select a categorical feature to filter by", categorical_columns)

                    if not selected_column == '':
                        filtered_data = df                        
                        unique_values = df[selected_column].unique()
                        # Add an empty string option as the first option for selecting a value
                        unique_values_options = [''] + list(unique_values)
                        selected_value = st.selectbox(f"Select a value from {selected_column}", unique_values_options, format_func=lambda x: 'All Values' if x == '' else x)

                        # Add filter for specific customer IDs
                        options = [''] + list(unique_customer_ids)  
                        selected_customer_id = st.sidebar.selectbox("Select a Customer ID", options, format_func=lambda x: str(x) if x else 'All Customers')

                        if selected_value == '' and selected_customer_id == '':
                            filtered_data = df
                            st.write("##### Filtered Data (showing all rows)")
                        elif selected_value != '' and selected_customer_id == '':
                            filtered_data = df[df[selected_column] == selected_value]
                            st.write(f"##### Filtered Data (showing rows where {selected_column} is {selected_value})")
                        elif selected_value == '' and selected_customer_id != '':
                            filtered_data = df[df.index == selected_customer_id]
                            st.write(f"##### Filtered Data (showing data for Customer ID {selected_customer_id})")
                        else:
                            # Filter by selected value and customer ID
                            filtered_data = df[(df[selected_column] == selected_value) & (df.index == selected_customer_id)]
                            if filtered_data.empty:
                                st.write(f"##### No data found for Customer ID {selected_customer_id} with {selected_column} = {selected_value}")
                            else:
                                st.write(f"##### Filtered Data (showing data for Customer ID {selected_customer_id} where {selected_column} is {selected_value})")


                        # Apply numerical filters to the filtered data
                        for column, (min_val, max_val) in slider_values.items():
                            filtered_data = filtered_data[
                                (filtered_data[column] >= min_val) & (filtered_data[column] <= max_val)
                            ]

                        # Add filter for specific customer IDs
                        # options = [''] + list(unique_customer_ids)  # Add empty string as the first option
                        # selected_customer_id = st.sidebar.selectbox("Select a Customer ID", options, format_func=lambda x: str(x) if x else 'All Customers')

                        # if not selected_customer_id == '':
                            # filtered_data = filtered_data[filtered_data.index == selected_customer_id]
                            # st.write(f"Showing data for {selected_customer_id}.")

                        # st.write("Download the filtered dataset in one of the following formats:")

                        # generate_download_buttons_filtered(filtered_data)

                        st.dataframe(filtered_data)

                        # Display numerical and categorical summaries only if no specific customer is selected
                        if selected_customer_id == '':
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

            with st.expander("📜 Column Description", expanded=False):
                st.write(
                    """
                    This section provides comprehensive descriptions of each column in the dataset, 
                    helping users understand the required structure and content to ensure alignment 
                    with analysis objectives. Consistency in data structure is critical, particularly 
                    when users upload datasets for analysis on the prediction page.

                    **Important:** It is highly recommended to upload clean data with minimal missing values 
                    for the best results. For categorical columns, missing values can be replaced with 'Unknown' 
                    to facilitate analysis. However, the app is designed to handle numerical missing values 
                    automatically to ensure proper data representation and accurate results.

                    When uploading data to the Future Projections page under the Insights and Forecasting section, 
                    it is advisable to retain the original missing values for both categorical and numerical data
                    to ensure accuracy in forecasting models.
                    """
                )
                # Create the DataFrame
                df_info = pd.DataFrame({"Column": initial_df.columns, "Type": initial_df.dtypes})

                # Map dtype values to more descriptive terms
                df_info['Type'] = df_info['Type'].replace({
                    'object': 'Categorical',
                    'int64': 'Numerical',
                    'float64': 'Numerical'
                })

                df_info = df_info.reset_index(drop=True)

                # Set the index to start from 1
                df_info.index = df_info.index + 1

                # Display the table
                st.table(df_info)

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

            with st.expander("⬇️ Download Data", expanded=False):
                st.write(
                    """
                    Download the dataset in multiple formats beyond the default CSV for enhanced analysis or dissemination. 
                    Both the original and filtered datasets are available for download in the following formats: Excel, Stata, HTML, and JSON.
                    """
                )
                st.write("##### Download Original Data")
                generate_download_buttons_original(df)
                
                # Provide options to download the filtered data if applicable
                st.write("##### Download Filtered Data")
                generate_download_buttons_filtered(filtered_data)

else:
    st.warning("Please login to access this page.")


            
        


        # st.subheader("Column Description")
        # st.write(
        #     """
        #     This section provides comprehensive descriptions of each column in the dataset, 
        #     helping users understand the required structure and content to ensure alignment 
        #     with analysis objectives. Consistency in data structure is critical, particularly 
        #     when users upload datasets for analysis on the prediction page.

        #     **Important:** It is highly recommended to upload clean data with minimal missing values 
        #     for the best results. For categorical columns, missing values can be replaced with 'Unknown' 
        #     to facilitate analysis. However, the app is designed to handle numerical missing values 
        #     automatically to ensure proper data representation and accurate results.

        #     When uploading data to the Future Projections page under the Insights and Forecasting section, 
        #     it is advisable to retain the original missing values for both categorical and numerical data
        #     to ensure accuracy in forecasting models.
        #     """
        # )


        # descriptions = {
        #     'Gender': 'Whether the customer is male or female',
        #     'SeniorCitizen': 'Whether a customer is a senior citizen (Yes or No)',
        #     'Partner': 'Customer has a partner (Yes, No)',
        #     'Dependents': 'Customer has dependents (Yes, No)',
        #     'Tenure': 'Months the customer has stayed with the company',
        #     'PhoneService': 'Customer has phone service (Yes, No)',
        #     'MultipleLines': 'Customer has multiple lines (Yes, No phone service, No)',
        #     'InternetService': 'Internet service provider (DSL, Fiber Optic, No)',
        #     'OnlineSecurity': 'Customer has online security (Yes, No, No internet service)',
        #     'OnlineBackup': 'Customer has online backup (Yes, No, No internet service)',
        #     'DeviceProtection': 'Customer has device protection (Yes, No, No internet service)',
        #     'TechSupport': 'Customer has tech support (Yes, No, No internet service)',
        #     'StreamingTV': 'Customer has streaming TV (Yes, No, No internet service)',
        #     'StreamingMovies': 'Customer has streaming movies (Yes, No, No internet service)',
        #     'Contract': 'Contract term (Month-to-month, One year, Two year)',
        #     'PaperlessBilling': 'Customer has paperless billing (Yes, No)',
        #     'PaymentMethod': 'Payment method (Bank transfer (automatic), Credit card (automatic), Electronic check, Mailed check)',
        #     'MonthlyCharges': 'Monthly charge to the customer',
        #     'TotalCharges': 'Total charge to the customer',
        #     'Churn': 'Whether the customer churned (Yes, No)',
        #     'AvgMonthlyCharges': 'The average amount charged to the customer per month over their tenure.',
        #     'MonthlyChargesToTotalChargesRatio': 'The ratio of the monthly charges to the total charges, indicating the proportion of total cost that is paid monthly.'            
        # }
        # for col, desc in descriptions.items():
        #     st.write(f"- *{col}*: {desc}")

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
