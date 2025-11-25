import streamlit as st
import itables
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
import streamlit.components.v1 as components
from utlis import key_metrics_price


# st.image('sigmoid_logo.png')
def market_summary():

    def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
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
                        "font": {"size": 15},
                    },
                )
            )
         
            fig.update_xaxes(visible=False, showgrid=False)
            fig.update_yaxes(visible=False, showgrid=False)
            fig.update_layout(
                paper_bgcolor="#F2F2F2",
                margin=dict(t=30, b=0),
                showlegend=False,
                plot_bgcolor="white",
                height=90,
            )

            st.plotly_chart(fig, use_container_width=True,theme = None)
    df_final = pd.read_csv('final_pricing_consolidated_file.csv')
    df = df_final.copy()
    df['retailer_id']=np.where(df['retailer_id']=='Target PT','Target',df['retailer_id'])
    df['retailer_id']=np.where(df['retailer_id']=='Publix TOTAL TA','Publix',df['retailer_id'])
    df['retailer_id']=np.where(df['retailer_id']=='CVS TOTAL Corp ex HI TA','CVS',df['retailer_id'])
    
    df=df.dropna()
    df['retailer_id'] = df['retailer_id'].apply(lambda x: x.upper())
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
    with stylable_container(
        key="container_with_border16",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-color: white;
            }
            """,
    ):
        f0,f1,f2,f3 = st.columns([1,1,1,1])
   
        with f0:
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5547)

        with f1:
            m1 = st.multiselect("Manufacturer",['All']+ df['manufacturer_nm'].unique().tolist())
            if "All" in m1:
                m1 = df['manufacturer_nm'].unique().tolist()
        if len(m1)==0:
            df_fil = df  
        else:          
            df_fil = df[df['manufacturer_nm'].isin(m1)]
        with f2:
            m3 = st.multiselect("Retailer",['All']+df_fil['retailer_id'].unique().tolist())
            if "All" in m3:
                m3 = df_fil['retailer_id'].unique().tolist()
        if len(m3)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['retailer_id'].isin(m3)]
        with f3:
            m5 = st.multiselect("Time Period",['All',]+df_fil['year'].unique().tolist()+['2022 H1','2022 H2','2023 H1','2023 H2',
                                                                                         '2022 Q1','2022 Q2','2022 Q3','2022 Q4',
                                                                                         '2023 Q1','2023 Q2','2023 Q3','2023 Q4',])
            if "All" in m5:
                m5 = df_fil['year'].unique().tolist()
        if len(m5)==0:
            df_fil = df_fil  
        else:
            old_df= df_fil.copy()
            df_fil = pd.DataFrame()
            for i in m5:
                if i=='2022':
                    temp = old_df[old_df['year']==i]
                    temp['time_period']=i
                if i=='2023':
                    temp = old_df[old_df['year']==i]
                    temp['time_period']=i
                if i=='2022 H1':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3,4,5,6]))]
                    temp['time_period']=i
                if i=='2022 H2':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9,10,11,12]))]
                    temp['time_period']=i
                if i=='2023 H1':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3,4,5,6]))]
                    temp['time_period']=i
                if i=='2023 H2':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9,10,11,12]))]
                    temp['time_period']=i
                if i=='2022 Q1':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3]))]
                    temp['time_period']=i
                if i=='2022 Q2':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([4,5,6]))]
                    temp['time_period']=i
                if i=='2022 Q3':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9]))]
                    temp['time_period']=i
                if i=='2022 Q4':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([10,11,12]))]
                    temp['time_period']=i
                if i=='2023 Q1':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3]))]
                    temp['time_period']=i
                if i=='2023 Q2':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([4,5,6]))]
                    temp['time_period']=i
                if i=='2023 Q3':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9]))]
                    temp['time_period']=i
                if i=='2023 Q4':
                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([10,11,12]))]
                    temp['time_period']=i
                df_fil = pd.concat([df_fil,temp],axis=0)


    df_filtered = df_fil.copy()
    manufacturers_count = df_filtered["manufacturer_nm"].nunique()
    brands_count = df_filtered["brand_nm"].nunique()
    retailers_count = df_filtered["retailer_id"].nunique()
    ppgs_count = df_filtered["ppg_nm"].nunique()
    

    # Using HTML div for container with specified class for styling
    st.markdown('<div class="st-emotion-cache-ocqkz7 e1f1d6gn5">', unsafe_allow_html=True)
    c1, c2, c3,c4,c5 = st.columns([1,1,1,1,1])
    with c5:
        st.write('Assessment Period')
        # st.write(df_filtered)
        min_year = df_filtered["year"].min()
        month_min = df_filtered["month"].min()
        a=df_filtered[df_filtered["month"]==month_min]
        max_year = df_filtered["year"].max()
        month_max = df_filtered["month"].max()
        b=df_filtered[df_filtered["month"]==month_max]
        date_range = f'{a["month_name"].iloc[0]} {min_year} - {b["month_name"].iloc[0]} {max_year}'

        # Construct the HTML string with the dynamic variable
        html_string = f"""
                    <style>
                    .big-font {{
                    
                        font-size:25px !important;
                        font-family: Graphik;
                        font-weight: bold;
                    }}
                    </style>
                    <p class='big-font'>{date_range}</p>
                    """


        st.markdown(html_string, unsafe_allow_html=True)

    with c1:
 
        key_metrics_price(
                    "Manufacturer Count",
                    manufacturers_count,
                    'https://i.im.ge/2024/03/28/Ws82sc.Manufacturer-Icon.png'
                )
        
    with c2:
        key_metrics_price(
                    "Brand Count",
                    brands_count,
                    'https://i.im.ge/2024/03/26/WFFOR6.Brand-Icon.png'
                        
                    )

    with c3:
        key_metrics_price(
                    "Retailer Count",
                    retailers_count,
                    'https://i.im.ge/2024/03/26/WFFSLK.Retailer-Icon.png'
                )
     
    with c4:
        key_metrics_price(
                    "PPG Count",
                    ppgs_count,
                    'https://i.im.ge/2024/03/26/WFFd39.PPG-Icon.png'
                  
                )
         
    

    st.write(' ')
    with st.container(height =480, border=False):
            col1,col2,col3 = st.columns([1,1,1])
            col4,col5,col6 = st.columns([1,1,1])

            df_filtered['manufacturer_nm']= df_filtered['manufacturer_nm']

            with col1:
                        
                        if len(m3)==0:
                            df_fair_share = df.copy()  
                        else:
                            df_fair_share = df[df['retailer_id'].isin(m3)]
                        if len(m5)==0:
                                df_fair_share = df_fair_share
                                df_fair_share_original = df.copy()
                        else:
                            old_df= df_fair_share.copy()
                            actual_fsh = df.copy()
                            df_fair_share = pd.DataFrame()
                            df_fair_share_original = pd.DataFrame()
                            for i in m5:
                                if i=='2022':
                                    temp = old_df[old_df['year']==i]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[actual_fsh['year']==i]
                                    temp2['time_period']=i
                                if i=='2023':
                                    temp = old_df[old_df['year']==i]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[actual_fsh['year']==i]
                                    temp2['time_period']=i
                                if i=='2022 H1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3,4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3,4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2022 H2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9,10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9,10,11,12]))]
                                    temp2['time_period']=i
                                if i=='2023 H1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3,4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3,4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2023 H2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9,10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9,10,11,12]))]
                                    temp2['time_period']=i
                                if i=='2022 Q1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3]))]
                                    temp2['time_period']=i
                                if i=='2022 Q2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2022 Q3':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9]))]
                                    temp2['time_period']=i
                                if i=='2022 Q4':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([10,11,12]))]
                                    temp2['time_period']=i
                                if i=='2023 Q1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3]))]
                                    temp2['time_period']=i
                                if i=='2023 Q2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2023 Q3':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9]))]
                                    temp2['time_period']=i
                                if i=='2023 Q4':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([10,11,12]))]
                                    temp2['time_period']=i
                                df_fair_share = pd.concat([df_fair_share,temp],axis=0)
                                df_fair_share_original = pd.concat([df_fair_share_original,temp2],axis=0)
                        final_df=pd.DataFrame()

                        for i in df_fair_share['manufacturer_nm'].unique():
                            temp= df_fair_share[df_fair_share['manufacturer_nm']==i]
                            temp['rev_share_manufacturer']= sum(temp['revenue'])/sum(df_fair_share['revenue'])*100
                            temp['rev_share_retailer']= temp['revenue']/sum(temp['revenue'])*100
                            temp['rev_share_retailer_overall']= temp['rev_share_retailer']*temp['rev_share_retailer']
                            final_df=pd.concat([final_df,temp],axis=0)
                        final_df2=pd.DataFrame()

                        for i in df_fair_share_original['manufacturer_nm'].unique():
                            temp= df_fair_share_original[df_fair_share_original['manufacturer_nm']==i]
                            temp['rev_share_manufacturer']= sum(temp['revenue'])/sum(df_fair_share_original['revenue'])*100
                            temp['rev_share_retailer']= temp['revenue']/sum(temp['revenue'])*100
                            temp['rev_share_retailer_overall']= temp['rev_share_retailer']*temp['rev_share_retailer']
                            final_df2=pd.concat([final_df2,temp],axis=0)
                        if len(m1)==0:

                            final_df=final_df
                        else:

                            final_df=final_df[final_df['manufacturer_nm'].isin(m1)]

                        final_df2 = final_df2[['manufacturer_nm','rev_share_manufacturer']].drop_duplicates()
                        final_df2.columns = ['manufacturer_nm','rev_share_manufacturer_fair_share']
                        final_df=pd.merge(final_df,final_df2,on=['manufacturer_nm'], how='left')
     
                        df_mod = final_df.groupby(['manufacturer_nm'])[['rev_share_manufacturer','rev_share_manufacturer_fair_share']].mean().reset_index()
                        df_mod['revenue_share']=df_mod['rev_share_manufacturer']
                        df_mod['revenue_share']=df_mod['revenue_share'].round(2)
                        df_mod['revenue_share_label']=(df_mod['revenue_share'].round(2)).astype(str)+'%'
                        df_mod = df_mod.sort_values(by='revenue_share',)


                        fig = go.Figure(data=[
                             go.Bar(name='Fair Share', x=df_mod['rev_share_manufacturer_fair_share'], y=df_mod['manufacturer_nm'],
                                        orientation='h', marker=dict(color='green'),text=df_mod['rev_share_manufacturer_fair_share'].round(2).astype(str)+'%',textfont=dict(
                                            size=24,
                                            color='white',  # Text color
                                            family='Graphik'  # Font 
                                        )),
                                go.Bar(name='Revenue Share', x=df_mod['revenue_share'], y=df_mod['manufacturer_nm'],
                                        orientation='h', marker=dict(color='#1E3D7D'),text=df_mod['revenue_share'].round(2).astype(str)+'%',textfont=dict(
                                            size=24,
                                            color='white',  # Text color
                                            family='Graphik' # Font
                                        ))
                            ])
                        fig.update_layout(title='Manufacturer Revenue Share',
                                        title_font=dict(size=24, family="Graphik",color='#555867'),
                                        legend=dict(orientation='h',yanchor="top", y=-0.1, xanchor="left", x=0),bargroupgap=0.1)
                        fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
    tickfont=dict(size=14, family='Graphik', color='black'))
                        fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
    tickfont=dict(size=14, family='Graphik', color='black'))
                
                        
                        
                        x=df_mod['revenue_share'].tolist()
                        y=df_mod['manufacturer_nm'].tolist()
                        max_x = max(x)
                        max_y_index = x.index(max_x)
                        max_y = y[max_y_index] 
                        
                        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',legend = dict(bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),paper_bgcolor="white", 
                                        plot_bgcolor="white",bargap=0.2,margin=dict(t=60, l=165, r=15, b=10)
                                        )

                        fig.update_layout(yaxis=dict(
                        title_standoff=25) )
                        fig.update_xaxes(showgrid=False)
        
                        st.plotly_chart(fig, theme=None,use_container_width=True)

            with col2:

                        if len(m5)==0:
                            df_filtered['revenue'] = df_filtered['revenue'] / 1e6
                            df_mod = (df_filtered.groupby(['manufacturer_nm','year'])['revenue'].sum().reset_index().round(2))
                            df_mod=df_mod.sort_values(['year','revenue'])

                           
                            color_map={}
                            for i in df_mod.head(5).sort_values(['year','revenue'],ascending= True)['manufacturer_nm'].tolist():
                                if i=='RECKITT':
                                    color_map[i]='#1E3D7D'
                                if i=='COLGATE PALMOLIVE':
                                    color_map[i]='#4E5960'
                                if i=='P&G':
                                    color_map[i]='#FF7A00'
                                if i=='PRIVATE LABEL':
                                    color_map[i]='#0996CE'
                                if i=='CLOROX COMPANY':
                                    color_map[i]='#D91E18'

                            fig = px.bar(df_mod, x='year', y='revenue', color="manufacturer_nm",color_discrete_map=color_map, 
                                        title="Manufacturer Wise Revenue",labels={'year': 'Year', 'revenue': 'Revenue','manufacturer_nm':'Manufacturer'})
                            
                            fig.update_traces(textposition= 'inside')
                            fig.update_xaxes(title_text="Year",showgrid=False,tickvals=df_mod["year"].tolist())
                            fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6)
                            fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                            fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))


                            fig.update_yaxes(
                                title_text="Revenue", 
                                secondary_y=False,showgrid=False,ticksuffix="M")
                            fig.update_layout(yaxis_tickformat='$.2fM')
                            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',legend = dict(bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),paper_bgcolor="white",plot_bgcolor="white",height=450,yaxis=dict(
                            title_standoff=25),margin=dict(t=60, l=80, r=10, b=70)
                                                        )
                            st.plotly_chart(fig, theme=None,use_container_width=True)
                        else:
                            df_filtered['revenue'] = df_filtered['revenue'] / 1e6
                            df_mod = (df_filtered.groupby(['manufacturer_nm','time_period'])['revenue'].sum().reset_index().round(2))
                            df_mod=df_mod.sort_values(['time_period','revenue'])


                            color_map={}
                            for i in df_mod.head(5).sort_values(['time_period','revenue'],ascending= True)['manufacturer_nm'].tolist():
                                if i=='RECKITT':
                                    color_map[i]='#1E3D7D'
                                if i=='COLGATE PALMOLIVE':
                                    color_map[i]='#4E5960'
                                if i=='P&G':
                                    color_map[i]='#FF7A00'
                                if i=='PRIVATE LABEL':
                                    color_map[i]='#0996CE'
                                if i=='CLOROX COMPANY':
                                    color_map[i]='#D91E18'

                            fig = px.bar(df_mod, x='time_period', y='revenue', color="manufacturer_nm",color_discrete_map=color_map,
                                        title="Manufacturer Wise Revenue",labels={'time_period': 'Time Period', 'revenue': 'Revenue','manufacturer_nm':'Manufacturer'})
                            fig.update_traces(textposition= 'inside')
                            fig.update_xaxes(title_text="Time Period",showgrid=False,tickvals=df_mod["time_period"].tolist())

                            fig.update_yaxes(
                                title_text="Revenue", 
                                secondary_y=False,showgrid=False,ticksuffix="M")
                            fig.update_layout(yaxis_tickformat='$.2fM',title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6)
                            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',legend = dict(bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),paper_bgcolor="white",plot_bgcolor="white",height=450,yaxis=dict(
                            title_standoff=25),margin=dict(t=60, l=80, r=10, b=70)
                                                        )
                            fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                            fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))

                            st.plotly_chart(fig, theme=None,use_container_width=True)
                            
            with col3:
                 with stylable_container(
            key="container_with_border17",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: white;
                }
                """,
        ):

                        st.write(" ")
                        if len(m5)==0:
                            df_mod = (df_filtered.groupby(['manufacturer_nm','year'])['revenue'].sum().reset_index().round(2))
                            df_mod=df_mod.sort_values(['year','revenue'])

                            print_df = pd.pivot_table(df_mod,index=['manufacturer_nm'], columns=['year'],values=['revenue'],margins=True, margins_name='TOTAL').reset_index()

                            print_df.columns = ['Manufacturer']+df_mod['year'].unique().tolist()+['TOTAL']
                            print_df=print_df.drop(['TOTAL'],axis=1)
                            time_pr_list= df_mod['year'].unique().tolist()
                            print_df[time_pr_list] = print_df[time_pr_list].round(2)

                            

                            for i in range(0,len(time_pr_list)-1):
                                print_df['%Change'+' '+time_pr_list[i+1]]=round(((print_df[time_pr_list[i+1]]/print_df[time_pr_list[i]])-1)*100,2).astype(str)+'%'
                            print_df=print_df.sort_values(time_pr_list,ascending=False)
                            print_df[time_pr_list] = print_df[time_pr_list].astype(str)+'M'
                            total_row = print_df[print_df['Manufacturer']=='TOTAL']
                            print_df = print_df[print_df['Manufacturer']!='TOTAL']
                            print_df=print_df.sort_values(time_pr_list,ascending=False)
                            print_df=pd.concat([print_df,total_row],axis=0)
                            html_table = print_df.to_html(index=False, classes=["dataframe"], escape=True)

                        

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
                                height: 400px; /* Set the fixed height for the container */
                                # overflow-y: auto; /* Add scrollbar when content overflows */
                            }
                            
                            </style>
                            """

                                # Combine HTML table and custom CSS

                                # Combine HTML table, title, and custom CSS
                            html_with_css = f"{custom_css}\n<div class='title'>Manufacturer Revenue Comparison</div>\n<div class='table-container'>{html_table}</div>"

                            

                            # Display HTML table with DataTable and custom styling
                            st.components.v1.html(html_with_css, height=400)
                        else:
                            df_mod = (df_filtered.groupby(['manufacturer_nm','time_period'])['revenue'].sum().reset_index().round(2))
                            df_mod=df_mod.sort_values(['time_period','revenue'])

                            print_df = pd.pivot_table(df_mod,index=['manufacturer_nm'], columns=['time_period'],values=['revenue'],margins=True, margins_name='TOTAL').reset_index()

                            print_df.columns = ['Manufacturer']+df_mod['time_period'].unique().tolist()+['TOTAL']
                            print_df=print_df.drop(['TOTAL'],axis=1)
                            time_pr_list= df_mod['time_period'].unique().tolist()
                            print_df[time_pr_list] = print_df[time_pr_list].round(2)

                            

                            for i in range(0,len(time_pr_list)-1):
                                print_df['%Change'+' '+time_pr_list[i+1]]=round(((print_df[time_pr_list[i+1]]/print_df[time_pr_list[i]])-1)*100,2).astype(str)+'%'

                            print_df=print_df.sort_values(time_pr_list,ascending=False)
                            print_df[time_pr_list] = print_df[time_pr_list].astype(str)+'M'
                            total_row = print_df[print_df['Manufacturer']=='TOTAL']
                            print_df = print_df[print_df['Manufacturer']!='TOTAL']
                            
                            print_df=pd.concat([print_df,total_row],axis=0)
                            html_table = print_df.to_html(index=False, classes=["dataframe"], escape=True)

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
                                    background-color: #F2F2F2; /* Blue */
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
                                height: 400px; /* Set the fixed height for the container */
                                overflow-y: auto; /* Add scrollbar when content overflows */
                            }
                            </style>
                            """

                                # Combine HTML table and custom CSS
                            table_title = "<div class='title'>Manufacturer Revenue Comparison</div>"

                                # Combine HTML table, title, and custom CSS
                            html_with_css = f"{custom_css}\n<div class='title'>Manufacturer Revenue Comparison</div>\n<div class='table-container'>{html_table}</div>"

                            

                            # Display HTML table with DataTable and custom styling
                            st.components.v1.html(html_with_css, height=400)
                            
            with col4:
                        

                        if len(m1)==0:
                            df_fair_share = df.copy()  
                        else:
                            df_fair_share = df[df['manufacturer_nm'].isin(m1)]
                        if len(m5)==0:
                                df_fair_share = df_fair_share
                                df_fair_share_original = df.copy()
                        else:
                            old_df= df_fair_share.copy()
                            actual_fsh = df.copy()
                            df_fair_share = pd.DataFrame()
                            df_fair_share_original = pd.DataFrame()
                            for i in m5:
                                if i=='2022':
                                    temp = old_df[old_df['year']==i]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[actual_fsh['year']==i]
                                    temp2['time_period']=i
                                if i=='2023':
                                    temp = old_df[old_df['year']==i]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[actual_fsh['year']==i]
                                    temp2['time_period']=i
                                if i=='2022 H1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3,4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3,4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2022 H2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9,10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9,10,11,12]))]
                                    temp2['time_period']=i
                                if i=='2023 H1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3,4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3,4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2023 H2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9,10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9,10,11,12]))]
                                    temp2['time_period']=i
                                if i=='2022 Q1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3]))]
                                    temp2['time_period']=i
                                if i=='2022 Q2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2022 Q3':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9]))]
                                    temp2['time_period']=i
                                if i=='2022 Q4':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([10,11,12]))]
                                    temp2['time_period']=i
                                if i=='2023 Q1':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([1,2,3]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([1,2,3]))]
                                    temp2['time_period']=i
                                if i=='2023 Q2':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([4,5,6]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([4,5,6]))]
                                    temp2['time_period']=i
                                if i=='2023 Q3':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([7,8,9]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([7,8,9]))]
                                    temp2['time_period']=i
                                if i=='2023 Q4':
                                    temp = old_df[(old_df['year']==i.split(' ')[0])&(old_df['month'].isin([10,11,12]))]
                                    temp['time_period']=i
                                    temp2 = actual_fsh[(actual_fsh['year']==i.split(' ')[0])&(actual_fsh['month'].isin([10,11,12]))]
                                    temp2['time_period']=i
                                df_fair_share = pd.concat([df_fair_share,temp],axis=0)
                                df_fair_share_original = pd.concat([df_fair_share_original,temp2],axis=0)
                        final_df=pd.DataFrame()

                        for i in df_fair_share['retailer_id'].unique():
                            temp= df_fair_share[df_fair_share['retailer_id']==i]
                            temp['rev_share_retailer']= (sum(temp['revenue'])/sum(df_fair_share['revenue']))*100
                            
                            final_df=pd.concat([final_df,temp],axis=0)
                        final_df2=pd.DataFrame()

                        for i in df_fair_share_original['retailer_id'].unique():
                            temp= df_fair_share_original[df_fair_share_original['retailer_id']==i]
                            temp['rev_share_retailer']= (sum(temp['revenue'])/sum(df_fair_share_original['revenue']))*100
                            
                            final_df2=pd.concat([final_df2,temp],axis=0)
                        if len(m3)==0:

                            final_df=final_df
                        else:

                            final_df=final_df[final_df['retailer_id'].isin(m3)]

                        final_df2 = final_df2[['retailer_id','rev_share_retailer']].drop_duplicates()
                        final_df2.columns = ['retailer_id','rev_share_retailer_fair_share']

                        final_df=pd.merge(final_df,final_df2,on=['retailer_id'], how='left')
                       


                        df_mod = final_df.groupby(['retailer_id'])[['rev_share_retailer','rev_share_retailer_fair_share']].mean().reset_index()
                        df_mod['revenue_share']=df_mod['rev_share_retailer']
                        df_mod['revenue_share']=df_mod['revenue_share'].round(2)
                        df_mod = df_mod.sort_values(by='revenue_share',ascending=False)
                        df_mod_5 = df_mod[df_mod['retailer_id'].isin(df_mod.head(4)['retailer_id'].unique().tolist())]
                        df_mod_other = df_mod[~(df_mod['retailer_id'].isin(df_mod.head(4)['retailer_id'].unique().tolist()))]

                        df_mod_other['rev_share_retailer']=df_mod_other['rev_share_retailer'].sum()
                        df_mod_other['rev_share_retailer_fair_share']=df_mod_other['rev_share_retailer_fair_share'].sum()
                        df_mod_other['revenue_share']=df_mod_other['revenue_share'].sum()
                        df_mod_other['retailer_id']='OTHERS'
                        df_mod_other=df_mod_other.drop_duplicates()
                        df_mod = pd.concat([df_mod_5,df_mod_other],axis=0)
                        df_mod=df_mod.sort_values('revenue_share')
                        df_mod['revenue_share_label']=df_mod['revenue_share'].round(2).astype(str)+'%'


                        fig = go.Figure(data=[
                             go.Bar(name='Fair Share', x=df_mod['rev_share_retailer_fair_share'], y=df_mod['retailer_id'],
                                        orientation='h', marker=dict(color='green'),text=df_mod['rev_share_retailer_fair_share'].round(2).astype(str)+'%',textfont=dict(
                                                size=24,
                                                color='white',  # Text color
                                                family='Graphik' # Font
                                            )),
                                go.Bar(name='Revenue Share', x=df_mod['revenue_share'], y=df_mod['retailer_id'],
                                        orientation='h', marker=dict(color='#1E3D7D'),text=df_mod['revenue_share'].round(2).astype(str)+'%',textfont=dict(
                                                size=24,
                                                color='white',  # Text color
                                                family='Graphik' # Font
                                            ))
                        
                            ])
                        fig.update_layout(title='Retailer Revenue Share',title_font=dict(size=24, family="Graphik",color='#555867'),
                                        legend=dict(orientation='h',yanchor="top", y=-0.1, xanchor="left", x=0),bargroupgap=0.1)
                        fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                        fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))




                        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',legend = dict(bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),paper_bgcolor="white", 
                                        plot_bgcolor="white",bargap=0.2,margin=dict(t=60, l=160, r=15, b=10)
                                                        )

                        fig.update_layout(yaxis=dict(
                        title_standoff=25) )
                        fig.update_xaxes(showgrid=False)
                       

                        st.plotly_chart(fig, theme=None,use_container_width=True)
                        
            with col5:

                        if len(m5)==0:
                            
                            df_mod = df_filtered.groupby(['retailer_id','year'])['revenue'].sum().reset_index()
                            df_mod = df_mod.sort_values(by=['revenue','year'],ascending=False)
                            df_mod_5 = df_mod[df_mod['retailer_id'].isin(df_mod.head(8)['retailer_id'].unique().tolist())]
                            df_mod_other = df_mod[~(df_mod['retailer_id'].isin(df_mod.head(8)['retailer_id'].unique().tolist()))]
                            df_mod_other=df_mod_other.groupby(['year'])['revenue'].sum().reset_index()
                            df_mod_other['retailer_id']='OTHERS'
                            df_mod_other=df_mod_other.drop_duplicates()
                            df_mod = pd.concat([df_mod_5,df_mod_other],axis=0)
                        
                            df_mod=df_mod.sort_values(['year','revenue'])
                            fig = px.bar(df_mod, x='year', y='revenue', color="retailer_id",
                                        title="Retailer Wise Revenue",labels={'year': 'Year', 'revenue': 'Revenue','retailer_id':'Retailers'},color_discrete_sequence=['#D91E18','#4E5960','#FF7A00','#0996CE','#1E3D7D'])

                            fig.update_xaxes(title_text="Year",showgrid=False,tickvals=df_mod["year"].tolist())
                            fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6)
                            fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                            fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))


                            fig.update_yaxes(
                                title_text="Revenue", 
                                secondary_y=False,showgrid=False,ticksuffix="M")
                            fig.update_layout()
                            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',legend = dict(bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),paper_bgcolor="white",plot_bgcolor="white",height=450,yaxis=dict(
                            title_standoff=25),margin=dict(t=60, l=80, r=180, b=70)
                                                        )
                            st.plotly_chart(fig, theme=None,use_container_width=True)
                        else:
                                df_mod = df_filtered.groupby(['retailer_id','time_period'])['revenue'].sum().reset_index()
                                df_mod = df_mod.sort_values(by=['revenue','time_period'],ascending=False)
                                df_mod_5 = df_mod[df_mod['retailer_id'].isin(df_mod.head(4*len(m5))['retailer_id'].unique().tolist())]
                                df_mod_other = df_mod[~(df_mod['retailer_id'].isin(df_mod.head(4*len(m5))['retailer_id'].unique().tolist()))]
                                df_mod_other=df_mod_other.groupby(['time_period'])['revenue'].sum().reset_index()
                                df_mod_other['retailer_id']='OTHERS'
                                df_mod_other=df_mod_other.drop_duplicates()
                                df_mod = pd.concat([df_mod_5,df_mod_other],axis=0)
                               
                                df_mod=df_mod.sort_values(['time_period','revenue'])
                               
                                fig = px.bar(df_mod, x='time_period', y='revenue', color="retailer_id",
                                            title="Retailer Wise Revenue",labels={'time_period': 'Time Period', 'revenue': 'Revenue','retailer_id':'Retailers'},color_discrete_sequence=['#4E5960','#FF7A00','#0996CE','#D91E18','#1E3D7D'])
                            
                                fig.update_xaxes(title_text="Time Period",showgrid=False,tickvals=df_mod["time_period"].tolist())
                                fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6)

                                fig.update_yaxes(
                                    title_text="Revenue", 
                                    secondary_y=False,showgrid=False,ticksuffix="M")
                                fig.update_layout()
                                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',legend = dict(bgcolor = 'white',font=dict(size=14, family='Graphik', color='black')),paper_bgcolor="white",plot_bgcolor="white",height=450,yaxis=dict(
                                title_standoff=25),margin=dict(t=60, l=80, r=180, b=70)
                                
                                                        )
                                fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                                fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))

                                st.plotly_chart(fig, theme=None,use_container_width=True)
                            

            with col6:
                 with stylable_container(
                    key="container_with_border18",
                    css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: calc(1em - 1px);
                            background-color: white;
                        }
                        """,
                ):
                        st.write(" ")
                        if len(m5)==0:
                            
                            df_mod = df_filtered.groupby(['retailer_id','year'])['revenue'].sum().reset_index()
                            df_mod = df_mod.sort_values(by='revenue',ascending=False)
                            df_mod_5 = df_mod[df_mod['retailer_id'].isin(df_mod.head(8)['retailer_id'].unique().tolist())]
                            df_mod_other = df_mod[~(df_mod['retailer_id'].isin(df_mod.head(8)['retailer_id'].unique().tolist()))]
                            df_mod_other=df_mod_other.groupby(['year'])['revenue'].sum().reset_index()
                            df_mod_other['retailer_id']='OTHERS'
                            df_mod_other=df_mod_other.drop_duplicates()
                            df_mod = pd.concat([df_mod_5,df_mod_other],axis=0)

                            df_mod=df_mod.sort_values(['year','revenue'])
                            print_df = pd.pivot_table(df_mod,index=['retailer_id'], columns=['year'],values=['revenue'],margins=True, margins_name='TOTAL').reset_index()

                            print_df.columns = ['Retailer']+df_mod['year'].unique().tolist()+['TOTAL']
                            print_df=print_df.drop(['TOTAL'],axis=1)
                            time_pr_list= df_mod['year'].unique().tolist()
                            print_df[time_pr_list] = print_df[time_pr_list].round(2)
                            # st.write(print_df)
                            

                            for i in range(0,len(time_pr_list)-1):
                                print_df['%Change'+' '+time_pr_list[i+1]]=round(((print_df[time_pr_list[i+1]]/print_df[time_pr_list[i]])-1)*100,2).astype(str)+'%'
                            # st.dataframe(print_df.set_index(print_df.columns[0]),100,200,use_container_width=True)
                            # st.components.v1.html(itables.to_html_datatable(print_df), height=400)
                            print_df=print_df.sort_values([time_pr_list[0]],ascending=False)
                            print_df[time_pr_list] = print_df[time_pr_list].astype(str)+'M'
                            total_row = print_df[print_df['Retailer']=='TOTAL']
                            print_df = print_df[print_df['Retailer']!='TOTAL']
                            
                            print_df=pd.concat([print_df,total_row],axis=0)
                            # st.write(print_df)
                            html_table = print_df.to_html(index=False, classes=["dataframe"], escape=True)

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
                                    background-color: #F2F2F2; /* Blue */
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
                                # height: 400px; /* Set the fixed height for the container */
                                overflow-y: auto; /* Add scrollbar when content overflows */
                            }
                            </style>
                            """

                            # Combine HTML table and custom CSS

                            # Combine HTML table, title, and custom CSS
                            html_with_css = f"{custom_css}\n<div class='title'>Retailer Revenue Comparison</div>\n<div class='table-container'>{html_table}</div>"

                            # Display HTML table with DataTable and custom styling
                            st.components.v1.html(html_with_css, height=400)
                                                                        

                        else:
                            df_mod = df_filtered.groupby(['retailer_id','time_period'])['revenue'].sum().reset_index()
                            df_mod = df_mod.sort_values(by='revenue',ascending=False)
                            df_mod_5 = df_mod[df_mod['retailer_id'].isin(df_mod.head(4*len(m5))['retailer_id'].unique().tolist())]
                            df_mod_other = df_mod[~(df_mod['retailer_id'].isin(df_mod.head(4*len(m5))['retailer_id'].unique().tolist()))]
                            df_mod_other=df_mod_other.groupby(['time_period'])['revenue'].sum().reset_index()
                            df_mod_other['retailer_id']='OTHERS'
                            df_mod_other=df_mod_other.drop_duplicates()
                            df_mod = pd.concat([df_mod_5,df_mod_other],axis=0)

                            df_mod=df_mod.sort_values(['time_period','revenue'])

                            print_df = pd.pivot_table(df_mod,index=['retailer_id'], columns=['time_period'],values=['revenue'],margins=True, margins_name='TOTAL').reset_index()

                            print_df.columns = ['Retailer']+df_mod['time_period'].unique().tolist()+['TOTAL']
                            print_df=print_df.drop(['TOTAL'],axis=1)
                            time_pr_list= df_mod['time_period'].unique().tolist()
                            print_df[time_pr_list] = print_df[time_pr_list].round(2)
                            

                            for i in range(0,len(time_pr_list)-1):
                                print_df['%Change'+' '+time_pr_list[i+1]]=round(((print_df[time_pr_list[i+1]]/print_df[time_pr_list[i]])-1)*100,2).astype(str)+'%'
                            print_df=print_df.sort_values(time_pr_list,ascending=False)
                            print_df[time_pr_list] = print_df[time_pr_list].astype(str)+'M'
                            total_row = print_df[print_df['Retailer']=='TOTAL']
                            print_df = print_df[print_df['Retailer']!='TOTAL']
                            
                            print_df=pd.concat([print_df,total_row],axis=0)
                            html_table = print_df.to_html(index=False, classes=["dataframe"], escape=True)

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
                                    background-color: #F2F2F2; /* Blue */
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
                                # height: 400px; /* Set the fixed height for the container */
                                overflow-y: auto; /* Add scrollbar when content overflows */
                            }
                            </style>
                            """

                            # Combine HTML table and custom CSS
                            # table_title = "<div class='title'>Retailer Revenue Comparison</div>"

                            # Combine HTML table, title, and custom CSS
                            html_with_css = f"{custom_css}\n<div class='title'>Retailer Revenue Comparison</div>\n<div class='table-container'>{html_table}</div>"

                            # Display HTML table with DataTable and custom styling
                            st.components.v1.html(html_with_css, height=400)
