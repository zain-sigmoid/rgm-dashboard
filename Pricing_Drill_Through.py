import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from utlis import key_metrics_price2,convert_to_abbreviated
def pricing_drill_through():
    
    def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
            fig = go.Figure()

            fig.add_trace(
                go.Indicator(
                    value=value,
                    number={
                        "prefix": prefix,
                        "suffix": suffix,
                        "font.size": 50,
                    },
                    title={
                        "text": label,
                        "font": {"size": 15},
                    },
                )
            )


            fig.update_xaxes(visible=False, showgrid=False)
            fig.update_yaxes(visible=False, showgrid=False)
            fig.update_layout(
                paper_bgcolor="white",
                margin=dict(t=30, b=0),
                showlegend=False,
                plot_bgcolor="white",
                height=100,
            )

            st.plotly_chart(fig, use_container_width=True,theme = None)
        # Access input from session state
    if "user_input_price" in st.session_state:
        df=st.session_state.user_input_price
        with stylable_container(
        key="container_with_border7",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-color: white;
            }
            """,
            ):
            f0,f1,f2,f3,f4,f5,f6 = st.columns([1,1,1,1,1,1,1])
            with f0:
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5542)
            with f1:
                m1 = st.multiselect("Manufacturer",['All']+ df['Manufacturer'].unique().tolist(),default =st.session_state.m1_price )
                if "All" in m1:
                    m1 = df['Manufacturer'].unique().tolist()
            if len(m1)==0:
                df_fil = df  
            else:          
                df_fil = df[df['Manufacturer'].isin(m1)]
            with f2:
                m2 = st.multiselect("Brand",['All']+df_fil['Brand'].unique().tolist(),default =st.session_state.m2_price)
                if "All" in m2:
                    m2 = df_fil['Brand'].unique().tolist()
            if len(m2)==0:
                df_fil = df_fil  
            else:          
                df_fil = df_fil[df_fil['Brand'].isin(m2)]
            with f3:
                m3 = st.multiselect("Retailer",['All']+df_fil['Retailer'].unique().tolist(),default =st.session_state.m3_price)
                if "All" in m3:
                    m3 = df_fil['Retailer'].unique().tolist()
            if len(m3)==0:
                df_fil = df_fil  
            else:
                df_fil = df_fil[df_fil['Retailer'].isin(m3)]
            with f4:
                m4 = st.multiselect("PPG ",['All']+df_fil['PPG'].unique().tolist(),default =st.session_state.m4_price)
                if "All" in m4:
                    m4 = df_fil['PPG'].unique().tolist()
            if len(m4)==0:
                df_fil = df_fil  
            else:
                df_fil = df_fil[df_fil['PPG'].isin(m4)]
            # price_latest = df_fil[(df_fil['year']==df_fil['year'].max())&(df_fil['week']==52)][['ppg_nm','retailer_id','price']]
            # df_new = df_fil[df_fil['year'].isin(['2021','2022'])].copy()
            # df_new['year']=df_new['year'].replace({'2021':2023,'2022':2024})
            # df_future = pd.merge(df_new,price_latest, on =['ppg_nm','retailer_id'], how='left', suffixes=('','_latest'))
            with f5:
                year_sl = st.multiselect("Year",['All']+df_fil['Year'].unique().tolist(),default =st.session_state.year_sl)
                if "All" in year_sl:
                    year_sl = df_fil['Year'].unique().tolist()
        if len(year_sl)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['Year'].isin(year_sl)]
        with f6:
            week_sl = st.multiselect("Week",['All']+df_fil['Week'].unique().tolist(),default =st.session_state.week_sl)
            if "All" in week_sl:
                week_sl = df_fil['Week'].unique().tolist()
        if len(week_sl)==0:
            df_future = df_fil  
        else:
            df_future = df_fil[df_fil['Week'].isin(week_sl)]
        updated_data_placeholder = st.empty()
        st.write("  ")
        st.write("  ")
                                         

        # Displaying the styled DataFrame in Streamlit
        st.dataframe(df_future.drop_duplicates())
        with updated_data_placeholder:

            c1, c2, c3,c4,c5,c6 = st.columns([1,1,1,1,1,1])
            with c1:
                key_metrics_price2(
                "Old Price",
                st.session_state.old_price,
                'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png')
            with c2:
                key_metrics_price2(
                "New Price",
                st.session_state.new_price,
                'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png')
            with c3:
                 key_metrics_price2(
                "Incremental Revenue",
                convert_to_abbreviated(st.session_state.inc_rev),
                'https://i.im.ge/2024/03/26/WFhf4m.Incremental-Revenue.png')
            with c4:
                key_metrics_price2(
                "Old Volume",
                convert_to_abbreviated(st.session_state.old_volume),
                'https://i.im.ge/2024/03/26/WFhzsr.Old-Volume.png')
            with c5:
                key_metrics_price2(
                "Volume Change(%)",
                str(round(st.session_state.volume_impact,2))+'%',
                'https://i.im.ge/2024/03/26/WFhpz0.Volume-Change.png')
            with c6:
                key_metrics_price2(
                "New Volume",
                convert_to_abbreviated(st.session_state.new_volume),
                'https://i.im.ge/2024/03/26/WFhzsr.Old-Volume.png')
    else:
            st.write("No input submitted")
            # df = pd.read_csv('final_pricing_consolidated_file.csv')
            # df=df.dropna()
            # df['year'] = pd.to_datetime(df['year'].astype(str), format='%Y')
            # df['year'] = df['year'].dt.strftime("%Y") #**change**
            # df['day']=1
            # df['month_name']=df['month'].map({1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})
            # # Define the order of the month names
            # month_order = ['Jan', 'Feb', 'Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

            # # Convert month_name column to categorical data type with specified order
            # df['month_name'] = pd.Categorical(df['month_name'], categories=month_order, ordered=True)
            # df['date'] = pd.to_datetime(df['year'].astype(str) + 
            #                                         df['month'].astype(str), format='%Y%m')
            # f1,f2,f3,f4,f5,f6 = st.columns([1,1,1,1,1,1])
            # with f1:
            #     m1 = st.multiselect("Manufacturer",['All']+ df['manufacturer_nm'].unique().tolist(),key=41)
            #     if "All" in m1:
            #         m1 = df['manufacturer_nm'].unique().tolist()
            # if len(m1)==0:
            #     df_fil = df  
            # else:          
            #     df_fil = df[df['manufacturer_nm'].isin(m1)]
            # with f2:
            #     m2 = st.multiselect("Brand",['All']+df_fil['brand_nm'].unique().tolist(),key=47)
            #     if "All" in m2:
            #         m2 = df_fil['brand_nm'].unique().tolist()
            # if len(m2)==0:
            #     df_fil = df_fil  
            # else:          
            #     df_fil = df_fil[df_fil['brand_nm'].isin(m2)]
            # with f3:
            #     m3 = st.multiselect("Retailer",['All']+df_fil['retailer_id'].unique().tolist(),key=43)
            #     if "All" in m3:
            #         m3 = df_fil['retailer_id'].unique().tolist()
            # if len(m3)==0:
            #     df_fil = df_fil  
            # else:
            #     df_fil = df_fil[df_fil['retailer_id'].isin(m3)]
            # with f4:
            #     m4 = st.multiselect("PPG ",['All']+df_fil['ppg_nm'].unique().tolist(),key=44)
            #     if "All" in m4:
            #         m4 = df_fil['ppg_nm'].unique().tolist()
            # if len(m4)==0:
            #     df_fil = df_fil  
            # else:
            #     df_fil = df_fil[df_fil['ppg_nm'].isin(m4)]
            # # price_latest = df_fil[(df_fil['year']==df_fil['year'].max())&(df_fil['week']==52)][['ppg_nm','retailer_id','price']]
            # # df_new = df_fil[df_fil['year'].isin(['2021','2022'])].copy()
            # # df_new['year']=df_new['year'].replace({'2021':2023,'2022':2024})
            # # df_future = pd.merge(df_new,price_latest, on =['ppg_nm','retailer_id'], how='left', suffixes=('','_latest'))
            # with f5:
            #     year_sl = st.multiselect("Year",['All']+df_fil['year'].unique().tolist(),key=45)
            #     if "All" in year_sl:
            #         year_sl = df_fil['year'].unique().tolist()
            # if len(year_sl)==0:
            #     df_fil = df_fil  
            # else:
            #     df_fil = df_fil[df_fil['year'].isin(year_sl)]
            # with f6:
            #     week_sl = st.multiselect("Week",['All']+df_fil['week'].unique().tolist(),key=46)
            #     if "All" in week_sl:
            #         week_sl = df_fil['week'].unique().tolist()
            # if len(week_sl)==0:
            #     df_future = df_fil  
            # else:
            #     df_future = df_fil[df_fil['week'].isin(week_sl)]
    # updated_data_placeholder = st.empty()
    # st.write(df_future)
    # with updated_data_placeholder:

    #     c1, c2, c3,c4,c5,c6 = st.columns([1,1,1,1,1,1])
    #     with c1:
    #         plot_metric(
    #         "Old Price",
    #         st.session_state.old_price,
    #         prefix="",
    #         suffix="")
    #     with c2:
    #         plot_metric(
    #         "New Price",
    #         st.session_state.new_price,
    #         prefix="",
    #         suffix="")
    #     with c3:
    #         plot_metric(
    #         "Incremental Revenue",
    #         st.session_state.inc_rev,
    #         prefix="",
    #         suffix="")
    #     with c4:
    #         plot_metric(
    #         "Old Volume",
    #         st.session_state.old_volume,
    #         prefix="",
    #         suffix="")
    #     with c5:
    #         plot_metric(
    #         "Volume Change(%)",
    #         st.session_state.volume_impact,
    #         prefix="",
    #         suffix="%")
    #     with c6:
    #         plot_metric(
    #         "New Volume",
    #         st.session_state.new_volume,
    #         prefix="",
    #         suffix="")