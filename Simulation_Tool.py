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
from streamlit_calendar import calendar
import json

def simulation_tool():

    def plot_metrics(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
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




   
    df2 = pd.read_csv('simulation_data.csv')
    df2['segment']=df2['subsegment_name'].str.split('|').str[0]
    df2['month'] = pd.to_datetime(df2['start_date']).dt.month
    # df2['roi'] = np.where(df2['promo_investment'] != 0, 
    #             (df2['volume_lift_pct'] * df2['promo_price_unit']) / df2['promo_investment'], 0)*100
    df2['promo_tactic'] = np.where(df2['promo_tactic']=='unknown','Display & TPR', df2['promo_tactic'] )
    df2['promo_tactic'] = np.where(df2['promo_tactic']=='No Tactic','Feature & TPR', df2['promo_tactic'] )

    df2['promo_tactic'] = np.where(df2['promo_tactic']=='Feature & TPR','Feature', df2['promo_tactic'] )
    df2['promo_tactic'] = np.where(df2['promo_tactic']=='Display & TPR','Display', df2['promo_tactic'] )
    df2['promo_tactic'] = np.where(df2['promo_tactic']=='Feature Only','Feature', df2['promo_tactic'] )
    df2['promo_tactic'] = np.where(df2['promo_tactic']=='Display Only','Display', df2['promo_tactic'] )
    df2['promo_tactic'] = np.where(df2['promo_tactic']=='TPR Only','TPR', df2['promo_tactic'] )
    df2['ROI']= df2['roi']
    df2['offer_mechanic']= np.where(df2['offer_mechanic']=='unknown','special x off',df2['offer_mechanic'])
    bins = [0,10,20,30,40,50,60,70,80]
    labels = ['0%-10%','10%-20%','20%-30%','30%-40%','40%-50%','50%-60%','60%-70%','70%-80%']
    df2['promo_bins']=pd.cut(df2['discount'], bins=bins,labels=labels, right=False) 
    df2['offer_type']=np.where(df2['offer_type']=='unknown','spend_reward',df2['offer_type'])
    df2['offer_type']= df2['offer_type'].str.upper()
    df2['offer_type'] = df2['offer_type'].replace('_', ' ', regex=True)
    # df2['offer_type']=np.where(df2['offer_mechanic'].str.contains('save'),'Save Dollers',
    #                         np.where(df2['offer_mechanic'].str.contains('price'),'Quantity for Price','Discount vouchers'))
    df2['start_dates'] = pd.to_datetime(df2['start_date']) 
     # Calculate the number of days to subtract to go back to the last Sunday
    days_to_subtract = df2['start_dates'].dt.dayofweek + 1
    
    # Subtract the days to go back to the last Sunday
    df2['start_dates'] = df2['start_dates'] - pd.to_timedelta(days_to_subtract, unit='D')
    
    # Convert the adjusted start_dates back to string format
    df2['start_dates'] = df2['start_dates'].dt.strftime("%Y/%m/%d")

    df2['retailer']=np.where(df2['retailer']=='Target PT','Target',df2['retailer'])
    df2['retailer']=np.where(df2['retailer']=='Publix Total TA','Publix',df2['retailer'])
    df2['retailer']=np.where(df2['retailer']=='CVS Total Corp ex HI TA','CVS',df2['retailer'])
    df2['brand_nm']=df2['ppg_id'].str.split('|').str[2]
    df2['retailer'] = df2['retailer'].apply(lambda x: x.upper())

    with stylable_container(
        key="container_with_border12",
        css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background-color: white;
                }
                """,
                ):
        f0,f1,f2,f3,f4 = st.columns([1,1,1,1,1])
        with f0:
            m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5543)
        with f1:
            m4_check = st.multiselect("Brand",['All']+df2['brand_nm'].unique().tolist(),key=23 )
            if "All" in m4_check:
                m4 = df2['brnad_nm'].unique().tolist()
            else:
                m4= m4_check
        if len(m4)==0:
            df_fil = df2
        else:
            df_fil = df2[df2['brand_nm'].isin(m4)]
        with f2:
            m2_check = st.multiselect("Segment",['All']+df_fil['segment'].unique().tolist(),key=22 )
            if "All" in m2_check:
                m2 = df_fil['segment'].unique().tolist()
            else:
                m2= m2_check
        if len(m2)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['segment'].isin(m2)]
        with f3:
            m3_check = st.multiselect("PPG",['All']+df_fil['ppg_id'].unique().tolist(),key=33 )
            if "All" in m3_check:
                m3 = df_fil['ppg_id'].unique().tolist()
            else:
                m3= m3_check
        if len(m3)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['ppg_id'].isin(m3)]
        with f4:
            m1_check = st.multiselect("Retailer",['All']+ df_fil['retailer'].unique().tolist(),key=11)
            if "All" in m1_check:
                m1 = df_fil['retailer'].unique().tolist()
            else:
                m1= m1_check
        if len(m1)==0:
            df_fil = df_fil
        else:
            df_fil = df_fil[df_fil['retailer'].isin(m1)]
        c1,c2 = st.columns([0.1,1])

        with c1:
            number_promotions = st.number_input('No of Promo Events', step=1, min_value=1)


    
    df_filtered2 = df_fil.copy()

    


                

    with st.container(height =500, border=False):
        with stylable_container(
                key="container_with_border13",
                css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: calc(1em - 1px);
                            background-color: white;
                        }
                        """,
                        ):
            column1,column2 =st.columns([6,1])
            with column1:
                    input_values=[]
                    for i in range(number_promotions):

                    
                        c0,c1,c11,c2,c3,c4,c5=st.columns([1.3,1.3,1.3,1,1,0.7,0.8])
                        with c0:
                            k0 = st.multiselect("Promo Tactic",['All']+df_fil['promo_tactic'].unique().tolist(),key=2000+i )
                            df_fil2=df_fil[df_fil['promo_tactic'].isin(k0)]
                        with c1:
                            k1 = st.multiselect("Offer Type",['All']+df_fil2['offer_type'].unique().tolist(),key=1000+i )
                            df_fil2=df_fil2[df_fil2['offer_type'].isin(k1)]
                        with c11:
                            k11 = st.multiselect("Offer Mechanic",['All']+df_fil2['offer_mechanic'].unique().tolist(),key=3000+i )
                            df_fil2=df_fil2[df_fil2['offer_mechanic'].isin(k11)]
                        
                        with c2:
                            k2=st.date_input("Start Date",value=None, max_value=datetime.date(2024, 12, 31),min_value=datetime.date(2024, 3, 1),format="YYYY-MM-DD",key = 100+i)
                        with c3:
                            k3 = st.text_input("Promo Duration (Days)", "",key=(200)+i)
                        with c4:
                            k4 = st.text_input("Discount (%)", "",key=(300)+i)
                        with c5:
                            updated_data_placeholder1 = st.empty()

                            with updated_data_placeholder1:

                                change = st.slider('Redemption Rate (%)', 0, 100, 0,disabled=False, key =(400)+i)
                        input_values.append([k0,k1,k11,k2,k3,k4,change])
                    output=pd.DataFrame(input_values, columns=['Promo Tactic','Offer Type','Offer Mechanic','Date','PromoDays','Discount','Redemption'])
                    cb1,cb2 = st.columns([.9,0.09])
                    with cb2:
                        with stylable_container(
                                    key="green_button_st1",
                                    css_styles="""
                                        button {
                                            background-color: #D81F1A;
                                            color: white;
                                            border-radius: 5px;
                                        }
                                        """,
                                ):
                                button = st.button("Submit")

            with column2:
            
                event_list=[]
                event_filtered_data = pd.DataFrame()
                df_filtered=pd.DataFrame()
                for i in range(output.shape[0]):
                    if len(output.iloc[i]['Promo Tactic'])==0:
                        df_filtered=df_filtered2.copy()

                    else:
                        df_filtered = df_filtered2[df_filtered2['promo_tactic'].isin(output.iloc[i]['Promo Tactic'])]
                        
                    
                    if len(output.iloc[i]['Offer Type'])==0:
                        df_filtered=df_filtered.copy()

                    else:
                        df_filtered = df_filtered[df_filtered['offer_type'].isin(output.iloc[i]['Offer Type'])]
                    if len(output.iloc[i]['Offer Mechanic'])==0:
                        df_filtered=df_filtered.copy()

                    else:
                        df_filtered = df_filtered[df_filtered['offer_mechanic'].isin(output.iloc[i]['Offer Mechanic'])]
                        
                    if output.iloc[i]['Date']==None:
                        df_filtered=df_filtered.copy()
                    else:
                        df_filtered = df_filtered[pd.to_datetime(df_filtered['start_dates'])==pd.to_datetime(output.iloc[i]['Date'])]
                    if len(output.iloc[i]['PromoDays'])==0:
                        df_filtered=df_filtered.copy()
                    else:
                        df_filtered = df_filtered[df_filtered['promo_duration_days']==int(output.iloc[i]['PromoDays'])]
                    if len(output.iloc[i]['Discount'])==0:
                        df_filtered=df_filtered.copy()
                    else:
                        df_filtered = df_filtered[df_filtered['discount']==int(output.iloc[i]['Discount'])]
                    if output.iloc[i]['Redemption']==0:
                        df_filtered=df_filtered.copy()
                    else:
                        df_filtered['Redemption Rate']= output.iloc[i]['Redemption']/100

                    df_filtered['input_number']=i
                    if len(output.iloc[i]['Promo Tactic'])!=0:
                        event_filtered_data=pd.concat([event_filtered_data,df_filtered])
                        

                    ROI = int(df_filtered['incr_revenue'].sum())/int(df_filtered['promo_investment'].sum())+1

                    if (len(output.iloc[i]['Promo Tactic'])==0) or (len(output.iloc[i]['Offer Mechanic'])==0) or(len(output.iloc[i]['PromoDays'])==0) or (len(output.iloc[i]['Discount'])==0) or (output.iloc[i]['Redemption']==0) or (len(output.iloc[i]['Offer Type'])==0):

                        key_metrics_price3(
                                "ROI ",
                                str(round(0,2)),
                                'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png'
                                
                        
                        )
                    else:
                        key_metrics_price3(
                                "ROI ",
                                str(round(ROI,2)),
                                'https://i.im.ge/2024/03/26/WFhKU1.Old-Price.png'
                                
                        
                        )
                    st.write('  ')
                    st.write('  ')
                    # st.write('  ')
                    if len(output.iloc[i]['PromoDays'])==0:
                        event_list.append({'title':'Promo '+str(i+1),'color':'#FF6C6C',
                                        'start':str(output.iloc[i]['Date']),'end':str(output.iloc[i]['Date'])})
                    else:
                        event_list.append({'title':'Promo '+str(i+1),'color':'#FF6C6C',
                                        'start':str(output.iloc[i]['Date']),'end':(output.iloc[i]['Date']+pd.DateOffset(days=int(output.iloc[i]['PromoDays']))).strftime('%Y-%m-%d')})

            
        final_output=pd.DataFrame(event_list)
        records = final_output.to_dict(orient='records')

        # Convert the list of dictionaries to JSON
        json_variable = json.dumps(records)


        calendar_options = {

            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth",
            },
            "initialDate": str(datetime.datetime.today().date()),
            "initialView": "dayGridMonth",
            "height": "550px",  # Adjust height as needed
            # "width": "100px"
            
        }

        state = calendar(
            events=event_list,
            options=calendar_options,
            custom_css="""
            .fc-event-past {
                opacity: 0.8;
            }
            .fc-event-time {
                font-style: italic;
            }
            .fc-event-title {
                font-weight: 200;
            }
            .fc-toolbar-title {
                font-size: 1rem;
            }
            .fc {
                border: 5px solid #ddd; /* Add border to calendar */
                background-color: white; /* Set white background */
                padding: 5px; /* Add padding for better spacing */
            }
            
            """,
        )

        weeks = ['W{}'.format(i) for i in range(1, 53)]

        # Create an empty DataFrame with weeks as columns
        df = pd.DataFrame(columns=['Promo Event']+weeks)

        # Display the empty DataFrame
        for i in range(output.shape[0]):
