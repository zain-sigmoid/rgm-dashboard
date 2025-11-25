import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from plotly.subplots import make_subplots
import streamlit_extras
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from utlis import key_metrics_price3,convert_to_abbreviated
import datetime

def drill_through():


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
    if "user_input_promo" in st.session_state:
        df=st.session_state.user_input_promo
        with stylable_container(
            key="container_with_border4",
            css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: calc(1em - 1px);
                        background-color: white;
                    }
                    """,
                    ):
            f0,f1,f2,f3,f4,f5,f6,f7,f8 = st.columns([1,1,1,1,1,1,1,1,1.5])
            df2 = df.copy()
            # df2['segment']=df2['subsegment_name'].str.split('|').str[0]
            # df2['month'] = pd.to_datetime(df2['start_dates']).dt.month
            # # df2['roi'] = np.where(df2['promo_investment'] != 0, 
            # #             (df2['volume_lift_pct'] * df2['promo_price_unit']) / df2['promo_investment'], 0)*100
            # df2['ROI%']= df2['roi']*100
            # df2['offer_mechanic']= np.where(df2['offer_mechanic']=='unknown','special x off',df2['offer_mechanic'])
            # bins = [0,10,20,30,40,50,60,70,80]
            # labels = ['0%-10%','10%-20%','20%-30%','30%-40%','40%-50%','50%-60%','60%-70%','70%-80%']
            # df2['promo_bins']=pd.cut(df2['discount'], bins=bins,labels=labels, right=False)
            # df2['offer_type']=np.where(df2['offer_type']=='unknown','spend_reward',df2['offer_type'])
            # df2['offer_type']= df2['offer_type'].str.upper()
            # df2['offer_type'] = df2['offer_type'].replace('_', ' ', regex=True)
            # # df2['offer_type']=np.where(df2['offer_mechanic'].str.contains('save'),'Save Dollers',
            # #                         np.where(df2['offer_mechanic'].str.contains('price'),'Quantity for Price','Discount vouchers'))
            # df2['start_dates'] = pd.to_datetime(df2['start_date'])
            # df2['start_dates'] = df2['start_dates'].dt.strftime("%Y/%m/%d")

            # st.write(df2)

            with f0:
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5545)
            with f1:
                m1 = st.multiselect("Retailer",['All']+ df2['retailer'].unique().tolist(),default =st.session_state.m1_promo )
                if "All" in m1:
                    m1 = df2['retailer'].unique().tolist()
            if len(m1)==0:
                df_fil = df2
            else:
                df_fil = df2[df2['retailer'].isin(m1)]
            with f2:
                m2 = st.multiselect("Segment",['All']+df_fil['segment'].unique().tolist(),default =st.session_state.m2_promo )
                if "All" in m2:
                    m2 = df_fil['segment'].unique().tolist()
            if len(m2)==0:
                df_fil = df_fil
            else:
                df_fil = df_fil[df_fil['segment'].isin(m2)]
            with f3:
                m3 = st.multiselect("PPG",['All']+df_fil['ppg_id'].unique().tolist(),default =st.session_state.m3_promo )
                if "All" in m3:
                    m3 = df_fil['ppg_id'].unique().tolist()
            if len(m3)==0:
                df_fil = df_fil
            else:
                df_fil = df_fil[df_fil['ppg_id'].isin(m3)]
            with f4:
                m4 = st.multiselect("Offer Type",['All']+df_fil['offer_type'].unique().tolist(),default =st.session_state.m4_promo)
                if "All" in m4:
                    m4 = df_fil['offer_type'].unique().tolist()
            if len(m4)==0:
                df_fil = df_fil
            else:
                df_fil = df_fil[df_fil['offer_type'].isin(m4)]
            with f5:
                 m5_check = st.date_input("Start Date",value=st.session_state.m5_promo, max_value=datetime.date(2024, 12, 31),min_value=datetime.date(2024, 1, 1),format="YYYY-MM-DD",disabled=True)

                 m5= m5_check
        # st.write(df_fil[pd.to_datetime(df_fil['start_dates'])==pd.to_datetime(m5)])
            df_fil = df_fil[pd.to_datetime(df_fil['start_dates'])==pd.to_datetime(m5)]
            #     m5 = st.multiselect("Start Date",['All']+df_fil['start_dates'].unique().tolist(),default =st.session_state.m5)
            #     if "All" in m5:
            #         m5 = df_fil['start_dates'].unique().tolist()
            # if len(m5)==0:
            #     df_fil = df_fil
            # else:
            #     df_fil = df_fil[df_fil['start_dates'].isin(m5)]
            with f6:
                m6 = st.text_input("Promo Duration (Days)", value=st.session_state.m6_promo)
            if len(m6)==0:
                df_fil = df_fil
            else:
                df_fil = df_fil[df_fil['promo_duration_days'].isin([int(m6)] if m6.isdigit() else df2['promo_duration_days'].tolist())]
            with f7:
                m7= st.text_input("Promotion Discount%", value=st.session_state.m7_promo)
                if "All" in m7:
                    m7 = df_fil['promo_depth'].unique().tolist()
            if len(m7)==0:
                df_fil = df_fil
            else:
                df_fil = df_fil[df_fil['discount'].isin([float(m7)] if m7.replace('.', '', 1).isdigit() else df_fil['discount'].tolist())]
            with f8:
                updated_data_placeholder1 = st.empty()
                # updated_data_placeholder11 = st.empty()
                with updated_data_placeholder1:
                    change = st.slider('Redemption Rate(%)', 0, 100, st.session_state.m8_promo,disabled=True)
                # with updated_data_placeholder11:
                #     st.write(round(change,2),'%')
                df_fil['Redemption Rate']= np.where(change==0,df_fil['Redemption Rate'],change/100)

        # m5 = [pd.to_datetime(date) for date in m5]
        df_filtered3 = df_fil.copy()   
        updated_data_placeholder = st.empty()
        # table
        df_filtered3['PPG-Retailer'] = df_filtered3['ppg_id'] + ' ' + df_filtered3['retailer']
        df_filtered3['discount%']= df_filtered3['discount']
        df_filtered3['Redemption Rate%']= df_filtered3['Redemption Rate']*100
        
        df_new2= df_filtered3.groupby(['PPG-Retailer']).agg({
                                'promo_price_unit':'mean',
                                'no_promo_price_unit':'mean',
                                'avg_price_unit':'mean',
                                'baseline':'sum',
                                'volume_lift_pct':'mean',
                                'incremental_volume':'sum',
                                'Redemption Rate%':'mean',
                                'discount%':'mean',
                                'promo_duration_days':'mean'}).reset_index()
        # df_new2['Redemption Rate%'] = (df_new2['no_promo_price_unit'] - df_new2['avg_price_unit'])/(df_new2['no_promo_price_unit'] - df_new2['promo_price_unit'])*100
        # df_new2['discount%'] = (df_new2['avg_price_unit']-df_new2['promo_price_unit'])/(df_new2['avg_price_unit'])*100
        df_new2['volume_lift_pct'] = (df_new2['incremental_volume'])/(df_new2['baseline'])*100

        df_new2= df_new2.drop(['promo_price_unit','no_promo_price_unit','avg_price_unit','baseline'],axis=1)
        
        df_new2.columns = [ 'PPG-Retailer','Volume Uplift%','Incremental Volume',
                                    'Redemption Rate%','Promo Discount%','Promo Duration Days']
        st.write(" ")
        st.write(" ")
        st.dataframe(df_new2,use_container_width=True)

        with updated_data_placeholder:     

            c1, c2, c3,c4 = st.columns([1,1,1,1])
            with c1:
                        key_metrics_price3(
                            "Average Uplift%",
                            str(round(st.session_state.volume_lift_pct,2))+'%',
                            'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png'
                           
                    )

            with c2:
                        key_metrics_price3(
                            "Incremental Volume ",
                            convert_to_abbreviated(st.session_state.incremental_volume),
                            'https://i.im.ge/2024/03/26/WFhf4m.Incremental-Revenue.png'
                            
                    )
                
            with c3:
                        key_metrics_price3(
                            "Baseline Volume ",
                            convert_to_abbreviated(round(st.session_state.baseline,2)),
                            'https://i.im.ge/2024/03/26/WFhpz0.Volume-Change.png'
                            
                    )
                    
            with c4:
                        key_metrics_price3(
                            "ROI% ",
                            str(round(st.session_state.ROI,2))+'%',
                            'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png'
                           
                    
                    )
            
    else:
            st.write("No input submitted")
            # f1,f2,f3,f4,f5,f6,f7 = st.columns([1,1,1,1,1,1,1,])
            # df2 = pd.read_excel('modelop4.xlsx')
            # df2['segment']=df2['subsegment_name'].str.split('|').str[0]
            # df2['month'] = pd.to_datetime(df2['start_date']).dt.month
            # df2['roi'] = np.where(df2['promo_investment'] != 0, 
            #             (df2['volume_lift_pct'] * df2['promo_price_unit']) / df2['promo_investment'], 0)*100
            # df2['ROI%']= df2['roi']/df2['total_volume']*100
            # df2['offer_mechanic']= np.where(df2['offer_mechanic']=='unknown','special x off',df2['offer_mechanic'])
            # bins = [0,10,20,30,40,50,60,70,80]
            # labels = ['0%-10%','10%-20%','20%-30%','30%-40%','40%-50%','50%-60%','60%-70%','70%-80%']
            # df2['promo_bins']=pd.cut(df2['discount'], bins=bins,labels=labels, right=False)
            # df2['offer_type']=np.where(df2['offer_mechanic'].str.contains('save'),'Save Dollers',
            #                         np.where(df2['offer_mechanic'].str.contains('price'),'Quantity for Price','Discount vouchers'))
            # df2['start_dates'] = pd.to_datetime(df2['start_date'])
            # df2['start_dates'] = df2['start_dates'].dt.strftime("%Y/%m/%d")
            #         #st.write(df2)
            # with f1:
            #     m1 = st.multiselect("Retailer",['All']+ df2['retailer'].unique().tolist(),key =70)
            #     if "All" in m1:
            #         m1 = df2['retailer'].unique().tolist()
            # if len(m1)==0:
            #     df_fil = df2
            # else:
            #     df_fil = df2[df2['retailer'].isin(m1)]
            # with f2:
            #     m2 = st.multiselect("Segment",['All']+df_fil['segment'].unique().tolist(),key =71)
            #     if "All" in m2:
            #         m2 = df_fil['segment'].unique().tolist()
            # if len(m2)==0:
            #     df_fil = df_fil
            # else:
            #     df_fil = df_fil[df_fil['segment'].isin(m2)]
            # with f3:
            #     m3 = st.multiselect("PPG",['All']+df_fil['ppg_id'].unique().tolist(),key =72)
            #     if "All" in m3:
            #         m3 = df_fil['ppg_id'].unique().tolist()
            # if len(m3)==0:
            #     df_fil = df_fil
            # else:
            #     df_fil = df_fil[df_fil['ppg_id'].isin(m3)]
            # with f4:
            #     m4 = st.multiselect("Offer Type",['All']+df_fil['offer_mechanic'].unique().tolist(),key =73)
            #     if "All" in m4:
            #         m4 = df_fil['offer_mechanic'].unique().tolist()
            # if len(m4)==0:
            #     df_fil = df_fil
            # else:
            #     df_fil = df_fil[df_fil['offer_mechanic'].isin(m4)]
            # with f5:
            #     m5 = st.multiselect("Start Date",['All']+df_fil['start_dates'].unique().tolist(),key =74)
            #     if "All" in m5:
            #         m5 = df_fil['start_dates'].unique().tolist()
            # if len(m5)==0:
            #     df_fil = df_fil
            # else:
            #     df_fil = df_fil[df_fil['start_dates'].isin(m5)]
            # with f6:
            #     m6 = st.text_input("Promo Duration (Days)",key =75)
            # if len(m6)==0:
            #     df_fil = df_fil
            # else:
            #     df_fil = df_fil[df_fil['promo_duration_days'].isin([int(m6)] if m6.isdigit() else df2['promo_duration_days'].tolist())]
            # with f7:
            #     m7= st.text_input("Promotion Discount%",key =76)
            #     if "All" in m7:
            #         m7 = df_fil['promo_depth'].unique().tolist()
            # if len(m7)==0:
            #     df_fil = df_fil
            # else:
            #     df_fil = df_fil[df_fil['discount'].isin([float(m7)] if m7.replace('.', '', 1).isdigit() else df_fil['discount'].tolist())]
            # m5 = [pd.to_datetime(date) for date in m5]
            # df_filtered3 = df_fil.copy()      

