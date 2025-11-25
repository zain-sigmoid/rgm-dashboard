import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from plotly.subplots import make_subplots
import streamlit_extras
from streamlit_extras.switch_page_button import switch_page
from Promotions_Analysis import promotion_analysis
from Performance_Analysis import performance_analysis
from Simulation_Tool import simulation_tool
from Drill_Through import drill_through
from Contribution_Analysis import contribution_analysis
from Descriptive_Analysis import descriptive_analysis
from Simulation_Analysis import simulation_analysis
from Pricing_Drill_Through import pricing_drill_through
from Summary import market_summary
from streamlit_extras.stylable_container import stylable_container

# def price_dashboard():  
st.set_page_config(
            page_title="RGM Dashboard",
            layout="wide",
            page_icon = 'sigmoid_logo.png',
            initial_sidebar_state="collapsed")
st.write("  ")
t1,t2,t3= st.columns([0.9,0.12,0.08])
with t2:
    on = st.toggle('Smart Pricing')

if on:
    with t3:
        with stylable_container(
                                    key="green_button1",
                                    css_styles="""
                                        button {
                                            background-color: #ffffff;
                                            color: #205B97;
                                            border-radius: 10px;
                                        }
                                        """,
                                ):
            if st.button('Glossary', key=10, use_container_width=True):
                    st.switch_page("./pages/Glossary Pricing.py")

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
                    font-family: Arial, sans-serif; /* Custom font style */
                }
                .navbar-brand {
                    color: white !important; /* Setting text color to white */
                    font-size: 24px; /* Custom font size */
                    # font-weight: bold; /* Custom font weight */
                    text-decoration: none; /* Remove underline */
                }
                .navbar-button {
                    background-color: white !important;
                    color: red !important;
                    border: 1px solid red;
                }
                .navbar-button:hover {
                    background-color: red !important;
                    color: white !important;
                }
            </style>
            """, unsafe_allow_html=True)

        # Navbar content
        st.markdown("""
            <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="margin-top: 20px; margin-bottom: 0px;">
            <div class="container-fluid">
                <img src="https://i.im.ge/2024/05/30/KLEPIh.Screenshot-2024-05-30-at-10-20-29AM.png" alt="Logo1" style="height: 55px; margin-right: -10px; margin-top: 20px; margin-bottom: -10px">
                <img src="https://i.im.ge/2024/03/21/RKWdrM.Sigmoid-Logo.png" alt="Logo2" style="height: 60px; margin-left: 1400px; margin-top: 20px; margin-bottom: -10px">
                <div class="navbar-collapse justify-content-end">
                </div>
            </div>
        </nav>
            """, unsafe_allow_html=True)

    render_navbar()
    with t1:
        st.markdown(
                   """
                    <div style="display: flex; justify-content: left; text-align: left;">
                        <p style="font-size: 30px; color: #205B97; font-weight: bold; font-family: 'Graphik';">
                            SMART PRICING
                        </p>
                    </div>
                    """,
                unsafe_allow_html=True
                )

  


    listTabs = ["    Market Share Summary   ","    Trend Analysis   ","    Elasticity & Contribution   ",'    Simulator   ']
    tab1, tab2,tab3,tab4 = st.tabs(listTabs)
    custom_css = """
    <style>
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            justify-content: left;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #F0F2F6;
            font-family: Graphik;
            font-size: 20px;
            color : #205B97;
            margin: 0 5px;
            transition: background-color 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #F0F2F6;
            color : #205B97;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #F0F2F6;
            border-bottom: 2px solid #555867;
            color: #205B97;
        }
    </style>
    """

    # Inject custom CSS into the Streamlit app
    st.markdown(custom_css, unsafe_allow_html=True)

    with tab1:
        market_summary()
    with tab3:
        contribution_analysis()
    with tab2:
        descriptive_analysis()
    with tab4:
        simulation_analysis()
    # with tab5:
    #     pricing_drill_through()


else:
    with t3:
        with stylable_container(
                                    key="green_button11",
                                    css_styles="""
                                        button {
                                            background-color: #ffffff;
                                            color: #205B97;
                                            border-radius: 10px;
                                        }
                                        """,
                                ):
            if st.button('Glossary', key=1, use_container_width=True):
                    st.switch_page("./pages/Glossary Promotion.py")
    def render_navbar_promo():
        # Adding Bootstrap CSS
        st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

        # Adding custom CSS for navbar
        st.markdown("""
            <style>
                .navbar {
                    background: linear-gradient(90deg, #D91E18, orange);
                    font-family: Arial, sans-serif; /* Custom font style */
                }
                .navbar-brand {
                    color: white !important; /* Setting text color to white */
                    font-size: 24px; /* Custom font size */
                    # font-weight: bold; /* Custom font weight */
                    text-decoration: none; /* Remove underline */
                }
                .navbar-button {
                    background-color: white !important;
                    color: red !important;
                    border: 1px solid red;
                }
                .navbar-button:hover {
                    background-color: red !important;
                    color: white !important;
                }
            </style>
            """, unsafe_allow_html=True)

        # Navbar content
        st.markdown("""
            <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="margin-top: 20px; margin-bottom: 0px;">
            <div class="container-fluid">
                <img src="https://i.im.ge/2024/05/30/KLEPIh.Screenshot-2024-05-30-at-10-20-29AM.png" alt="Logo1" style="height: 55px; margin-right: -10px; margin-top: 20px; margin-bottom: -10px">
                <img src="https://i.im.ge/2024/03/21/RKWdrM.Sigmoid-Logo.png" alt="Logo2" style="height: 60px; margin-left: 1400px; margin-top: 20px; margin-bottom: -10px">
                <div class="navbar-collapse justify-content-end">
                </div>
            </div>
        </nav>
            """, unsafe_allow_html=True)

    render_navbar_promo()
    with t1:
        st.markdown(
                   """
                    <div style="display: flex; justify-content: left; text-align: left;">
                        <p style="font-size: 30px; color: #205B97; font-weight: bold; font-family: 'Graphik';">
                            OPTIMAL PROMOTION
                        </p>
                    </div>
                    """,
                unsafe_allow_html=True
                )
    listTabs = ["    Past Promotional Analysis   ","    Performance Analysis   ",'    Simulator   ']
    tab1, tab2,tab3 = st.tabs(listTabs)
    custom_css = """
    <style>
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            justify-content: left;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #F0F2F6;
            font-family: Graphik;
            font-size: 20px;
            color : #205B97;
            margin: 0 5px;
            transition: background-color 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #F0F2F6;
            color : #205B97;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #F0F2F6;
            border-bottom: 2px solid #555867;
            color: #205B97;
        }
    </style>
    """

    # Inject custom CSS into the Streamlit app
    st.markdown(custom_css, unsafe_allow_html=True)

    with tab1:
        promotion_analysis()
    with tab2:
        performance_analysis()
    with tab3:
        simulation_tool()
    # with tab4:
    #     drill_through()