import requests
from streamlit_lottie import st_lottie
import streamlit as st
import streamlit.components.v1 as components
import time
import base64
from PIL import Image
from utils.login import invoke_login_widget
from utils.lottie import display_lottie_on_page


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
      st.text_input("First Name")

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
    </div> <!-- Missing closing div -->
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

  # lottie_coding = "https://lottie.host/f3734960-8bd5-4e1e-94c7-57787a497ac7/dXSGaeZhUf.json"

  with st.container():
      left_column, right_column = st.columns(2)
      with left_column:
          st.markdown("<h2 style='font-size: 2.5em;'>Churn Predictor</h2>", unsafe_allow_html=True)
          st.write("This app is designed to predict customer churn in a telecomunication company.")

          st.subheader("User Interaction")
          st.markdown("""
          - **Home Page:** Welcome page providing an overview and access to other sections.
          - **Login Page:** Secure login functionality for user access.
                      """)

          st.subheader("Data Management")
          st.markdown("""
          - **Data Overview:** Tools for managing and visualizing data.
          - **Analytics Dashboard:** Interactive visualizations and data insights.
                      """)

          st.subheader("Insights and Forecasting")
          st.markdown("""
          - **Historical Data Analysis:** Exploration of past data trends.
          - **Predictive Modeling:** Forecasting future trends based on historical data.
                      """)
        
      with right_column:  
          # st_lottie(lottie_coding, height=300, key="coding")
          display_lottie_on_page("Home")
      

  # Team Section
  st.subheader("Team")

  # Define team member details with provided names and roles
  team_members = [
      {"image": "./assets/team_member_1.jpeg", "name": "Nfayem Imoro", "title": "Data Analyst", "role": "Lead Analyst & Project Manager"},
      {"image": "./assets/team_member_2.jpeg", "name": "Gabriel Koku Kuma", "title": "Data Analyst", "role": "Data Engineer & Modeling Expert"},
      {"image": "./assets/team_member_3.jpeg", "name": "Jackline Wangari Maina", "title": "Data Analyst", "role": "Machine Learning Specialist"},
      {"image": "./assets/team_member_4.jpeg", "name": "Obed Korda", "title": "Data Analyst", "role": "Customer Churn Analyst"},
      {"image": "./assets/team_member_5.jpeg", "name": "Godfred Frank Aning", "title": "Data Analyst", "role": "Data Visualization Specialist"},
      {"image": "./assets/team_member_6.jpeg", "name": "Victor Obondo", "title": "Data Analyst", "role": "Database Manager"},
  ]

  # Display team members in two rows
  for i in range(0, 6, 3):
      cols = st.columns(3)
      for j, col in enumerate(cols):
          col.image(team_members[i + j]["image"], width=300)
          col.text(team_members[i + j]["name"])
          col.text(team_members[i + j]["title"])
          col.text(team_members[i + j]["role"])


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
              <p>📧 Email: contact@azubiafrica.org</p>
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
