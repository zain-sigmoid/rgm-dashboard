import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
from utlis import key_metrics_price,convert_to_abbreviated, key_metrics_price4, key_metrics_price4
def simulation_analysis():


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

    with stylable_container(
        key="container_with_border9",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-color: white;
            }
            """,
    ):
        f0,f1,f2,f3,f4= st.columns([1,1,1,1,1])
        with f0:
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5550)
        with f1:
            m1_check = st.multiselect("Manufacturer",['All']+ df['manufacturer_nm'].unique().tolist(),key=111)
            if "All" in m1_check:
                m1 = df['manufacturer_nm'].unique().tolist()
            else:
                m1 = m1_check
        if len(m1)==0:
            df_fil = df  
        else:          
            df_fil = df[df['manufacturer_nm'].isin(m1)]
        with f2:
            m2_check = st.multiselect("Brand",['All']+df_fil['brand_nm'].unique().tolist(),key=222)
            if "All" in m2_check:
                m2 = df_fil['brand_nm'].unique().tolist()
            else:
                m2= m2_check
        if len(m2)==0:
            df_fil = df_fil  
        else:          
            df_fil = df_fil[df_fil['brand_nm'].isin(m2)]
        with f3:
            m3_check = st.multiselect("PPG ",['All']+df_fil['ppg_nm'].unique().tolist(),key=444)
            if "All" in m3_check:
                m3 = df_fil['ppg_nm'].unique().tolist()
            else:
                m3 = m3_check
        if len(m3)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['ppg_nm'].isin(m3)]
        with f4:
            m4_check = st.multiselect("Retailer",['All']+df_fil['retailer_id'].unique().tolist(),key=333)
            if "All" in m4_check:
                m4 = df_fil['retailer_id'].unique().tolist()
            else:
                m4= m4_check
        if len(m4)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['retailer_id'].isin(m4)]
    
          
    price_latest = df_fil[(df_fil['year']==df_fil['year'].max())&(df_fil['week']==52)][['ppg_nm','retailer_id','price']]
    df_new = df_fil[df_fil['year'].isin(['2021','2022'])].copy()
    df_new['year']=df_new['year'].replace({'2021':2023,'2022':2024})
    df_new=df_new[df_new['year']==2024]
    df_future = pd.merge(df_new,price_latest, on =['ppg_nm','retailer_id'], how='left', suffixes=('','_latest'))

    df_future=df_future.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm','year']).agg({'Price_coeff':'mean','price':'mean','acv_wtd_distribution':'mean',
                                                                                                  'Distribution_coeff':'mean','xpi_final':'mean','com_price_coef':'mean',
                                                                                                  're_intercept':'mean','d_intercept':'mean','volume':'sum'}).reset_index()

    df_filtered_temp = df_future.copy()
    df_filtered_temp['new_price']= np.nan
    df_filtered_temp['chnage%'] = np.nan
    df_filtered_temp['com_new_price']= np.nan
    df_filtered_temp['com_chnage%'] = np.nan
    df_filtered_temp['distribution']= np.nan
    df_filtered_temp['New cometitor Price']= False
    df_filtered_temp['New Price']= False
    df_filtered_temp['Change Distribution']= False

    updated_data_placeholder10 = st.empty()
    updated_data_placeholder2 = st.empty()
    df_input = df_filtered_temp[['manufacturer_nm','brand_nm','retailer_id','ppg_nm','year',
                    'Price_coeff','price','New Price','new_price','chnage%','acv_wtd_distribution','Change Distribution','distribution','Distribution_coeff',
                    'xpi_final','com_price_coef','New cometitor Price','com_new_price','com_chnage%','volume','re_intercept','d_intercept']]

    df_input.columns = ['Manufacturer','Brand', 'Retailer', 'PPG','Year',
                        'Elasticity','Price','Price Flag','New Price','Change%','Distribution','Distribution Flag','New Distribution','Distribution Elasticity',
                        'Competitor Price','Competitor Price Elasticity','Competitor Price Flag','New Competitor Price','Competitor Price Change%','Volume','re_Intercept','Intercept']

    with stylable_container(
        key="container_with_border10",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-color: white;
            }
            """,
    ):
        col1,col2,col3,col4,col5 = st.columns([1,1,1,1,1])
        with col1:
            
            updated_data_placeholder1 = st.empty()
            updated_data_placeholder11 = st.empty()

            with updated_data_placeholder11:
                chnage = st.slider('Price Change %', -20, +20, 0,disabled=False)
            with updated_data_placeholder1:

                key_metrics_price4('Price Change %',round(chnage,2))
        with col2:

            c1,c2=st.columns([1,1])
            with c1:
                key_metrics_price4("Current price", round(df_input['Price'].mean(),2))
            with c2:
                updated_data_placeholder = st.empty()

            if(chnage==0):
                price = st.number_input("New Price", value=0.0, placeholder="Type a number...",step=.1,min_value=0.0,
                                        max_value=1.2*round(df_input['Price'].mean(),2))
                with updated_data_placeholder:

                    if price==0:

                        key_metrics_price4('New Price',round(df_input['Price'].mean(),2))
                    else:
                        key_metrics_price4('New Price',round(price,2)) 
                with updated_data_placeholder1:
                    if price ==0:

                        key_metrics_price4('Price Change %',round(((df_input['Price'].mean()/df_input['Price'].mean())-1)*100,2))
                    else:

                        key_metrics_price4('Price Change %',round(((price/round(df_input['Price'].mean(),2))-1)*100,2))
                if price!=0:
                    with updated_data_placeholder11:
                        chnage = st.slider('Price Change %', -20.0, +20.0, round(((price/round(df_input['Price'].mean(),2))-1)*100,2),disabled=True)

            else:
                price = st.number_input("New Price", value=df_input['Price'].mean()*((100+chnage)/100), disabled=True,step=.1,min_value=0.0,
                                        max_value=1.2*round(df_input['Price'].mean(),2))
                with updated_data_placeholder:

                    key_metrics_price4('New Price',round(price,2))
                with updated_data_placeholder1:

                    key_metrics_price4('Price Change %',round(((price/df_input['Price'].mean())-1)*100,2))
        with col3:

            c1,c2=st.columns([1,1])
            with c1:
                key_metrics_price4('Current Distribution', int(df_input['Distribution'].mean()))
            with c2:
                updated_data_placeholder = st.empty()
            wd = st.number_input("New Distribution", value=0, disabled=False,min_value=0,max_value=100)
            with updated_data_placeholder:

                if wd==0:
                    key_metrics_price4('New Distribution',int(df_input['Distribution'].mean()))
                else:
                    key_metrics_price4('New Distribution',wd)
        with col4:
            updated_data_placeholder2 = st.empty()
            updated_data_placeholder21 = st.empty()
            with updated_data_placeholder21:
                com_chnage = st.slider('Competitor Price Change %', -20, +20, 0,disabled=False)
            with updated_data_placeholder2:
                #st.write('New Competitor Price',round(com_chnage,2))
                key_metrics_price4('Competitor Price Change %',round(com_chnage,2))
        with col5:

            c1,c2=st.columns([1,0.9])
            with c1:
                key_metrics_price4('Current Competitor Price',round(df_input['Competitor Price'].mean(),2))
            with c2:
                updated_data_placeholder = st.empty()
            if(com_chnage==0):
                com_price = st.number_input("New Competitor Price", value=0.0, placeholder="Type a number...",step=.1,min_value=0.0,
                                        max_value=1.2*round(df_input['Competitor Price'].mean(),2))
                with updated_data_placeholder:
                    if com_price==0:

                        key_metrics_price4('New Competitor Price',round(df_input['Competitor Price'].mean(),2))
                    else:

                        key_metrics_price4('New Competitor Price',round(com_price,2))
                with updated_data_placeholder2:
                    if com_price==0:

                        key_metrics_price4('Competitor Price Change %',round(((df_input['Competitor Price'].mean()/df_input['Competitor Price'].mean())-1)*100,2))
                    else:

                        key_metrics_price4('Competitor Price Change %',round(((com_price/round(df_input['Competitor Price'].mean(),2))-1)*100,2))
                if com_price!=0:
                    with updated_data_placeholder21:
                        com_chnage = st.slider('Competitor Price Change %', -20.0, +20.0, round(((com_price/round(df_input['Competitor Price'].mean(),2))-1)*100,2),disabled=True)
            else:
                com_price = st.number_input("New Competitor Price", value=df_input['Competitor Price'].mean()*((100+com_chnage)/100), disabled=True,step=.1,min_value=0.0,
                                        max_value=1.2*round(df_input['Competitor Price'].mean(),2))
                with updated_data_placeholder:

                    key_metrics_price4('New Competitor Price',round(com_price,2))
                with updated_data_placeholder2:

                    key_metrics_price4('Competitor Price Change %',round(((com_price/round(df_input['Competitor Price'].mean(),2))-1)*100,2))
            cb1,cb2 = st.columns([.7,0.7])
            with cb2:
                with stylable_container(
                        key="green_button_s2",
                        css_styles="""
                            button {
                                background-color: #D81F1A;
                                color: white;
                                border-radius: 5px;
                            }
                            """,
                    ):
                    button = st.button("Submit")
    df_input['New Price']= np.where(price==0,df_input['Price'],price)
    df_input['New Competitor Price']= np.where(com_price==0,df_input['Competitor Price'],com_price)
    df_input['New Distribution'] = np.where(wd==0,df_input['Distribution'],wd)
    df_input['New Distribution Change%'] = ((df_input['New Distribution']/df_input['Distribution'])-1)*100
    df_input['New Distribution Change%'] =df_input['New Distribution Change%'].fillna(0)
    df_input['Intercept']= np.where(df_input['Intercept']<0,-1*df_input['Intercept'],df_input['Intercept'])
    df_input['re_Intercept']= np.where(df_input['re_Intercept']<0,-1*df_input['re_Intercept'],df_input['re_Intercept'])


    if button:
        st.session_state["button1"] = True
        df_input['Change%']= ((df_input['New Price']/df_input['Price'])-1)*100
        df_input['Competitor Price Change%']= ((df_input['New Competitor Price']/df_input['Competitor Price'])-1)*100

        df_input['New Volume'] = df_input['Volume']*(1+(((df_input['Change%']/100)*df_input['Elasticity'])+
                                                     ((df_input['Competitor Price Change%']/100)*df_input['Competitor Price Elasticity'])+
                                                     ((df_input['New Distribution Change%']/100)*df_input['Distribution Elasticity'])))
        df_input["Volume Impact(%)"] = ((df_input["New Volume"]/ df_input["Volume"])-1)*100
        df_input['Old Revenue'] = df_input['Volume']*df_input['Price']
        df_input['New Revenue'] = df_input['New Volume']*df_input['New Price']
        df_input["Revenue Impact(%)"] = ((df_input["New Revenue"]/ df_input["Old Revenue"])-1)*100
        df_input ['Incremental Revenue'] = df_input['New Volume']*df_input['New Price'] -  df_input['Volume']*df_input['Price']

        old_price = round(df_input["Price"].mean(),2)
        new_price = round(df_input["New Price"].mean(),2)
        old_volume = round(df_input["Volume"].sum(),2)
        new_volume = round(df_input["New Volume"].sum(),2)
        volume_impact = round(df_input["Volume Impact(%)"].mean(),2)
        old_rev = round(df_input["Old Revenue"].sum(),2)
        new_rev = round(df_input["New Revenue"].sum(),2)
        rev_impact = round(df_input["Revenue Impact(%)"].mean(),2)
        inc_rev = round(df_input["Incremental Revenue"].sum(),2)


        with st.container(height =350, border=False):
            c1, c2, c3,c4,c5,c6 = st.columns([1,1,1,1,1,1])
            with c4:
                key_metrics_price(
                "Current Revennue",
                convert_to_abbreviated(old_rev),
                'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png')
            with c5:
                key_metrics_price(
                "New Revenue",
                convert_to_abbreviated(new_rev),
                'https://i.im.ge/2024/03/26/WFhV3f.New-Price.png'
                )
            with c6:
                key_metrics_price(
                "Revenue Change(%)",
                str(round(rev_impact,2))+'%',
                'https://i.im.ge/2024/03/26/WFhf4m.Incremental-Revenue.png'
                )
            with c1:
                key_metrics_price(
                "Current Volume",
                convert_to_abbreviated(old_volume),
                'https://i.im.ge/2024/03/26/WFhzsr.Old-Volume.png')
            with c3:
                key_metrics_price(
                "Volume Change(%)",
                str(round(volume_impact,2))+'%',
                'https://i.im.ge/2024/03/26/WFhpz0.Volume-Change.png')
            with c2:
                key_metrics_price(
                "New Volume",
                convert_to_abbreviated(new_volume),
                'https://i.im.ge/2024/03/26/WFhzsr.Old-Volume.png')
            edited_df=df_input[['Manufacturer','Brand', 'Retailer', 'PPG','Year','Elasticity','Price',
                            'New Price','Change%','Distribution','New Distribution','New Distribution Change%','Competitor Price Elasticity',
                            'Competitor Price','New Competitor Price','Competitor Price Change%','Volume','New Volume','Volume Impact(%)','Incremental Revenue','Old Revenue','New Revenue']]

            st.write(' ')
            
                
            col1,col2 = st.columns([1,1])

            with col1:
                st.write(" ")
                df2_pl1 = edited_df.groupby(['Year'])['Volume'].sum().reset_index()
                df2_pl2 = edited_df.groupby(['Year'])['New Volume'].sum().reset_index()

                # Create horizontal bar traces
                trace52 = go.Bar(
                    y=['New Volume'],
                    x=df2_pl2['New Volume'],
                    name='New Volume',
                    orientation='h',
                    text=convert_to_abbreviated(round(df2_pl2['New Volume'][0], 0)),
                    textfont=dict(size=14, color='white', family='Graphik'),
                    marker=dict(color='#1E3D7D')
                )
                trace5 = go.Bar(
                    y=['Current Volume'],
                    x=df2_pl1['Volume'],
                    name='Current Volume',
                    orientation='h',
                    text=convert_to_abbreviated(round(df2_pl1['Volume'][0], 0)),
                    textfont=dict(size=14, color='white', family='Graphik'),
                    marker=dict(color='#06C480')
                )

                

                # Create the figure
                fig = make_subplots(specs=[[{"secondary_y": False}]])
                fig.add_trace(trace52)
                fig.add_trace(trace5)

                # Update layout
                fig.update_layout(
                    title_text="Change in Volume",
                    plot_bgcolor='white',
                    paper_bgcolor="white",
                    bargap=0.5,
                    height=400,
                    title_font=dict(size=24, family="Graphik", color='#555867'),
                    bargroupgap=0.6,yaxis=dict(tickmode='array',
                        tickvals=list(range(len(['Current Volume','New Volume']))),
                        # ticktext=df_vol_rev['date'],
                        # tickfont=dict(size=10),
                        tickangle=0,
                        automargin=True,
                        ticktext=[text[:-7] + '<br>' + text[-7:] if len(text) > 3 else text for text in ['Current Volume','New Volume']])
        
                )
                fig.update_xaxes(
                    title_text="Volume",
                    showgrid=False,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    mirror=False,
                    title_font=dict(size=16, family='Graphik', color='black'),
                    tickfont=dict(size=14, family='Graphik', color='black')
                )
                fig.update_yaxes(
                    title_text="2024",
                    showgrid=False,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    mirror=False,
                    title_font=dict(size=16, family='Graphik', color='black'),
                    tickfont=dict(size=14, family='Graphik', color='black')
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig, theme=None, use_container_width=True)

            with col2:
                st.write(" ")
                
                df2_pl1 = edited_df.groupby(['Year'])['Old Revenue'].sum().reset_index()
                df2_pl2 = edited_df.groupby(['Year'])['New Revenue'].sum().reset_index()

                # Create horizontal bar traces
                trace5 = go.Bar(
                    y=['Current Revenue'],
                    x=df2_pl1['Old Revenue'],
                    name='Current Revenue',
                    orientation='h',
                    text=convert_to_abbreviated(round(df2_pl1['Old Revenue'][0], 0)),
                    textfont=dict(size=14, color='white', family='Graphik'),
                    marker=dict(color='#06C480')
                )

                trace52 = go.Bar(
                    y=['New Revenue'],
                    x=df2_pl2['New Revenue'],
                    name='New Revenue',
                    orientation='h',
                    text=convert_to_abbreviated(round(df2_pl2['New Revenue'][0], 0)),
                    textfont=dict(size=14, color='white', family='Graphik'),
                    marker=dict(color='#1E3D7D')
                )

                # Create the figure
                fig = make_subplots(specs=[[{"secondary_y": False}]])
                fig.add_trace(trace52)
                fig.add_trace(trace5)

                # Update layout
                fig.update_layout(
                    title_text="Change in Revenue",
                    plot_bgcolor='white',
                    paper_bgcolor="white",
                    bargap=0.5,
                    height=400,
                    title_font=dict(size=24, family="Graphik", color='#555867'),
                    bargroupgap=0.6,yaxis=dict(tickmode='array',
                        tickvals=list(range(len(['Current Volume','New Volume']))),
                        # ticktext=df_vol_rev['date'],
                        # tickfont=dict(size=10),
                        tickangle=0,
                        automargin=True,
                        ticktext=[text[:-8] + '<br>' + text[-8:] if len(text) > 3 else text for text in ['Current Revenue','New Revenue']])
        
                )
                fig.update_xaxes(
                    title_text="Revenue",
                    showgrid=False,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    mirror=False,
                    title_font=dict(size=16, family='Graphik', color='black'),
                    tickfont=dict(size=14, family='Graphik', color='black')
                )
                fig.update_yaxes(
                    title_text="2024",
                    showgrid=False,
                    showline=True,
                    linewidth=1,
                    linecolor='black',
                    mirror=False,
                    title_font=dict(size=16, family='Graphik', color='black'),
                    tickfont=dict(size=14, family='Graphik', color='black')
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig, theme=None, use_container_width=True)
            with stylable_container(
            key="container_with_border11",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: white;
                }
                """,
            ):

                    def format_number(x):
                        if isinstance(x, (int, float)):
                            return '{:.2f}'.format(x)  # Format numbers to two decimal places
                        return str(x)
                    edited_df['Old Revenue'] = edited_df['Old Revenue'].astype(int).map('{:,}'.format)
                    edited_df['New Revenue'] = edited_df['New Revenue'].astype(int).map('{:,}'.format)
                    edited_df['Volume'] = edited_df['Volume'].astype(int).map('{:,}'.format)
                    edited_df['New Volume'] =edited_df['New Volume'].astype(int).map('{:,}'.format)
                    html_table = edited_df.to_html(index=False, classes=["dataframe"], escape=True,float_format=format_number)
                            

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
                            font-size: 18px;
                            # font-weight: ;
                            margin-bottom: 30px;
                            margin-top: 30px;
                            font-family: Graphik;
                            color: #555867;
                            text-align: center;

                        }
                    .table-container {
                        height: 400px; /* Set the fixed height for the container */
                        overflow-y: scroll; /* Add scrollbar when content overflows */
                    }
                    
                    </style>
                    """

                        # Combine HTML table and custom CSS

                        # Combine HTML table, title, and custom CSS
                    html_with_css = f"{custom_css}\n<div class='title'>Drill Through</div>\n<div class='table-container'>{html_table}</div>"
                    sp1, sp2 = st.columns([9, 1])

                    with sp2:
                        with stylable_container(
                                key="green_button_s1",
                                css_styles="""
                                    button {
                                        background-color: #D81F1A;
                                        color: white;
                                        border-radius: 5px;
                                    }
                                    """,
                            ):
                            st.download_button(
                                label="Download as CSV",
                                data=edited_df.to_csv(index=False),
                                file_name="Pricing Simulation.csv",
                                mime="text/csv",
                                key="download_button6"  # Ensure unique key for reactivity
                            )

                    

                    # Display HTML table with DataTable and custom styling
                    st.components.v1.html(html_with_css,height=6000)
