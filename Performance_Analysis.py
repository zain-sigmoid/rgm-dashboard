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
from utlis import key_metrics_price2,convert_to_abbreviated

def performance_analysis():
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


    df = pd.read_csv('df_hist_check.csv')

    df['segment']=df['subsegment_name'].str.split('|').str[0]
    df['year']=np.where(df['year']==2022,2023,df['year'])
    df['year']=np.where(df['year']==2021,2022,df['year'])
    df['month'] = pd.to_datetime(df['start_date']).dt.month
    df['promo_tactic'] = np.where(df['promo_tactic']=='unknown','Display & TPR', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='No Tactic','Feature & TPR', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='Feature & TPR','Feature', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='Display & TPR','Display', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='Feature Only','Feature', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='Display Only','Display', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='TPR Only','TPR', df['promo_tactic'] )
    df['ROI']= df['roi']
    df['retailer']=np.where(df['retailer']=='Target PT','Target',df['retailer'])
    df['retailer']=np.where(df['retailer']=='Publix Total TA','Publix',df['retailer'])
    df['retailer']=np.where(df['retailer']=='CVS Total Corp ex HI TA','CVS',df['retailer'])
    df['offer_mechanic']= np.where(df['offer_mechanic']=='unknown','special x off',df['offer_mechanic'])
    bins = [0,0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80]
    labels = ['0%-10%','10%-20%','20%-30%','30%-40%','40%-50%','50%-60%','60%-70%','70%-80%']
    df['promo_depth']=pd.cut(df['discount'], bins=bins,labels=labels, right=False)
    df['offer_type']=np.where(df['offer_type']=='unknown','spend_reward',df['offer_type'])
    df['offer_type']= df['offer_type'].str.upper()
    df['offer_type'] = df['offer_type'].replace('_', ' ', regex=True)
    df['brand_nm']=df['ppg_id'].str.split('|').str[2]
    df['retailer'] = df['retailer'].apply(lambda x: x.upper())
    # df['offer_type']=np.where(df['offer_mechanic'].str.contains('save'),'Save Dollers',
    #                         np.where(df['offer_mechanic'].str.contains('price'),'Quantity for Price','Discount vouchers'))
    with stylable_container(
        key="container_with_border5",
        css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: white;
                }
                """,
                ):

        f0,f1,f2,f3,f4,f5,f6,f7,f8 = st.columns([1,1,1,1,1,1,1,1,1])
        with f0:
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5546)
        with f1:
            m1_check = st.multiselect("Brand",['All']+df['brand_nm'].unique().tolist(),key=146576879,default=st.session_state.m1_promo)
            if "All" in m1_check:
                m1 = df['brand_nm'].unique().tolist()
            else:
                m1= m1_check
        if len(m1)==0:
            df_fil = df
        else:
            df_fil = df[df['brand_nm'].isin(m1)]
        with f2:
            m2 = st.multiselect("Segment",['All']+df_fil['segment'].unique().tolist(),key=2,default=st.session_state.m2_promo )
            if "All" in m2:
                m2 = df_fil['segment'].unique().tolist()
        if len(m2)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['segment'].isin(m2)]
        with f3:
            m3 = st.multiselect("PPG",['All']+df_fil['ppg_id'].unique().tolist(),key=3,default=st.session_state.m3_promo )
            if "All" in m3:
                m3 = df_fil['ppg_id'].unique().tolist()
        if len(m3)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['ppg_id'].isin(m3)]
        with f4:
            m8 = st.multiselect("Retailer",['All']+ df_fil['retailer'].unique().tolist(),key=8,default=st.session_state.m8_promo)
            if "All" in m8:
                m8 = df_fil['retailer'].unique().tolist()
        if len(m8)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['retailer'].isin(m8)]
        with f5:
            m4 = st.multiselect("Offer Type",['All']+df_fil['offer_type'].unique().tolist() ,key=4,default=st.session_state.m4_promo)
            if "All" in m4:
                m4 = df_fil['offer_type'].unique().tolist()
        if len(m4)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['offer_type'].isin(m4)]
        with f6:
            m5 = st.multiselect("Promo Tactics",['All']+df_fil['promo_tactic'].unique().tolist(),key=5,default=st.session_state.m5_promo )
            if "All" in m5:
                m5 = df_fil['promo_tactic'].unique().tolist()
        if len(m5)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['promo_tactic'].isin(m5)]
        with f7:
            m6 = st.multiselect("Year",['All']+df_fil['year'].unique().tolist(),key=6 ,default=st.session_state.m6_promo)
            if "All" in m6:
                m6 = df_fil['year'].unique().tolist()
        if len(m6)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['year'].isin(m6)]
        with f8:
            m7 = st.multiselect("Month",['All']+df_fil['month'].unique().tolist() ,key=7,default=st.session_state.m7_promo)
            if "All" in m7:
                m7 = df_fil['month'].unique().tolist()
        if len(m7)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['month'].isin(m7)]

    df_filtered = df_fil.copy()
    incremental_volume = int(df_filtered["incremental_volume"].sum())
    volume = int(df_filtered["total_volume"].sum())
    investment = int(df_filtered["promo_investment"].sum())
    baseline = int(df_filtered["baseline"].sum())
    inc_rev = int(df_filtered['incr_revenue'].sum())
    volume_lift_pct = round((((volume/baseline)-1)*100),2)
    roi = (inc_rev/investment)+1
    ROI = round(roi, 2)
    count_retails = df_filtered["retailer"].nunique()
    count_segment = df_filtered["segment"].nunique()
    count_ppg = df_filtered["ppg_id"].nunique()

    c1, c2, c3,c4,c5,c6 = st.columns([1.45,1.5,1.3,1,1.55,1.7])
    with c1:
                key_metrics_price2(
                    "Count Retailer",
                    count_retails,
                    'https://i.im.ge/2024/03/26/WFhzsr.Old-Volume.png'
                    )
    with c2:
                key_metrics_price2(
                    "Count Segment",
                    count_segment,
                    'https://i.im.ge/2024/03/26/WFhpz0.Volume-Change.png'
                   )
    with c3:
                key_metrics_price2(
                    "Count PPG",
                    count_ppg,
                    'https://i.im.ge/2024/03/26/WFhzsr.Old-Volume.png'
                   )
    
    with c4:
                key_metrics_price2(
                    "ROI",
                    round(ROI,2),
                    'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png'
                   )
    with c5:
                key_metrics_price2(
                    "Average Uplift %",
                    str(volume_lift_pct)+'%',
                    'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png'
                  )
    with c6:
                key_metrics_price2(
                    "Incremental Volume",
                    convert_to_abbreviated(incremental_volume),
                    'https://i.im.ge/2024/03/26/WFhf4m.Incremental-Revenue.png'
                   )
    st.write(" ")
    df_filtered['discount%']= df_filtered['discount']*100
    df_filtered['Redemption Rate%']= df_filtered['Redemption Rate']*100
    def format_number(x):
        if isinstance(x, (int, float)):
            return '{:.2f}'.format(x)  # Format numbers to two decimal places
        return str(x)
    with st.container(height =450, border=False):
        with stylable_container(
        key="container_with_border6",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-color: white;
            }
            """,
            ):
            custom_css = """
            <style>
                .stTabs [data-baseweb="tab-list"] {
                    display: flex;
                    justify-content: left;
                }
                .stTabs [data-baseweb="tab"] {
                    background-color: #F0F2F6;
                    border: 1px solid #ddd;
                    border-radius: 10px 10px 0 0;
                    font-family: Graphik;
                    font-size: 20px;
                    color : #205B97;
                    margin: 0 5px;
                    padding: 10px 20px;
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
            tab1, tab2,tab3,tab4 = st.tabs(["Offer Mechanics", "PPG",'Subsegment','Retailer'])
            with tab1:
                        df_new= df_filtered.groupby(['offer_mechanic','retailer','ppg_id']).agg({
                                    'baseline':'sum',
                                    'promo_investment':'sum',
                                    'no_promo_price_unit':'mean',
                                    'avg_price_unit':'mean',
                                    'promo_price_unit':'mean',
                                    'volume_lift_pct':'mean',
                                    'incremental_volume':'sum',
                                    'Redemption Rate%':'mean',
                                    'discount%':'mean',
                                    'promo_duration_days':'mean'}).reset_index()
                        df_new['ROI']=(df_new['incremental_volume']/df_new['promo_investment'])+1
                        df_new['Redemption Rate%'] = (df_new['no_promo_price_unit'] - df_new['avg_price_unit'])/(df_new['no_promo_price_unit'] - df_new['promo_price_unit'])*100
                        df_new['discount%'] = (df_new['avg_price_unit']-df_new['promo_price_unit'])/(df_new['avg_price_unit'])*100
                        df_new['volume_lift_pct']=(df_new['incremental_volume']/df_new['baseline'])*100
                        df_new= df_new.drop(['promo_price_unit','no_promo_price_unit','avg_price_unit','promo_investment'],axis=1)
                        df_new.columns = ['Offer Mechanics', 'Retailer','PPG','Baseline','Avg Volume Uplift%','Incremental Volume',
                                        'Avg Redemption Rate%','Avg Promo Discount%','Avg Promo Duration Days','ROI']
                        # st.dataframe(df_new,use_container_width=True)
                        df_new['Baseline'] = df_new['Baseline'].astype(int).map('{:,}'.format)
                        df_new['Incremental Volume'] = df_new['Incremental Volume'].astype(int).map('{:,}'.format)
                        
                        html_table = df_new.to_html(index=False, classes=["dataframe"], escape=True,float_format=format_number)
                        

                        # Define custom CSS for background styling
                        custom_css = """
                        <style>
                            .dataframe {
                                background-color: #ffffff; /* Light grey */
                                border-collapse: collapse;
                                width: 100%; /* Set width to 50% */
                                font:dict(size=16);
                                font-family: Graphik; /* Change font-family */
                            }
                            th, td {
                                padding: 8px;
                                text-align: left;
                                border: 1px solid #ddd;
                            }
                            th {
                                background-color: #F2F2F2;  
                                color: Black;
                            }
                            .title {
                                font-size: 24px;
                                # font-weight: ;
                                margin-bottom: 30px;
                                margin-top: 30px;
                                font-family: Graphik;
                                color: #555867;
                                text-align: center;

                            }
                            .table-container {
                                height: 350px; /* Set the fixed height for the container */
                                overflow-y: scroll; /* Add scrollbar when content overflows */
                            }
                        </style>
                        """

                        # Combine HTML table and custom CSS
                        html_with_css = f"<div class='table-container'>{custom_css}{html_table}</div>"

                                            

                        # Display HTML table with DataTable and custom styling

                        sp1, sp2 = st.columns([9, 1])

                        with sp2:
                            with stylable_container(
                            key="green_button_4",
                            css_styles="""
                                button {
                                    background-color: #205B97;
                                    color: white;
                                    border-radius: 5px;
                                }
                                """,
                        ):
                                st.download_button(
                                    label="Download as CSV",
                                    data=df_new.to_csv(index=False),
                                    file_name="Offer Mechanics.csv",
                                    mime="text/csv",
                                    key="download_button1"  # Ensure unique key for reactivity
                                )

                        st.components.v1.html(html_with_css, height=400)
            with tab2:
                        df_new= df_filtered.groupby(['ppg_id','retailer']).agg({
                                    'baseline':'sum',
                                    'promo_investment':'sum',
                                    'no_promo_price_unit':'mean',
                                    'avg_price_unit':'mean',
                                    'promo_price_unit':'mean',
                                    'volume_lift_pct':'mean',
                                    'incremental_volume':'sum',
                                    'Redemption Rate%':'mean',
                                    'discount%':'mean',
                                    'promo_duration_days':'mean'}).reset_index()
                        df_new['ROI']=(df_new['incremental_volume']/df_new['promo_investment'])+1
                        df_new['Redemption Rate%'] = (df_new['no_promo_price_unit'] - df_new['avg_price_unit'])/(df_new['no_promo_price_unit'] - df_new['promo_price_unit'])*100
                        df_new['discount%'] = (df_new['avg_price_unit']-df_new['promo_price_unit'])/(df_new['avg_price_unit'])*100
                        df_new['volume_lift_pct']=(df_new['incremental_volume']/df_new['baseline'])*100
                        df_new= df_new.drop(['promo_price_unit','no_promo_price_unit','avg_price_unit','promo_investment'],axis=1)
                        df_new.columns = ['PPG', 'Retailer','Baseline','Avg Vol Uplift','Incremental Volume',
                                        'Avg Redemption Rate%','Avg Promo Discount%','Avg Promo Duration Days','ROI']
                        # st.dataframe(df_new,use_container_width=True)
                        df_new['Baseline'] = df_new['Baseline'].astype(int).map('{:,}'.format)
                        df_new['Incremental Volume'] = df_new['Incremental Volume'].astype(int).map('{:,}'.format)
                        html_table = df_new.to_html(index=False, classes=["dataframe"], escape=True,float_format=format_number)
                        

                        # Define custom CSS for background styling
                        custom_css = """
                        <style>
                            .dataframe {
                                background-color: #ffffff; /* Light grey */
                                border-collapse: collapse;
                                width: 100%; /* Set width to 50% */
                                font:dict(size=16);
                                font-family: Graphik; /* Change font-family */
                            }
                            th, td {
                                padding: 8px;
                                text-align: left;
                                border: 1px solid #ddd;
                            }
                            th {
                                background-color: #F2F2F2;  
                                color: Black;
                            }
                            .title {
                                font-size: 24px;
                                # font-weight: ;
                                margin-bottom: 30px;
                                margin-top: 30px;
                                font-family: Graphik;
                                color: #555867;
                                text-align: center;

                            }
                            .table-container {
                                height: 350px; /* Set the fixed height for the container */
                                overflow-y: scroll; /* Add scrollbar when content overflows */
                            }
                        </style>
                        """

                        # Combine HTML table and custom CSS
                        html_with_css = f"<div class='table-container'>{custom_css}{html_table}</div>"
                        sp1, sp2 = st.columns([9, 1])

                        with sp2:
                            with stylable_container(
                            key="green_button_1",
                            css_styles="""
                                button {
                                    background-color: #205B97;
                                    color: white;
                                    border-radius: 5px;
                                }
                                """,
                        ):
                                st.download_button(
                                    label="Download as CSV",
                                    data=df_new.to_csv(index=False),
                                    file_name="PPG.csv",
                                    mime="text/csv",
                                    key="download_button2"  # Ensure unique key for reactivity
                                )

                                            

                        # Display HTML table with DataTable and custom styling
                        st.components.v1.html(html_with_css, height=400)
            with tab3:
                        df_new= df_filtered.groupby(['subsegment_name','retailer','ppg_id']).agg({
                                    'baseline':'sum',
                                    'promo_investment':'sum',
                                    'no_promo_price_unit':'mean',
                                    'avg_price_unit':'mean',
                                    'promo_price_unit':'mean',
                                    'volume_lift_pct':'mean',
                                    'incremental_volume':'sum',
                                    'Redemption Rate%':'mean',
                                    'discount%':'mean',
                                    'promo_duration_days':'mean'}).reset_index()
                        df_new['ROI']=(df_new['incremental_volume']/df_new['promo_investment'])+1
                        df_new['Redemption Rate%'] = (df_new['no_promo_price_unit'] - df_new['avg_price_unit'])/(df_new['no_promo_price_unit'] - df_new['promo_price_unit'])*100
                        df_new['discount%'] = (df_new['avg_price_unit']-df_new['promo_price_unit'])/(df_new['avg_price_unit'])*100
                        df_new['volume_lift_pct']=(df_new['incremental_volume']/df_new['baseline'])*100
                        df_new= df_new.drop(['promo_price_unit','no_promo_price_unit','avg_price_unit','promo_investment'],axis=1)
                        df_new.columns = ['Subsegment', 'Retailer','PPG','Baseline','Avg Vol Uplift','Incremental Volume',
                                        'Avg Redemption Rate%','Avg Promo Discount%','Avg Promo Duration Days','ROI']
                        # st.dataframe(df_new,use_container_width=True)
                        df_new['Baseline'] = df_new['Baseline'].astype(int).map('{:,}'.format)
                        df_new['Incremental Volume'] = df_new['Incremental Volume'].astype(int).map('{:,}'.format)
                        html_table = df_new.to_html(index=False, classes=["dataframe"], escape=True,float_format=format_number)
                        

                        # Define custom CSS for background styling
                        custom_css = """
                        <style>
                            .dataframe {
                                background-color: #ffffff; /* Light grey */
                                border-collapse: collapse;
                                width: 100%; /* Set width to 50% */
                                font:dict(size=16);
                                font-family: Graphik; /* Change font-family */
                            }
                            th, td {
                                padding: 8px;
                                text-align: left;
                                border: 1px solid #ddd;
                            }
                            th {
                                background-color: #F2F2F2;  
                                color: Black;
                            }
                            .title {
                                font-size: 24px;
                                # font-weight: ;
                                margin-bottom: 30px;
                                margin-top: 30px;
                                font-family: Graphik;
                                color: #555867;
                                text-align: center;

                            }
                            .table-container {
                                height: 350px; /* Set the fixed height for the container */
                                overflow-y: scroll; /* Add scrollbar when content overflows */
                            }
                        </style>
                        """

                        # Combine HTML table and custom CSS

                        html_with_css = f"<div class='table-container'>{custom_css}{html_table}</div>"
                        sp1, sp2 = st.columns([9, 1])

                        with sp2:
                            with stylable_container(
                            key="green_button_2",
                            css_styles="""
                                button {
                                    background-color: #205B97;
                                    color: white;
                                    border-radius: 5px;
                                }
                                """,
                        ):
                                st.download_button(
                                    label="Download as CSV",
                                    data=df_new.to_csv(index=False),
                                    file_name="Sub Segment.csv",
                                    mime="text/csv",
                                    key="download_button3"  # Ensure unique key for reactivity
                                )

                                            

                        # Display HTML table with DataTable and custom styling
                        st.components.v1.html(html_with_css, height=400)
            with tab4:
                        df_new= df_filtered.groupby(['retailer','ppg_id']).agg({
                                    'baseline':'sum',
                                    'promo_investment':'sum',
                                    'no_promo_price_unit':'mean',
                                    'avg_price_unit':'mean',
                                    'promo_price_unit':'mean',
                                    'volume_lift_pct':'mean',
                                    'incremental_volume':'sum',
                                    'Redemption Rate%':'mean',
                                    'discount%':'mean',
                                    'promo_duration_days':'mean'}).reset_index()
                        df_new['ROI']=(df_new['incremental_volume']/df_new['promo_investment'])+1
                        df_new['Redemption Rate%'] = (df_new['no_promo_price_unit'] - df_new['avg_price_unit'])/(df_new['no_promo_price_unit'] - df_new['promo_price_unit'])*100
                        df_new['discount%'] = (df_new['avg_price_unit']-df_new['promo_price_unit'])/(df_new['avg_price_unit'])*100
                        df_new['volume_lift_pct']=(df_new['incremental_volume']/df_new['baseline'])*100
                        df_new= df_new.drop(['promo_price_unit','no_promo_price_unit','avg_price_unit','promo_investment'],axis=1)
                        df_new.columns = ['Retailer','PPG','Baseline','Avg Vol Uplift','Incremental Volume',
                                        'Avg Redemption Rate%','Avg Promo Discount%','Avg Promo Duration Days','ROI']
                        st.write(
                            f"""
                            <style>
                                .dataframe td:nth-child(1) {{
                                    background-color: blue;
                                    color: white;
                                }}
                                .dataframe td:nth-child(2) {{
                                    background-color: blue;
                                    color: white;
                                }}
                            </style>
                            """
                            , unsafe_allow_html=True
                        )
                        # st.dataframe(df_new,use_container_width=True)
                        df_new['Baseline'] = df_new['Baseline'].astype(int).map('{:,}'.format)
                        df_new['Incremental Volume'] = df_new['Incremental Volume'].astype(int).map('{:,}'.format)
                        html_table = df_new.to_html(index=False, classes=["dataframe"], escape=True,float_format=format_number)
                        

                        # Define custom CSS for background styling
                        custom_css = """
                        <style>
                            .dataframe {
                                background-color: #ffffff; /* Light grey */
                                border-collapse: collapse;
                                width: 100%; /* Set width to 50% */
                                font:dict(size=16);
                                font-family: Graphik; /* Change font-family */
                            }
                            th, td {
                                padding: 8px;
                                text-align: left;
                                border: 1px solid #ddd;
                            }
                            th {
                                background-color: #F2F2F2;  
                                color: Black;
                            }
                            .title {
                                font-size: 24px;
                                # font-weight: ;
                                margin-bottom: 30px;
                                margin-top: 30px;
                                font-family: Graphik;
                                color: #555867;
                                text-align: center;

                            }
                            .table-container {
                                height: 350px; /* Set the fixed height for the container */
                                overflow-y: scroll; /* Add scrollbar when content overflows */
                            }
                        </style>
                        """

                        # Combine HTML table and custom CSS
                        html_with_css = f"<div class='table-container'>{custom_css}{html_table}</div>"
                        sp1, sp2 = st.columns([9, 1])

                        with sp2:
                            with stylable_container(
                            key="green_button_3",
                            css_styles="""
                                button {
                                    background-color: #205B97;
                                    color: white;
                                    border-radius: 5px;
                                }
                                """,
                        ):
                                st.download_button(
                                    label="Download as CSV",
                                    data=df_new.to_csv(index=False),
                                    file_name="Retailer.csv",
                                    mime="text/csv",
                                    key="download_button4"  # Ensure unique key for reactivity
                                )

                                            

                        # Display HTML table with DataTable and custom styling
                        st.components.v1.html(html_with_css, height=400)