# Get the week number of the promo event
        # Get the ISO week number for the original date
            if output.iloc[i]['Date']!=None:
                week_number = pd.to_datetime(output.iloc[i]['Date']).isocalendar().week

            # Get the ISO week number for the date incremented by PromoDays
                if len(output.iloc[i]['PromoDays'])==0:
                    week_number2 = pd.to_datetime(output.iloc[i]['Date']).isocalendar().week
                else:
                    week_number2 = pd.to_datetime(pd.to_datetime(output.iloc[i]['Date']) + pd.DateOffset(days=int(output.iloc[i]['PromoDays']))).isocalendar().week
                df.at[i, 'Promo Event'] = 'Promo {}'.format(i + 1)
                if len(output.iloc[i]['PromoDays'])!=0:

                    for j in range(week_number,week_number2+1):

                        if j!= week_number and j!= week_number2:
                            df.at[i, 'W{}'.format(j)] = 7

                        elif j ==week_number2:
                            start_of_week = pd.to_datetime(pd.to_datetime(output.iloc[i]['Date']) + pd.DateOffset(days=int(output.iloc[i]['PromoDays']))) - datetime.timedelta(days=pd.to_datetime(pd.to_datetime(output.iloc[i]['Date']) + pd.DateOffset(days=int(output.iloc[i]['PromoDays']))).weekday())
                            lived_days = (pd.to_datetime(pd.to_datetime(output.iloc[i]['Date']) + pd.DateOffset(days=int(output.iloc[i]['PromoDays']))) - start_of_week).days + 1
                            df.at[i, 'W{}'.format(j)] = lived_days

        df=df.fillna(' ')

            
        def color_cells(val):

            if isinstance(val,int):
                return 'background-color: #34b1aa'
            else:
                return ''

        # Apply the background color to the DataFrame
        
        
        with stylable_container(
                key="container_with_border14",
                css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: calc(1em - 1px);
                            background-color: white;
                        }
                        """,
                        ):
            styled_df = df.style.map(color_cells).hide(axis="index")
            
            html_table = styled_df.to_html(index=True, classes=["dataframe"], escape=True)
                    

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
                                border: 3px solid #ddd;
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

            multi_level_header = """
            <thead>
                <tr>
                    <th></th> <!-- Empty cell for index column -->
                    <th colspan="4">Jan</th>
                    <th colspan="4">Feb</th>
                    <th colspan="5">Mar</th>
                    <th colspan="4">Apr</th>
                    <th colspan="4">May</th>
                    <th colspan="5">Jun</th>
                    <th colspan="4">Jul</th>
                    <th colspan="4">Aug</th>
                    <th colspan="5">Sep</th>
                    <th colspan="4">Oct</th>
                    <th colspan="4">Nov</th>
                    <th colspan="5">Dec</th>
                </tr>
            </thead>
            """

            # Replace the original header with the multi-level header
            html_table_with_multi_header = html_table.replace("<thead>", multi_level_header)
            # Combine HTML table and custom CSS
            html_with_css = f"<div class='table-container'>{custom_css}{html_table_with_multi_header}</div>"


            # Display the styled DataFrame
            st.components.v1.html(html_with_css, height=550)


            # st.dataframe(styled_df)
        

        if button:
            st.write(" ")

            plot1,plot2=st.columns([3,1])
            with plot1:
                baseline_yearly=df_filtered2.groupby(['ppg_id','brand_nm','retailer','segment','start_date'])['baseline'].first().reset_index()
                baseline_uplift=[baseline_yearly.groupby(['ppg_id','brand_nm','retailer','segment'])['baseline'].sum().reset_index()['baseline'][0]]

                for i in event_filtered_data['input_number'].unique():
                    temp = event_filtered_data[event_filtered_data['input_number']==i]
                    if len(output.iloc[i]['Promo Tactic'])==0 or len(output.iloc[i]['Offer Type'])==0 or len(output.iloc[i]['Offer Mechanic'])==0 or output.iloc[i]['Date']==None or len(output.iloc[i]['PromoDays'])==0 or len(output.iloc[i]['Discount'])==0 or output.iloc[i]['Redemption']==0:
                        break


                    increment = temp['incremental_volume'].sum()

                    baseline_uplift.append(increment)
                baseline_uplift.append(sum(baseline_uplift))

                label_list=['Baseline']
                for i in event_filtered_data['input_number'].unique():

                    if len(output.iloc[i]['Promo Tactic'])==0 or len(output.iloc[i]['Offer Type'])==0 or len(output.iloc[i]['Offer Mechanic'])==0 or output.iloc[i]['Date']==None or len(output.iloc[i]['PromoDays'])==0 or len(output.iloc[i]['Discount'])==0 or output.iloc[i]['Redemption']==0:
                        break
                    label_list.append('Incremental Sales Promo'+str(i+1))
                label_list.append("Total")

                fig = go.Figure(go.Waterfall(
                        orientation = "v",
                        measure = ["absolute"]+ ["relative"]* (len(label_list)-2)+["total"],
                        x = label_list,
                        textposition = "outside",
                        y = baseline_uplift,
                        connector = {"mode": "between"},
                        decreasing = {"marker":{"color":"#D91E18"}},
        increasing = {"marker":{"color":"#06C480"}},
        totals = {"marker":{"color":"#1E3D7D"}} 
                ))
                fig.data[0].connector.visible = False

                y_axe=0
                for i, value in enumerate(baseline_uplift[:-1]):

                        if value is not None:

                            y_axe+=baseline_uplift[i]
                            fig.add_annotation(
                                x=label_list[i],
                                y=y_axe,
                                text=convert_to_abbreviated(round(value,0)),
                                showarrow=False,
                                font=dict( size=16, color="Black"),
                                yshift=15
                            )
                y_axe=0
                for i, value in enumerate(baseline_uplift[-1:]):
                        if value is not None:
                            y_axe+=baseline_uplift[-1]
                            fig.add_annotation(
                                x=label_list[-1],
                                y=y_axe,
                                text=convert_to_abbreviated(round(value,0)),
                                showarrow=False,
                                font=dict( size=16, color="Black"),
                                yshift=15
                            )

                fig.update_layout(
                                title = "Baseline sales Vs Promotional Sales",
                                title_x=0.5 ,plot_bgcolor="white",
                            paper_bgcolor="white", bargap = 0.5,height=550
                        )
                fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6
        ,paper_bgcolor="white", plot_bgcolor="white" ,yaxis=dict(
                title_standoff=30),margin=dict(l=100),xaxis=dict(
                title_standoff=30),
                                                    )
                fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=12, family='Graphik', color='black'))
                fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=12, family='Graphik', color='black'))

                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=False,title_text = 'Volume')
                st.plotly_chart(fig, theme=None,use_container_width=True)
                event_filtered_data['ROI']=event_filtered_data['ROI']
            with plot2:
                categories = ['Total Sales']
                values1 = [baseline_uplift[0]]
                values2 = [sum(baseline_uplift[1:-1])]

                # Create traces for each stacked component
                trace1 = go.Bar( x=['Total Sales'],y=values1, name='Baseline',marker=dict(color='#1E3D7D'),text=convert_to_abbreviated(round(values1[0],1)), textposition='inside',textfont=dict(
                                    size=14,
                                    color='black',  # Text color
                                    family='Graphik' # Font
                                ))
                trace2 = go.Bar( x=['Total Sales'],y=values2, name='Incremental Sales',marker=dict(color='#06C480'),text=convert_to_abbreviated(round(values2[0],0)), textposition='inside',textfont=dict(
                                    size=14,
                                    color='black',  # Text color
                                    family='Graphik' # Font
                                ))

                # Create the stacked bar plot
                fig = go.Figure(data=[trace1, trace2])

                # Update layout
                fig.update_layout(
                    title='Total Sales',
                    # xaxis_title='Sales',
                    yaxis_title='Volume',
                    barmode='stack',  # Set the bar mode to stack
                    title_x=0.5 ,plot_bgcolor="white",
                            paper_bgcolor="white", bargap = 0.5,height=550
                )

                fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargroupgap=0.6,
                                                    legend=dict(orientation='h',yanchor="top", y=0.5, xanchor="center", x=1.2,
                                                                bgcolor = 'white',font=dict(size=12, family='Graphik', color='black')))
                fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=12, family='Graphik', color='black'))
                fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=12, family='Graphik', color='black'))

                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=False,title_text = 'Volume')
                st.plotly_chart(fig, theme=None,use_container_width=True)
                event_filtered_data['ROI']=event_filtered_data['ROI']
            event_filtered_data=event_filtered_data.groupby(['retailer','brand_nm','segment','ppg_id','promo_tactic','offer_mechanic','offer_type','start_dates','promo_duration_days','discount','Redemption Rate']).agg({
                'incr_revenue':'sum','incremental_volume':'sum','promo_investment':'sum','baseline':'sum',
                'promo_price_unit':'mean','no_promo_price_unit':'mean','avg_price_unit':'mean'
            }).reset_index()
            event_filtered_data['ROI']=(event_filtered_data['incr_revenue']/event_filtered_data['promo_investment'])+1
            event_filtered_data['volume_lift_pct']=(event_filtered_data['incremental_volume']/event_filtered_data['baseline'])*100

            edited_df=event_filtered_data[['retailer','brand_nm','segment','ppg_id','promo_tactic','offer_mechanic','offer_type','start_dates','promo_duration_days','discount',"incremental_volume"
                                    ,"volume_lift_pct",'ROI','baseline','promo_price_unit','no_promo_price_unit','avg_price_unit','Redemption Rate']]

            edited_df.columns = ['Retailer','Brand','Segment','PPG','Promo Tactic','Offer Mechanic','Offer Type','Start Date','Promo Duration Days','Discount',
                                        'Incremental Volume','Volume Uplift','ROI','Baseline','Promo Price Unit','No Promo Price Unit','Average Price Unit','Redemption Rate']


            edited_df=edited_df.drop_duplicates()
            edited_df['Baseline'] = edited_df['Baseline'].astype(int).map('{:,}'.format)
            edited_df['Incremental Volume'] = edited_df['Incremental Volume'].astype(int).map('{:,}'.format)
            with stylable_container(
                key="container_with_border15",
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
                            key="green_button_st2",
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
                            file_name="Promotion Simulation.csv",
                            mime="text/csv",
                            key="download_button5"  # Ensure unique key for reactivity
                        )

                

                # Display HTML table with DataTable and custom styling
                st.components.v1.html(html_with_css,height=6000)


