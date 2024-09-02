import time
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_lottie import st_lottie
import streamlit as st
import streamlit.components.v1 as components
import time
import base64
from PIL import Image
from utils.login import invoke_login_widget
from utils.lottie import display_lottie_on_page
from streamlit_authenticator.utilities import RegisterError

# Invoke the login form
invoke_login_widget('Home')

# Fetch the authenticator from session state
authenticator = st.session_state.get('authenticator')

if not authenticator:
    st.error("Authenticator not found. Please check the configuration.")
    st.stop()

# Check authentication status
if st.session_state.get("authentication_status"):

    # Contact form dialog
    @st.dialog("Contact Us")
    def show_contact_form():
        with st.form(key='contact_form'):
            st.text_input("First Name")
            st.text_input("Last Name")
            st.text_input("Email")
            st.text_area("Message")
            st.form_submit_button("Submit")

    # Function to convert an image to base64
    def image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    # Image paths
    image_paths = [
        "./assets/slideshow_1.jpeg",
        "./assets/slideshow_2.jpeg",
        "./assets/slideshow_3.png",
        "./assets/slideshow_4.jpeg",
        "./assets/slideshow_5.png",
        "./assets/slideshow_6.jpeg",
        "./assets/slideshow_7.png",
        "./assets/favicon.png"
    ]

    # Convert images to base64
    image_b64 = [image_to_base64(img) for img in image_paths]

    st.write("---")

    # Define the HTML for a slideshow with base64 images
    slideshow_html = f"""
    <div class="slideshow-container">
      <div class="mySlides fade">
        <img src="data:image/png;base64,{image_b64[0]}" style="width:100%">
      </div>
      <div class="mySlides fade">
        <img src="data:image/png;base64,{image_b64[1]}" style="width:100%">
      </div>
      <div class="mySlides fade">
        <img src="data:image/png;base64,{image_b64[2]}" style="width:100%">
      </div>
      <div class="mySlides fade">
        <img src="data:image/png;base64,{image_b64[3]}" style="width:100%">
      </div>
      <div class="mySlides fade">
        <img src="data:image/png;base64,{image_b64[4]}" style="width:100%">
      </div>
      <div class="mySlides fade">
        <img src="data:image/png;base64,{image_b64[5]}" style="width:100%">
      </div>
      <div class="mySlides fade">
        <img src="data:image/png;base64,{image_b64[6]}" style="width:100%">
      </div>
    </div>

    <style>
    .slideshow-container {{
      position: relative;
      max-width: 100%;
      margin: auto;
    }}

    .mySlides {{
      display: none;
    }}

    .fade {{
      animation: fade 3s ease-in-out infinite;
    }}

    @keyframes fade {{
      0% {{opacity: 0}}
      20% {{opacity: 1}}
      80% {{opacity: 1}}
      100% {{opacity: 0}}
    }}
    </style>

    <script>
    let slideIndex = 0;
    showSlides();

    function showSlides() {{
      let i;
      let slides = document.getElementsByClassName("mySlides");
      for (i = 0; i < slides.length; i++) {{
        slides[i].style.display = "none";  
      }}
      slideIndex++;
      if (slideIndex > slides.length) {{slideIndex = 1}}    
      slides[slideIndex-1].style.display = "block";  
      setTimeout(showSlides, 3000); // Change image every 3 seconds
    }}
    </script>
    """

    # Streamlit app code
    st.markdown(
        """
        <h1 style='text-align: center;'>Switzerland Data Insights</h1>
        <p style='text-align: center;'>We are a team of data science professionals in the Azubi-Africa Data Analytics Program.</p>
        <p style='text-align: center;'>Our mission is to drive insights and impact through collaborative projects and cutting-edge analytics.</p>
        <p style='text-align: center;'>Join us in leveraging data for meaningful advancements! 🌍📈</p>
        """,
        unsafe_allow_html=True
    )

    # Display the slideshow
    components.html(slideshow_html, height=750)

    # Lottie Animation
    with st.container():
        left_column, right_column = st.columns(2)
        with left_column:
            st.markdown("<h2 style='font-size: 2.5em;'>Churn Predictor</h2>", unsafe_allow_html=True)
            st.write("This app is designed to predict customer churn in a telecommunication company.")

            st.subheader("User Interaction")
            st.markdown("""
            - **Home Page:** Provides a comprehensive overview of the app’s functionalities and introduces the team behind its development.
            - **Login and Sign Up Forms:** Secure access management with options for both logging in and creating a new user account.
            - **Account Page:** Manage your personal account settings, including updating details, resetting passwords, and handling user registrations.
            """)


            st.subheader("Data Management and Analysis")
            st.markdown("""
            - **Data Overview:** Tools to upload and explore datasets with interactive filters.
            - **Analytics Dashboard:** Interactive visualizations and data insights.
            """)


            st.subheader("Insights and Forecasting")
            st.markdown("""
            - **Historical Insights:** Displays results from previous predictions, showing trends and outcomes based on historical data. This section helps users understand past prediction results and their implications.
            - **Future Projections:** Predicts future customer churn based on historical data insights. This page leverages past trends to forecast potential churn rates and guide decision-making for customer retention strategies.
            """)


        
        with right_column:  
            display_lottie_on_page("Home")
    
    # App Features Section
    st.subheader("App Features")
    st.write("""
    - **Churn Predictor:** Predicts customer churn in a telecommunications company.
    - **Data Management:** Tools for managing and visualizing data.
    - **Interactive Dashboard:** Provides interactive data visualizations.
    - **Predictive Analytics:** Forecasts future trends based on historical data.
    """)

    # Key Features
    st.subheader("Key Features")
    st.write("""
    - **Accurate Churn Predictions:** Uses advanced models to forecast customer churn.
    - **User-Friendly Interface:** Easy navigation with intuitive design.
    - **Data Visualization:** Interactive graphs and charts to explore data insights.
    - **Secure Access:** Login system to protect user data.
    """)

    # User Benefits
    st.subheader("User Benefits")
    st.write("""
    - **Data-Driven Decisions:** Make informed decisions based on accurate churn predictions.
    - **Easy Machine Learning Integration:** Leverage advanced machine learning models with ease.
    - **Comprehensive Insights:** Gain valuable insights from data visualizations and forecasts.
    - **Efficient Data Management:** Organize and manage data effectively.
    """)

    # Watch Demo Video
    st.subheader("Watch Demo Video") 
    video_file = open('./assets/app_demo.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes, start_time=0, format="video/mp4")
    st.markdown("<p style='text-align: center;'>Watch how to use the Churn Predictor app.</p>", unsafe_allow_html=True)

    # How to Run the Application
    st.subheader("How to Run the Application")
    st.code("""
    # Install necessary packages
    pip install streamlit pandas numpy scikit-learn

    # Run the app
    streamlit run 00_🚪_Gateway.py
    """, language='bash')

    # Machine Learning Integration
    st.subheader("Machine Learning Integration")
    st.write("""
    - **Model Selection:** Choose the best model for your data, such as random forest and xgboost classifiers.
    - **Seamless Integration:** Integrate machine learning models with your Streamlit app effortlessly.
    - **Probability Estimates:** Get probability estimates for predictions and understand model outputs.
    """)

    # # Need Help Section
    # st.subheader("Need Help")
    # st.write("""
    # - **For Collaborations:** Contact us at sdi@azubiafrica.org
    # """)
    # if st.button("GitHub Repository"):
    #     st.write("[Visit our GitHub Repository](https://github.com/Nfayem/Churn_Predictor.git)")

    # # Expanded Contact Form
    # st.subheader("Contact Us")
    # with st.form(key='expanded_contact_form'):
    #     st.text_input("First Name")
    #     st.text_input("Last Name")
    #     st.text_input("Email")
    #     st.text_area("Message")
    #     st.form_submit_button("Submit")

    # Team Section
    st.subheader("Team")

    # Define team member details with provided names and roles
    team_members = [
        {"image": "./assets/devops.jpeg", "name": "Nfayem Imoro", "title": "Data Analyst", "role": "Lead Analyst & Project Manager"},
        {"image": "./assets/team_member_2.jpeg", "name": "Gabriel Koku Kuma", "title": "Data Analyst", "role": "Data Engineer & Modeling Expert"},
        {"image": "./assets/jackops.jpg", "name": "Jackline Wangari Maina", "title": "Data Analyst", "role": "Machine Learning Specialist"},
        {"image": "./assets/team_member_4.jpeg", "name": "Obed Korda", "title": "Data Analyst", "role": "Customer Churn Analyst"},
        {"image": "./assets/team_member_5.jpeg", "name": "Godfred Frank Aning", "title": "Data Analyst", "role": "Data Visualization Specialist"},
        {"image": "./assets/team_member_6.jpeg", "name": "Victor Obondo", "title": "Data Analyst", "role": "Database Manager"},
    ]

    # Resize team images to the same dimensions
    team_images_resized = [Image.open(member["image"]).resize((300, 300)) for member in team_members]

    # Display team members in two rows
    for i in range(0, 6, 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            col.image(team_images_resized[i + j])
            col.text(team_members[i + j]["name"])
            col.text(team_members[i + j]["title"])
            col.text(team_members[i + j]["role"])

    # Need Help Section
    st.subheader("Need Help?")
    st.write("""
    - **For Collaborations:** Contact us at [sdi@azubiafrica.org](mailto:sdi@azubiafrica.org)
    """)

    # Create a styled link that looks like a button
    st.markdown(
        """
        <div style="text-align: left;">
            <a href="https://github.com/Nfayem/Churn_Predictor.git" target="_blank" style="
                display: inline-block;
                padding: 10px 20px;
                font-size: 16px;
                color: white;
                background-color: #0366d6;
                border-radius: 5px;
                text-decoration: none;
            ">Visit GitHub Repository</a>
        </div>
        """,
        unsafe_allow_html=True
    )

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
                <img src="data:image/png;base64,{image_b64[7]}" style="width:100%";" />
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Contact Button
    if st.button("Inquiries"):
        show_contact_form()

# Loading config file
with open('./config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Handle user registration
try:
    (email_of_registered_user,
     username_of_registered_user,
     name_of_registered_user) = authenticator.register_user("sidebar", pre_authorization=False, fields={'Form name':'Sign Up Here', 'Register':'Sign Up'})
    
    if email_of_registered_user:
        # Create a placeholder for the success message
        success_placeholder = st.empty()
        success_placeholder.success('The new user has been successfully registered.')
        
        # Clear the success message after a delay
        time.sleep(3)  # Wait for 3 seconds
        success_placeholder.empty()

except RegisterError as e:
    st.error(f"Error registering user: {e}")


# Save the updated configuration file
with open('./config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)