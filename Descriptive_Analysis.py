import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

# st.image('sigmoid_logo.png')


def descriptive_analysis():

    

    #data

    df_final = pd.read_csv('final_pricing_consolidated_file.csv')
    df = df_final.copy()
    df=df.dropna()
    df['retailer_id'] = df['retailer_id'].apply(lambda x: x.upper())
    df['retailer_id']=np.where(df['retailer_id']=='Target PT','Target',df['retailer_id'])
    df['retailer_id']=np.where(df['retailer_id']=='Publix Total TA','Publix',df['retailer_id'])
    df['retailer_id']=np.where(df['retailer_id']=='CVS Total Corp ex HI TA','CVS',df['retailer_id'])
    df['year'] = pd.to_datetime(df['year'].astype(str), format='%Y')
    df['year'] = df['year'].dt.strftime("%Y") #**change**
    df['day']=1
    df['month_name']=df['month'].map({1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})
    # Define the order of the month names
    month_order = ['Jan', 'Feb', 'Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    # Convert month_name column to categorical data type with specified order
    df['month_name'] = pd.Categorical(df['month_name'], categories=month_order, ordered=True)
    df['year']=np.where(df['year']=='2022','2023',df['year'])
    df['year']=np.where(df['year']=='2021','2022',df['year'])
    df['date'] = pd.to_datetime(df['year'].astype(str) + 
                                            df['month'].astype(str), format='%Y%m')

    # st.title('MARKET ANALYSIS SUMMARY')
    with stylable_container(
        key="container_with_border2",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-color: white;
            }
            """,
    ):
        f0,f1,f2,f3,f4,f5 = st.columns([1,1,1,1,1,1])
        with f0:
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5548)
        with f1:
            m1 = st.multiselect("Manufacturer",['All']+ df['manufacturer_nm'].unique().tolist(),key=11)
            if "All" in m1:
                m1 = df['manufacturer_nm'].unique().tolist()
        if len(m1)==0:
            df_fil = df  
        else:          
            df_fil = df[df['manufacturer_nm'].isin(m1)]
        with f2:
            m2 = st.multiselect("Brand",['All']+df_fil['brand_nm'].unique().tolist(),key=22)
            if "All" in m2:
                m2 = df_fil['brand_nm'].unique().tolist()
        if len(m2)==0:
            df_fil = df_fil  
        else:          
            df_fil = df_fil[df_fil['brand_nm'].isin(m2)]
        with f3:
            m3 = st.multiselect("PPG ",['All']+df_fil['ppg_nm'].unique().tolist(),key=42)
            if "All" in m3:
                m3 = df_fil['ppg_nm'].unique().tolist()
        if len(m3)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['ppg_nm'].isin(m3)]
        with f4:
            m4 = st.multiselect("Retailer",['All']+df_fil['retailer_id'].unique().tolist(),key=32)
            if "All" in m4:
                m4 = df_fil['retailer_id'].unique().tolist()
        if len(m4)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['retailer_id'].isin(m4)]
        with f5:
            m5 = st.multiselect("Year",['All']+df_fil['year'].unique().tolist(),key=52)
            if "All" in m5:
                m5 = df_fil['year'].unique().tolist()
        if len(m5)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['year'].isin(m5)]
        df_filtered_com=pd.DataFrame(columns=df_fil.columns)
        check = st.checkbox('Select Competitor')
        if check:

            df_com = df[(~df['manufacturer_nm'].isin(m1))]

            df_com = df_com[(~df_com['retailer_id'].isin(m3))]
            df_com = df_com[(~df_com['ppg_nm'].isin(m4))]

            f1,f2,f3,f4 = st.columns([1,1,1,1])
            with f1:
                m1_com = st.multiselect("Manufacturer",df_com['manufacturer_nm'].unique().tolist(),key=115)
                # if "All" in m1_com:
                #     m1_com = df_com['manufacturer_nm'].unique().tolist()
            if len(m1)==0:
                df_fil_com = df_com 
            else:          
                df_fil_com = df_com[df_com['manufacturer_nm'].isin(m1_com)]
            with f2:
                m2_com = st.multiselect("Brand",df_fil_com['brand_nm'].unique().tolist(),key=2252)
            if len(m2_com)==0:
                df_fil_com = df_fil_com  
            else:          
                df_fil_com = df_fil_com[df_fil_com['brand_nm'].isin(m2_com)]
            with f3:
                m3_com = st.multiselect("PPG ",df_fil_com['ppg_nm'].unique().tolist(),key=422)
                if "All" in m3_com:
                    m3_com = df_fil_com['ppg_nm'].unique().tolist()
            if len(m3_com)==0:
                df_fil_com = df_fil_com  
            else:
                df_fil_com = df_fil_com[df_fil_com['ppg_nm'].isin(m3_com)]
            with f4:
                m4_com = st.multiselect("Retailer",df_fil_com['retailer_id'].unique().tolist(),key=322)
                if "All" in m3:
                    m4_com = df_fil_com['retailer_id'].unique().tolist()
            if len(m4_com)==0:
                df_fil_com = df_fil_com  
            else:
                df_fil_com = df_fil_com[df_fil_com['retailer_id'].isin(m4_com)]
            if len(m5)==0:
                df_fil_com = df_fil_com  
            else:
                df_fil_com = df_fil_com[df_fil_com['year'].isin(m5)]

            df_filtered_com = df_fil_com.copy()
    df_filtered = df_fil.copy()

    
    with stylable_container(
        key="container_with_border3",
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
        main_tabs = ['KPI Trend','Comparison VS Competition']
        tab1,tab3=st.tabs(main_tabs)
        with tab1:

            listTabs = ['Volume Vs Revenue','Volume Vs Price',"Volume Vs Distritubion"]
            tab1, tab2,tab4 = st.tabs(listTabs)
            with tab1:
                df_vol_rev = df_filtered.groupby(['date']).agg({'volume':'sum','revenue':'sum'}).reset_index()
                df_vol_rev['date'] = pd.to_datetime(df_vol_rev['date'])
                df_vol_rev['date'] = df_vol_rev['date'].dt.strftime("%b %Y")
                trace1 = go.Line(x=df_vol_rev['date'],
                    y=df_vol_rev['volume'],
                    name='Volume',marker=dict(color='#205B97'))
                trace5 = go.Line(x=df_vol_rev['date'],
                    y=df_vol_rev['revenue'],
                    name='Revenue',marker=dict(color='#06C480'))
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(trace1)
                fig.add_trace(trace5, secondary_y=True)

                fig.update_layout(title_text="Volume Vs Revenue",paper_bgcolor="white",height = 500,plot_bgcolor="white")
                fig.update_xaxes(title_text="Month",showgrid=False,tickangle= 30,tickvals=df_vol_rev['date'],title_standoff=30)
                fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(df_vol_rev['date']))),
                        # ticktext=df_vol_rev['date'],
                        # tickfont=dict(size=10),
                        tickangle=0,
                        automargin=True,
                        ticktext=[text[:3] + '<br>' + text[3:] if len(text) > 3 else text for text in df_vol_rev['date']] # Wrap the text
                    ),legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.46,bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),
                    )
                fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=True,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))


                # Set y-axes titles
                fig.update_yaxes(
                    title_text="Volume", 
                    secondary_y=False,showgrid=False,range = [0,55000000+df_vol_rev['volume'].max()],title_standoff=30)
                fig.update_yaxes(
                    title_text="Revenue", 
                    secondary_y=True,showgrid=False,title_standoff=30)
                st.plotly_chart(fig, theme=None,use_container_width=True)
            with tab4:
                    df_plot = df_filtered.copy()
                    # df_plot['date']=pd.to_datetime(df_plot[['year', 'month', 'day']])
                    df_plot=(df_plot.groupby(['date']).agg({'volume':'sum','acv_wtd_distribution':'mean'}).reset_index().round(2))
                    df_plot=df_plot.sort_values('date')
                    #  df_plot=df_plot.sort_values('date')
                    df_plot['date'] = pd.to_datetime(df_plot['date'])
                    df_plot['date'] = df_plot['date'].dt.strftime("%b %Y")
                    trace1 = go.Line(x=df_plot['date'],
                        y=df_plot['volume'],
                        name='Volume',line=dict(color='#205B97'))
                    trace2 = go.Line(x=df_plot['date'],
                        y=df_plot['acv_wtd_distribution'],
                        name='Distribution',line=dict(color='#06C480'))
                    fig = make_subplots(specs=[[{"secondary_y": True}]])
                    fig.add_trace(trace1)
                    fig.add_trace(trace2,secondary_y=True)
                    fig.update_layout(title_text="Volume Vs Distribution",paper_bgcolor="white",height = 500,plot_bgcolor="white")
                    fig.update_xaxes(title_text="Month",showgrid=False,tickangle= 30,tickvals=df_vol_rev['date'],title_standoff=30)
                    fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(df_plot['date']))),
                        # ticktext=df_vol_rev['date'],
                        # tickfont=dict(size=10),
                        tickangle=0,
                        automargin=True,
                        ticktext=[text[:3] + '<br>' + text[3:] if len(text) > 3 else text for text in df_plot['date']] # Wrap the text
                    ),legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.46,bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                    fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                    fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=True,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))


                    # Set y-axes titles
                    fig.update_yaxes(
                        title_text="Volume", 
                        secondary_y=False,showgrid=False,range = [0,55000000+df_plot['volume'].max()],title_standoff=30)
                    fig.update_yaxes(
                        title_text="Distribution", 
                        secondary_y=True,showgrid=False)
                    st.plotly_chart(fig, theme=None,use_container_width=True,height = 800)
                    
            with tab2:
                        df_plot = df_filtered.copy()

                        df_plot=(df_plot.groupby(['date']).agg({'volume':'sum','price':'mean'}).reset_index().round(2))
                        df_plot=df_plot.sort_values('date')

                        df_plot['date'] = pd.to_datetime(df_plot['date'])
                        df_plot['date'] = df_plot['date'].dt.strftime("%b %Y")
                        trace1 = go.Line(x=df_plot['date'],
                            y=df_plot['volume'],
                            name='Volume',line=dict(color='#205B97'))
                        trace2 = go.Line(x=df_plot['date'],
                            y=df_plot['price'],
                            name='Price',line=dict(color='#06C480'))
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(trace1)
                        fig.add_trace(trace2,secondary_y=True)
                        fig.update_layout(title_text="Volume Vs Price",paper_bgcolor="white",height = 500,plot_bgcolor="white")
                        fig.update_xaxes(title_text="Month",showgrid=False,tickangle= 30,tickvals=df_vol_rev['date'],title_standoff=30)
                        fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),xaxis=dict(
                            tickmode='array',
                            tickvals=list(range(len(df_plot['date']))),
                            # ticktext=df_vol_rev['date'],
                            # tickfont=dict(size=10),
                            tickangle=0,
                            automargin=True,
                            ticktext=[text[:3] + '<br>' + text[3:] if len(text) > 3 else text for text in df_plot['date']] # Wrap the text
                        ),legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.46,bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),
                       )
                        fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                        fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=True,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))


                    # Set y-axes titles
                        fig.update_yaxes(
                            title_text="Volume", 
                            secondary_y=False,showgrid=False,range = [0,55000000+df_plot['volume'].max()],title_standoff=30)
                        fig.update_yaxes(
                            title_text="Price", 
                            secondary_y=True,showgrid=False)
                        st.plotly_chart(fig, theme=None,use_container_width=True,height = 800)
        with tab3:
            # st.write(df_filtered_com.columns)
            # with tab5:
            if check:
    
                com_tabs = ['Own Price Vs Competitor Price','Own Distribution Vs Competitor Distribution']
                tab1,tab3=st.tabs(com_tabs)
                with tab1:
                    df_price = (df_filtered.groupby(['date']).agg({'price':'mean'}).reset_index().round(2))
                    df_price_com = (df_filtered_com.groupby(['date']).agg({'price':'mean'}).reset_index().round(2))

                    df_price = df_price.sort_values(['date'])
                    df_price['date'] = pd.to_datetime(df_price['date'])
                    df_price['date'] = df_price['date'].dt.strftime("%b %Y")
                    df_price_com = df_price_com.sort_values(['date'])
                    df_price_com['date'] = pd.to_datetime(df_price_com['date'])
                    df_price_com['date'] = df_price_com['date'].dt.strftime("%b %Y")
                    trace1 = go.Line(x=df_price['date'],
                        y=df_price['price'],
                        name='Price',line=dict(color='#205B97'))
                    trace2 = go.Line(x=df_price_com['date'],
                        y=df_price_com['price'],
                        name='Competitor Price',line=dict(color='#06C480'))
                    fig = make_subplots(specs=[[{"secondary_y": False}]])
                    fig.add_trace(trace1)
                    fig.add_trace(trace2)
                    fig.update_layout(title_text="Own Price Vs Competitor Price",paper_bgcolor="white",font=dict(size=14),height=500,plot_bgcolor="white")
                    fig.update_xaxes(title_text="Month",showgrid=False,tickangle= 30,tickvals=df_price['date'],title_standoff=30)
                    fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),xaxis=dict(
                                tickmode='array',
                                tickvals=list(range(len(df_price_com['date']))),
                                # ticktext=df_vol_rev['date'],
                                # tickfont=dict(size=10),
                                tickangle=0,
                                automargin=True,
                                ticktext=[text[:3] + '<br>' + text[3:] if len(text) > 3 else text for text in df_price_com['date']] # Wrap the text
                            ),legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                    fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))
                    fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))


                    # Set y-axes titles
                    fig.update_yaxes(
                        title_text="Price", 
                        secondary_y=False,showgrid=False)
                    fig.update_yaxes(showgrid=False)
                    st.plotly_chart(fig, theme=None,use_container_width=True)
                    
                with tab3:
                    df_price = (df_filtered.groupby(['date']).agg({'acv_wtd_distribution':'mean'}).reset_index().round(0))
                    df_price_com = (df_filtered_com.groupby(['date']).agg({'acv_wtd_distribution':'mean'}).reset_index().round(0))

                    df_price = df_price.sort_values(['date'])
                    df_price['date'] = pd.to_datetime(df_price['date'])
                    df_price['date'] = df_price['date'].dt.strftime("%b %Y")
                    df_price_com = df_price_com.sort_values(['date'])
                    df_price_com['date'] = pd.to_datetime(df_price_com['date'])
                    df_price_com['date'] = df_price_com['date'].dt.strftime("%b %Y")
                    trace1 = go.Line(x=df_price['date'],
                        y=df_price['acv_wtd_distribution'],
                        name='Distribution',line=dict(color='#205B97'))
                    trace2 = go.Line(x=df_price_com['date'],
                        y=df_price_com['acv_wtd_distribution'],
                        name='Competitor Distribution',line=dict(color='#06C480'))
                    fig = make_subplots(specs=[[{"secondary_y": False}]])
                    fig.add_trace(trace1)
                    fig.add_trace(trace2)
                    fig.update_layout(title_text="Own Distribution Vs Competitor Distribution",paper_bgcolor="white",height=500,plot_bgcolor="white",
                                    )
                    fig.update_xaxes(title_text="Month",showgrid=False,tickangle= 30,tickvals=df_price['date'],title_standoff=30)
                    fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),xaxis=dict(
                                tickmode='array',
                                tickvals=list(range(len(df_price_com['date']))),
                                # ticktext=df_vol_rev['date'],
                                # tickfont=dict(size=10),
                                tickangle=0,
                                automargin=True,
                                ticktext=[text[:3] + '<br>' + text[3:] if len(text) > 3 else text for text in df_price_com['date']] # Wrap the text
                            ),legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                    fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))
                    fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))


                    # Set y-axes titles
                    fig.update_yaxes(
                        title_text="Distribution", 
                        secondary_y=False,showgrid=False)
                    fig.update_yaxes(showgrid=False)
                    st.plotly_chart(fig, theme=None,use_container_width=True)
            else:
                com_tabs = ['Own Price Vs Competitor Price','Own Distribution Vs Competitor Distribution']
                tab1,tab3=st.tabs(com_tabs)
                with tab1:
                    df_price = (df_filtered.groupby(['date']).agg({'price':'mean'}).reset_index().round(2))

                    df_price = df_price.sort_values(['date'])
                    df_price['date'] = pd.to_datetime(df_price['date'])
                    df_price['date'] = df_price['date'].dt.strftime("%b %Y")
                    trace1 = go.Line(x=df_price['date'],
                        y=df_price['price'],
                        name='Price',line=dict(color='#205B97'))

                    fig = make_subplots(specs=[[{"secondary_y": False}]])
                    fig.add_trace(trace1)

                    fig.update_layout(title_text="Own Price Vs Competitor Price",paper_bgcolor="white",font=dict(size=14),height=500,plot_bgcolor="white")
                    fig.update_xaxes(title_text="Month",showgrid=False,tickangle= 30,tickvals=df_price['date'],title_standoff=30)
                    fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),xaxis=dict(
                                tickmode='array',
                                tickvals=list(range(len(df_price['date']))),
                                # ticktext=df_vol_rev['date'],
                                # tickfont=dict(size=10),
                                tickangle=0,
                                automargin=True,
                                ticktext=[text[:3] + '<br>' + text[3:] if len(text) > 3 else text for text in df_price['date']] # Wrap the text
                            ),legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                    fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))
                    fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))


                    # Set y-axes titles
                    fig.update_yaxes(
                        title_text="Price", 
                        secondary_y=False,showgrid=False)
                    fig.update_yaxes(showgrid=False)
                    st.plotly_chart(fig, theme=None,use_container_width=True)
                    
                with tab3:
                    df_price = (df_filtered.groupby(['date']).agg({'acv_wtd_distribution':'mean'}).reset_index().round(0))


                    df_price = df_price.sort_values(['date'])
                    df_price['date'] = pd.to_datetime(df_price['date'])
                    df_price['date'] = df_price['date'].dt.strftime("%b %Y")

                    trace1 = go.Line(x=df_price['date'],
                        y=df_price['acv_wtd_distribution'],
                        name='Distribution',line=dict(color='#205B97'))
                    fig = make_subplots(specs=[[{"secondary_y": False}]])
                    fig.add_trace(trace1)
                    fig.update_layout(title_text="Own Distribution Vs Competitor Distribution",paper_bgcolor="white",height=500,plot_bgcolor="white",
                                    )
                    fig.update_xaxes(title_text="Month",showgrid=False,tickangle= 30,tickvals=df_price['date'],title_standoff=30)
                    fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),xaxis=dict(
                                tickmode='array',
                                tickvals=list(range(len(df_price['date']))),
                                # ticktext=df_vol_rev['date'],
                                # tickfont=dict(size=10),
                                tickangle=0,
                                automargin=True,
                                ticktext=[text[:3] + '<br>' + text[3:] if len(text) > 3 else text for text in df_price['date']] # Wrap the text
                            ),legend=dict(orientation='h',yanchor="top", y=-0.3, xanchor="center", x=0.5,bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')))
                    fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))
                    fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                    tickfont=dict(size=14, family='Graphik', color='black'))


                    # Set y-axes titles
                    fig.update_yaxes(
                        title_text="Distribution", 
                        secondary_y=False,showgrid=False)
                    fig.update_yaxes(showgrid=False)
                    st.plotly_chart(fig, theme=None,use_container_width=True)



            





            

