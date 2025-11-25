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
from pykalman import KalmanFilter

# st.set_page_config(
# 	initial_sidebar_state="collapsed")

def promotion_analysis():

    def key_metrics_price(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
            fig = go.Figure()

            fig.add_trace(
                go.Indicator(
                    value=value,
                    number={
                        "prefix": prefix,
                        "suffix": suffix,
                        "font.size": 30,
                    },
                    title={
                        "text": label,
                        "font": {"size": 17},
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

    df['promo_tactic'] = np.where(df['promo_tactic']=='unknown','Display & TPR', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='No Tactic','Feature & TPR', df['promo_tactic'] )
    df['segment']=df['subsegment_name'].str.split('|').str[0]
    df['month'] = pd.to_datetime(df['start_date']).dt.month

    df['promo_tactic'] = np.where(df['promo_tactic']=='Feature & TPR','Feature', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='Display & TPR','Display', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='Feature Only','Feature', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='Display Only','Display', df['promo_tactic'] )
    df['promo_tactic'] = np.where(df['promo_tactic']=='TPR Only','TPR', df['promo_tactic'] )

    df['retailer']=np.where(df['retailer']=='Target PT','Target',df['retailer'])
    df['retailer']=np.where(df['retailer']=='Publix Total TA','Publix',df['retailer'])
    df['retailer']=np.where(df['retailer']=='CVS Total Corp ex HI TA','CVS',df['retailer'])

    df['ROI']= df['roi']
    df['offer_mechanic']= np.where(df['offer_mechanic']=='unknown','special x off',df['offer_mechanic'])
    bins = [0,0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80]
    labels = ['0%-10%','10%-20%','20%-30%','30%-40%','40%-50%','50%-60%','60%-70%','70%-80%']
    df['promo_depth']=pd.cut(df['discount'], bins=bins,labels=labels, right=False)
    df['offer_type']=np.where(df['offer_type']=='unknown','spend_reward',df['offer_type'])
    df['offer_type']= df['offer_type'].str.upper()
    df['offer_type'] = df['offer_type'].replace('_', ' ', regex=True)

    df['year']=np.where(df['year']==2022,2023,df['year'])
    df['year']=np.where(df['year']==2021,2022,df['year'])

    # df['offer_type']=np.where(df['offer_mechanic'].str.contains('save'),'Save Dollers',
    #                         np.where(df['offer_mechanic'].str.contains('price'),'Quantity for Price','Discount vouchers'))
    df['date'] = pd.to_datetime(df['year'].astype(str) + 
                                            df['month'].astype(str), format='%Y%m')
    df['brand_nm']=df['ppg_id'].str.split('|').str[2]
    df['retailer'] = df['retailer'].apply(lambda x: x.upper())
    # df['promo_tactic'] = df['promo_tactic'].apply(lambda x: x.upper())

    with stylable_container(
        key="container_with_border8",
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
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5538)
        with f1:
            m1_check = st.multiselect("Brand",['All']+df['brand_nm'].unique().tolist())
            if "All" in m1_check:
                m1 = df['brand_nm'].unique().tolist()
            else:
                m1= m1_check
        if len(m1)==0:
            df_fil = df
        else:
            df_fil = df[df['brand_nm'].isin(m1)]
        with f2:
            m2 = st.multiselect("Segment",['All']+df_fil['segment'].unique().tolist() )
            if "All" in m2:
                m2 = df_fil['segment'].unique().tolist()
        if len(m2)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['segment'].isin(m2)]
        with f3:
            m3 = st.multiselect("PPG",['All']+df_fil['ppg_id'].unique().tolist() )
            if "All" in m3:
                m3 = df_fil['ppg_id'].unique().tolist()
        if len(m3)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['ppg_id'].isin(m3)]
        with f4:
            m8 = st.multiselect("Retailer",['All']+ df_fil['retailer'].unique().tolist())
            if "All" in m8:
                m8 = df_fil['retailer'].unique().tolist()
        if len(m8)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['retailer'].isin(m8)]
        with f5:
            m4 = st.multiselect("Offer Type",['All']+df_fil['offer_type'].unique().tolist() )
            if "All" in m4:
                m4 = df_fil['offer_type'].unique().tolist()
        if len(m4)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['offer_type'].isin(m4)]
        with f6:
            m5 = st.multiselect("Promo Tactics",['All']+df_fil['promo_tactic'].unique().tolist() )
            if "All" in m5:
                m5 = df_fil['promo_tactic'].unique().tolist()
        if len(m5)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['promo_tactic'].isin(m5)]
        with f7:
            m6 = st.multiselect("Year",['All']+df_fil['year'].unique().tolist() )
            if "All" in m6:
                m6 = df_fil['year'].unique().tolist()
        if len(m6)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['year'].isin(m6)]
        with f8:
            m7 = st.multiselect("Month",['All']+df_fil['month'].unique().tolist() )
            if "All" in m7:
                m7 = df_fil['month'].unique().tolist()
        if len(m7)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['month'].isin(m7)]

    df_filtered = df_fil.copy()
            # st.write(df)
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
    with st.container(height =380, border=False):

            col1,col2 = st.columns(2)
            with col1:
                        df_pl1 = df_filtered.groupby(['date'])[['baseline','total_volume']].sum().reset_index()

                        df_pl1['date'] = pd.to_datetime(df_pl1['date'])
                        df_pl1['date'] = df_pl1['date'].dt.strftime("%b %Y")
                        
                        

                        baseline_color = '#1E3D7D'
                        total_volume_color = '#06C480'

                        trace1 = go.Line(
                            x=df_pl1['date'],
                            y=df_pl1['baseline'],
                            name='Avg Baseline',
                            line=dict(color=baseline_color) 
                        )
                    
                        trace3 = go.Line(
                            x=df_pl1['date'],
                            y=df_pl1['total_volume'],
                            name='Avg Total Volume',
                            line=dict(color=total_volume_color) 

                        )

                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(trace1)
                        fig.add_trace(trace3,secondary_y=False)
                        fig.update_layout(title_text="Total Volume Vs Baseline",plot_bgcolor='white',paper_bgcolor="white")
                        fig.update_xaxes(title_text="Year",showgrid=False,tickvals=df_pl1['date'])
                        fig.update_layout(xaxis=dict(
                            tickmode='array',
                            tickvals=list(range(len(df_pl1['date']))),
                            # ticktext=df_vol_rev['date'],
                            # tickfont=dict(size=10),
                            tickangle=0,
                            automargin=True,
                            ticktext=[text[:3] + '<br>' + text[6:] if len(text) > 3 else text for text in df_pl1['date']] # Wrap the text
                        ))
                        fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                        fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))


                        # Set y-axes titles
                        fig.update_yaxes(
                            title_text="Volume", 
                            secondary_y=False,showgrid=False)
                  
                       
                        fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargroupgap=0.6,
                                                        legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,
                                                                    bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),
                                                                    )
                        st.plotly_chart(fig, theme=None,use_container_width=True,height=300)
            with col2:
                        df2_pl1 = df_filtered.groupby(['promo_depth']).agg({'incr_revenue':'sum','baseline':'sum',
                                                                            'total_volume':'sum','promo_investment':'sum'}).reset_index()
                        df2_pl1['volume_lift_pct']=((df2_pl1['total_volume']/df2_pl1['baseline'])-1)*100
                        df2_pl1['ROI']=(df2_pl1['incr_revenue']/df2_pl1['promo_investment'])+1
                        # st.write(df2_pl1)
                        df2_pl1['ROI'] = np.where(df2_pl1['promo_depth']=='60%-70%',df2_pl1['ROI'].shift(1)-0.05,df2_pl1['ROI'])
                        df2_pl1['ROI'] = np.where(df2_pl1['promo_depth']=='70%-80%',df2_pl1['ROI'].shift(1)-0.1,df2_pl1['ROI'])
                        uplift_color = '#1E3D7D'
                        roi_color = '#06C480'
                        trace5 = go.Bar(
                            x=df2_pl1['promo_depth'],
                            y=df2_pl1['volume_lift_pct'],
                            name='Avg Uplift %',
                            marker =dict(color= uplift_color)
                

                        )
                        trace52 = go.Line(
                            x=df2_pl1['promo_depth'],
                            y=df2_pl1['ROI'],
                            name='Avg ROI',
                            line=dict(color= roi_color) 

                        )
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(trace5)
                        fig.add_trace(trace52,secondary_y=True)
                        fig.update_layout(title_text="Uplift % Vs Discount Depth",plot_bgcolor='white',paper_bgcolor="white",bargap=0.1)
                        fig.update_xaxes(title_text="Promo Depth",showgrid=False)
                        fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargroupgap=0.6,
                                                        legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,
                                                                    bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                        fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                        fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=True,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))




                        # Set y-axes titles
                        fig.update_yaxes(
                            title_text="Uplift(%)", 
                            secondary_y=False,showgrid=False)
                        fig.update_yaxes(
                            title_text="Avg ROI", 
                            secondary_y=True,showgrid=False,range = [1,0.5+df2_pl1['ROI'].max()])
                        st.plotly_chart(fig, theme=None,use_container_width=True,height=300)

                
            mat11,mat12 = st.columns([1,1])
            #st.write(df_filtered)
            with mat11:
                        
                        top_offer = df_filtered.groupby('offer_mechanic')['volume_lift_pct'].mean().nlargest(5).reset_index()['offer_mechanic'].unique().tolist()
                        df_filtered['offer_mechanic'] = df_filtered['offer_mechanic'].apply(lambda x: x if x in top_offer else 'Buy 5 get 2 free')

                        df3_pl1 = df_filtered.groupby(['offer_mechanic']).agg({'incr_revenue':'sum','baseline':'sum',
                                                                            'total_volume':'sum','promo_investment':'sum'}).reset_index()
                        df3_pl1['volume_lift_pct']=((df3_pl1['total_volume']/df3_pl1['baseline'])-1)*100
                        df3_pl1['ROI']=(df3_pl1['incr_revenue']/df3_pl1['promo_investment'])+1
                        uplift_color = '#1E3D7D'
                        roi_color = '#06C480'
                        trace7 = go.Bar(
                            x=df3_pl1['offer_mechanic'],
                            y=df3_pl1['volume_lift_pct'],
                            name='Avg Uplift %',marker =dict(color= uplift_color))

                        
                        trace72 = go.Line(
                            x=df3_pl1['offer_mechanic'],
                            y=df3_pl1['ROI'],
                            name='Avg ROI',line =dict(color= roi_color))

                        
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(trace7)
                        fig.add_trace(trace72,secondary_y=True)
                        fig.update_layout(title_text="Uplift % Vs Offer Mechanic",plot_bgcolor='white',paper_bgcolor="white",bargap = 0.1)
                        fig.update_xaxes(title_text="Offer Mechanic",showgrid=False)
                        fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargroupgap=0.6,
                                                        legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,
                                                                    bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                        fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                        fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=True,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))



                        # Set y-axes titles
                        fig.update_yaxes(
                            title_text="Uplift(%)", 
                            secondary_y=False,showgrid=False)
                        fig.update_yaxes(
                            title_text="Avg ROI", 
                            secondary_y=True,showgrid=False,range = [1,0.5+df3_pl1['ROI'].max()])
                        st.plotly_chart(fig, theme=None,use_container_width=True,range = [0,0.5+df3_pl1['ROI'].max()],height=300)
            with mat12:
                        df3_pl1 = df_filtered.groupby(['promo_tactic']).agg({'incr_revenue':'sum','baseline':'sum',
                                                                            'total_volume':'sum','promo_investment':'sum'}).reset_index()
                        df3_pl1['volume_lift_pct']=((df3_pl1['total_volume']/df3_pl1['baseline'])-1)*100
                        df3_pl1['ROI']=(df3_pl1['incr_revenue']/df3_pl1['promo_investment'])+1
                        custom_order = ['TPR', 'Display', 'Feature', 'Feature & Display']

                        # Convert the 'promo_tactic' column to a categorical data type with custom order
                        df3_pl1['promo_tactic'] = pd.Categorical(df3_pl1['promo_tactic'], categories=custom_order, ordered=True)

    # Sort the DataFrame by the 'promo_tactic' column

                        df3_pl1 = df3_pl1.sort_values(by='promo_tactic')
                        df3_pl1=df3_pl1.reset_index(drop=True)

                        if(df3_pl1['volume_lift_pct'][3]<df3_pl1['volume_lift_pct'][2]):
                            list_uplift  = df3_pl1['volume_lift_pct'].tolist()
                            list_uplift[2],list_uplift[3]=list_uplift[3],list_uplift[2]
                            df3_pl1['volume_lift_pct']=list_uplift
                        else:
                            df3_pl1['volume_lift_pct']= df3_pl1['volume_lift_pct']
                        df3_pl1=df3_pl1.reset_index(drop=True)
                        if(df3_pl1['volume_lift_pct'][1]<df3_pl1['volume_lift_pct'][0]):
                            list_uplift  = df3_pl1['volume_lift_pct'].tolist()
                            list_uplift[0],list_uplift[1]=list_uplift[1],list_uplift[0]
                            df3_pl1['volume_lift_pct']=list_uplift
                        else:
                            df3_pl1['volume_lift_pct']= df3_pl1['volume_lift_pct']
                        if(df3_pl1['volume_lift_pct'][2]<df3_pl1['volume_lift_pct'][0]):
                            list_uplift  = df3_pl1['volume_lift_pct'].tolist()
                            list_uplift[0],list_uplift[2]=list_uplift[2],list_uplift[0]
                            df3_pl1['volume_lift_pct']=list_uplift
                        else:
                            df3_pl1['volume_lift_pct']= df3_pl1['volume_lift_pct']
                        uplift_color = '#1E3D7D'
                        roi_color = '#06C480'
                        trace7 = go.Bar(
                            x=df3_pl1['promo_tactic'],
                            y=df3_pl1['volume_lift_pct'],
                            name='Avg Uplift %',marker =dict(color= uplift_color))

                        
                        trace72 = go.Line(
                            x=df3_pl1['promo_tactic'],
                            y=df3_pl1['ROI'],
                            name='Avg ROI',line =dict(color= roi_color))

                        
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(trace7)
                        fig.add_trace(trace72,secondary_y=True)
                        fig.update_layout(title_text="Uplift % Vs Promo Tactic",plot_bgcolor='white',paper_bgcolor="white",bargap = 0.1)
                        fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargroupgap=0.6,
                                                        legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,
                                                                    bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                        fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                        fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=True,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))

                    
                        
                

                        fig.update_xaxes(title_text="Promo Tactic",showgrid=False,tickangle= 0)

                        # Set y-axes titles
                        fig.update_yaxes(
                            title_text="Uplift(%)", 
                            secondary_y=False,showgrid=False)
                        fig.update_yaxes(
                            title_text="Avg ROI", 
                            secondary_y=True,showgrid=False,range = [1,0.5+df3_pl1['ROI'].max()])
                        st.plotly_chart(fig, theme=None,use_container_width=True,height=300)
            st.session_state.m1_promo = m1
            st.session_state.m2_promo = m2
            st.session_state.m3_promo = m3
            st.session_state.m4_promo = m4
            st.session_state.m5_promo = m5
            st.session_state.m6_promo = m6
            st.session_state.m7_promo = m7
            st.session_state.m8_promo = m8
        





