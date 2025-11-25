import numpy as np
import pandas as pd
import streamlit as st  
import time 
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(
        page_title="RGM Dashboard",
        layout="wide",
        page_icon = 'sigmoid_logo.png',
        initial_sidebar_state="collapsed")

def sidebar_fix_width():
    st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 1px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
    )
sidebar_fix_width()

def render_navbar():
# Adding Bootstrap CSS
    st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

    # Adding custom CSS for navbar
    st.markdown("""
        <style>
            .navbar {
                background: linear-gradient(90deg, #D91E18, orange);
            
            }
        </style>
        """, unsafe_allow_html=True)

    # Navbar content
    st.markdown("""
        <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="margin-top: 20px; margin-bottom: 10px;">
            <div class="container-fluid">
                <img src="https://i.im.ge/2024/05/30/KLEPIh.Screenshot-2024-05-30-at-10-20-29AM.png" alt="Logo1" style="height: 55px; margin-right: -10px; margin-top: 20px; margin-bottom: -10px">
                <img src="https://i.im.ge/2024/03/21/RKWdrM.Sigmoid-Logo.png" alt="Logo2" style="height: 60px; margin-left: 1400px; margin-top: 20px; margin-bottom: -10px">
                <div class="navbar-collapse justify-content-end">
                </div>
        </nav>
        """, unsafe_allow_html=True)

render_navbar()
columns1 = st.columns(1)
with columns1[0]:
    background_image = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://media-hosting.imagekit.io/3bde305e78e04d8e/landing_page.png?Expires=1838207440&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=Z3a3q5qiObphzBNUA9d9XzXhG2AgK8XNaPunNYwk-8jxZUhYl1U7fhLOcb2A9Fj-Y12M9~-whl5MqSQiCZHdaL5vRGF3hbudNqCb2lqxkXnpVxXi9eCDtwhGuxLjoazJxQOmXb9aW3itG1nnbGk7Dlimhzln9rip~Hufves9BOBoY~-B0adRnsov6tXYFrjDUa21xD8BPfsfO4CNP6ixzr2vmgj7Q1oexlXmUafqWL~ZxiCo23HM~5LCY60CY~fEYzeCdldJA8qSgE0dfcNcNntbfSrKe~NTlj-elb8uO5CMMpN6sKO5GuByddpOU--FQ~RwyCudgCeqKAD-Qar1sQ__");
        background-size: cover;
        background-position: center; 
        background-repeat: no-repeat;
    }
    </style>
    """

    st.markdown(background_image, unsafe_allow_html=True)
    # set_background('https://i.im.ge/2024/05/15/KQFYEf.Fair-share.png')
    col2,col1 = st.columns([5,2])
    # with col1:
    #     st.write("        ")
    #     st.write("        ")
    #     st.write("        ")
    #     st.write("        ")
    #     st.write("        ")
    #     st.write("        ")


    #     st.image("undraw_dashboard_re_3b76 1.png")

    with col2:
      


        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.markdown(
                   """
                    <div style="display: flex; justify-content: center; text-align: left;flex-direction: column;">
                        <p style="font-size: 75px; color: #171719; font-weight: bold; font-family: 'Graphik';">
                            <span style="color: #023E8A;">Sigmoid's</span>
                        </p>
                        <p style="font-size: 75px; color: #171719; font-weight: bold; font-family: 'Graphik';">
                            <span style="color: #023E8A;">Pricing</span> and <span style="color: #023E8A;">Promotion</span>
                        </p>
                        <p style="font-size: 75px; color: #171719; font-weight: bold; font-family: 'Graphik';">
                            Optimization Tool
                        </p>
                    </div>
                    """,
                unsafe_allow_html=True
                )
        
def main():   
    c1,c2,c3,c4  = st.columns([2,2,3,3])


    with c1:
            with stylable_container(
                                    key="green_button11",
                                    css_styles="""
                                        button {
                                           
                                            height: auto;
                                            background-color : #023E8A;
                                            padding-top: 10px !important;
                                            padding-bottom: 10px !important;
                                            padding-left: 10px !important;
                                            padding-right: 10px !important;
                                            font-size:20px !important;
                                            font-family : 'Graphik';
                                            color:white;
                            }
                            """,
                                ):
                if st.button('SMART PRICING', key = 'green_button11',use_container_width=True):
                    st.switch_page("./pages/Smart Pricing.py")
    with c2:
         with stylable_container(
                                    key="green_button10",
                                    css_styles="""
                                        button {
                                           
                                            height: auto;
                                            background-color : #023E8A;
                                            padding-top: 10px !important;
                                            padding-bottom: 10px !important;
                                            padding-left: 10px !important;
                                            padding-right: 10px !important;
                                            font-size:20px !important;
                                            font-family : 'Graphik';
                                            color:white;
                            }
                            """,
                                ):
            if st.button('OPTIMAL PROMOTION', key = 'green_button10',use_container_width=True):
                st.switch_page("./pages/Optimal Promotion.py")



if __name__ == "__main__":
    main()
