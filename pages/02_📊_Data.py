import streamlit as st
import pandas as pd
import plotly.express as px
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

    st.title("Data Hub")

    # Display Lottie animation for the data page
    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.header("Data Analysis")
            st.write(
                """
                This page allows you to upload, view, and analyze datasets.
                Use the sidebar to upload your data file.
                """
            )
        with right_column:
            display_lottie_on_page("Data Overview")

    # Load the data
    @st.cache_data(persist=True)
    def load_initial_data():
        df_2000 = pd.read_excel('./data/LP2_train_final.xlsx')
        return df_2000
    
    initial_df = load_initial_data()
    st.dataframe(initial_df)

    st.sidebar.header("Data Upload")
    uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

    def load_uploaded_data(uploaded_file):
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

    df = load_uploaded_data(uploaded_file) or initial_df

    if df is not None:
        st.write("### Uploaded Dataset")
        st.dataframe(df)

        st.write("### Data Summary")
        st.write(df.describe())

        st.write("---")

        # Map Churn to numerical values
        df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})

        # Churn Distribution (Pie Chart)
        st.subheader("Churn Distribution (Pie Chart)")
        churn_counts = df['Churn'].value_counts()
        fig = px.pie(churn_counts, names=['No', 'Yes'], values=churn_counts.values,
                     title="Churn Distribution")
        st.plotly_chart(fig)

        # Monthly Charges vs. Churn (Bar Chart)
        st.subheader("Monthly Charges vs. Churn (Bar Chart)")
        if 'MonthlyCharges' in df.columns:
            churn_vs_charges = df.groupby('Churn')['MonthlyCharges'].mean().reset_index()
            churn_vs_charges['Churn'] = churn_vs_charges['Churn'].map({0: 'No', 1: 'Yes'})  # Remap 0 and 1 to 'No' and 'Yes'
            fig = px.bar(churn_vs_charges, x='Churn', y='MonthlyCharges',
                         labels={'Churn': 'Churn', 'MonthlyCharges': 'Average Monthly Charges'},
                         title="Average Monthly Charges vs. Churn")
            st.plotly_chart(fig)
        else:
            st.warning("Column 'MonthlyCharges' not found in the data.")

        # Scatter Plot with Trend Line
        st.subheader("Tenure vs. Churn (Scatter Plot with Trend Line)")
        if 'tenure' in df.columns:
            fig = px.scatter(df, x='tenure', y='Churn', trendline='ols',
                             labels={'tenure': 'Tenure', 'Churn': 'Churn (0 = No, 1 = Yes)'},
                             title="Tenure vs. Churn with Trend Line")
            st.plotly_chart(fig)
        else:
            st.warning("Column 'tenure' not found in the data.")

        # Interactive filters
        st.subheader("Filter Data")
        columns = df.columns.tolist()
        selected_column = st.selectbox("Select a column to filter by", columns)
        unique_values = df[selected_column].unique()
        selected_value = st.selectbox(f"Select a value from {selected_column}", unique_values)
        filtered_data = df[df[selected_column] == selected_value]

        st.write(f"Filtered Data (showing rows where {selected_column} is {selected_value}):")
        st.dataframe(filtered_data)
    else:
        st.warning("No data available to display.")
else:
    st.warning("You must be logged in to access the data.")




# Lottie animation for the data page
# lottie_data = "https://assets5.lottiefiles.com/private_files/lf30_5ttqPi.json"

# st_lottie(lottie_data, height=300, key="data")