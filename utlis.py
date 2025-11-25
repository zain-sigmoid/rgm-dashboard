import streamlit as st  
import numpy as np
def key_metrics_price(label,value,icon_link):
    icon_url = icon_link

    # box_width = "250px"
    box_height = "70px"

    component_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: start;
        border: 1px solid #F1F1F1;
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        color: black;
        font-family: 'Graphik'; /* Use Graphik font */
        width: 100%;
        height: {box_height};
    ">
        <img src="{icon_url}" alt="Icon" style="width: 60px; height: 60px; margin-right: 20px;">
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
            <div style="color: #808495; font-size:15px;padding:  0px 0px 0px 0px; ">{label}</div>
            <div style="font-size:25px; font-weight: bold; padding: 0px 0px 0px 0px ;">{value}</div>
        </div>
    </div>
    """

    st.markdown(component_html, unsafe_allow_html=True)



def convert_to_abbreviated(num):
    if np.abs(num) < 1000:
        return str(num)
    elif np.abs(num) >= 1000 and np.abs(num)< 1000000:
        return str(round(np.abs(num)/ 1000, 2)) + 'K'
    elif np.abs(num)>= 1000000 and np.abs(num)< 1000000000:
        return str(round(np.abs(num)/ 1000000, 2)) + 'M'
    elif np.abs(num)>= 1000000000 and np.abs(num)< 1000000000000:
        return str(round(np.abs(num)/ 1000000000, 2)) + 'B'
    elif np.abs(num)>= 1000000000000:
        return str(round(np.abs(num)/ 1000000000000, 2)) + 'T'
def key_glossary(label,value,icon_link):
    icon_url = icon_link

    # box_width = "210px"
    box_height = "px"

    component_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: start;
        border: 1px solid #F1F1F1;
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        color: black;
        font-family: 'Graphik'; /* Use Graphik font */
        width: 100%;
        height: {box_height};
    ">
        <img src="{icon_url}" alt="Icon" style="width: 60px; height: 60px; margin-right: 20px;">
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
            <div style="font-size:20px; font-weight: bold; padding: 0px 0px 0px 0px ;">{value}</div>
            <div style="color: #808495; font-size:18px;padding:  0px 0px 15px 0px; ">{label}</div>
        </div>
    </div>
    """

    st.markdown(component_html, unsafe_allow_html=True)

def key_metrics_price2(label,value,icon_link):
    icon_url = icon_link

    # box_width = "210px"
    box_height = "70px"

    component_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: start;
        border: 1px solid #F1F1F1;
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        color: black;
        font-family: 'Graphik'; /* Use Graphik font */
        width: 100%;
        height: {box_height};
    ">
        <img src="{icon_url}" alt="Icon" style="width: 60px; height: 60px; margin-right: 20px;">
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
            <div style="color: #808495; font-size:15px;padding:  0px 0px 0px 0px; ">{label}</div>
            <div style="font-size:25px; font-weight: bold; padding: 0px 0px 0px 0px ;">{value}</div>
        </div>
    </div>
    """

    st.markdown(component_html, unsafe_allow_html=True)


def key_metrics_price3(label,value,icon_link):
    icon_url = icon_link

    # box_width = "310px"
    box_height = "30px"

    component_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: start;
        border: 1px solid #F1F1F1;
        background-color: #F0F2F6;
        border-radius: 5px;
        padding: 2px;
        color: black;
        font-family: 'Graphik'; /* Use Graphik font */
        width: 100%;
        height: {box_height};
    ">
        <img src="{icon_url}" alt="Icon" style="width:60px;height: 60px; margin-right: 20px;">
        <div style="display: flex; flex-direction: column; justify-content: center; ">
            <div style="color: #808495; font-size:14px; ">{label}</div>
            <div style="font-size:20px; font-weight: bold; ">{value}</div>
        </div>
    </div>
    """

    st.markdown(component_html, unsafe_allow_html=True)

def key_metrics_price4(label,value):

    # box_width = "180px"
    box_height = "80px"

    component_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: left;
        border: 1px solid #F1F1F1;
        background-color: #c0e4f4;
        font-family: 'Graphik'; /* Use Graphik font */
        border-radius: 5px;
        padding: 10px;
        color: black;
        width: 100%;
        height: {box_height};
    ">
    <div style="display: flex; flex-direction: column; justify-content: left; height: 100%;">
            <div style="font : Graphik;color: #262730;font-size: 0.8em;">{label}</div>
            <div style="color: black;font-size:1.5em">{value}</div>
        </div>
    </div>
    """

    st.markdown(component_html, unsafe_allow_html=True)

def key_metrics_price5(value):

    # box_width = "180px"
    box_height = "60px"

    component_html = f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: left;
        border: 1px solid #F1F1F1;
        background-color: #F2ECFE;
        border-radius: 5px;
        padding: 10px;
        color: #803DF5;
        width: 100%;
        font-family: 'Graphik';
        height: {box_height};
    ">
    <div style="display: flex; flex-direction: column; justify-content: left; height: 100%;">
            <div style="color: #803DF5;font-size:1.5em;">{value}</div>
        </div>
    </div>
    """

    st.markdown(component_html, unsafe_allow_html=True)