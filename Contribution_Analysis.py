import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container
# st.image('sigmoid_logo.png')
def contribution_analysis():


    # render_navbar()
    #data

    df_final = pd.read_csv('final_pricing_consolidated_file.csv')
    df = df_final.copy()
    df=df.dropna()
    df['retailer_id'] = df['retailer_id'].apply(lambda x: x.upper())
    df['retailer_id']=np.where(df['retailer_id']=='Target PT','Target',df['retailer_id'])
    df['retailer_id']=np.where(df['retailer_id']=='Publix Total TA','Publix',df['retailer_id'])
    df['retailer_id']=np.where(df['retailer_id']=='CVS Total Corp ex HI TA','CVS',df['retailer_id'])
    df['Distribution_coeff'] = np.where(df['Distribution_coeff']>=1,1,df['Distribution_coeff'])
    df['year'] = pd.to_datetime(df['year'].astype(str), format='%Y')
    df['year'] = df['year'].dt.strftime("%Y") 
    df['day']=1
    df['month_name']=df['month'].map({1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'})
    # Define the order of the month names
    month_order = ['Jan', 'Feb', 'Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    # Convert month_name column to categorical data type with specified order
    df['month_name'] = pd.Categorical(df['month_name'], categories=month_order, ordered=True)
    df['year']=np.where(df['year']=='2022','2023',df['year'])
    df['year']=np.where(df['year']=='2021','2022',df['year'])



    with stylable_container(
        key="container_with_border1",
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
             m0 = st.multiselect("Category",["SurfaceCare"],default='SurfaceCare', key=5549)
        with f1:
            m1 = st.multiselect("Manufacturer",['All']+ df['manufacturer_nm'].unique().tolist(), key=1)
            if "All" in m1:
                m1 = df['manufacturer_nm'].unique().tolist()
        if len(m1)==0:
            df_fil = df  
        else:          
            df_fil = df[df['manufacturer_nm'].isin(m1)]
        with f2:
            m2 = st.multiselect("Brand",['All']+df_fil['brand_nm'].unique().tolist(),key=2)
            if "All" in m2:
                m2 = df_fil['brand_nm'].unique().tolist()
        if len(m2)==0:
            df_fil = df_fil  
        else:          
            df_fil = df_fil[df_fil['brand_nm'].isin(m2)]
        with f3:
            m3 = st.multiselect("PPG ",['All']+df_fil['ppg_nm'].unique().tolist(),key=4)
            if "All" in m3:
                m3 = df_fil['ppg_nm'].unique().tolist()
        if len(m3)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['ppg_nm'].isin(m4)]
        with f4:
            m4 = st.multiselect("Retailer",['All']+df_fil['retailer_id'].unique().tolist(),key=3)
            if "All" in m4:
                m4 = df_fil['retailer_id'].unique().tolist()
        if len(m4)==0:
            df_fil = df_fil  
        else:
            df_fil = df_fil[df_fil['retailer_id'].isin(m4)]

        df_filtered = df_fil.copy()

    with st.container(height =430, border=False):

            cl1,cl2,cl3=st.columns([1,1,1])


            #chart1
            with cl1:

                df_filtered['Price Elasticity']= df_filtered['Price_coeff']
                df['Price Elasticity']= df['Price_coeff']

                df_mod = (df_filtered.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm']).agg({
                            'Price Elasticity':'mean',
                            }).reset_index().round(2))
                df_mod_all = (df.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm']).agg({
                            'Price Elasticity':'mean',
                            }).reset_index().round(2))
                df_mod2 = round(df_mod_all['Price Elasticity'].mean(),2)
                df_mod['Category Price Elasticity']=df_mod2
                melted_df = df_mod.melt(id_vars=['manufacturer_nm','brand_nm','retailer_id','ppg_nm'], var_name='Drivers', value_name='elasticity')
                melted_df_check = (melted_df.groupby(['Drivers'])['elasticity'].mean().reset_index().round(2))
                custom_order = ['Category Price Elasticity', 'Price Elasticity']

                # Convert the 'Name' column to a categorical data type with custom order
                melted_df_check['Drivers'] = pd.Categorical(melted_df_check['Drivers'], categories=custom_order, ordered=True)

                # Sort the DataFrame by the 'Drivers' column
                melted_df_check = melted_df_check.sort_values(by='Drivers')


                
                melted_df_check["Color"] = np.where(melted_df_check["elasticity"]<0,  '#1E3D7D', '#06C480')

                trace1 = go.Bar(
                    x=['Category Benchmark', 'Selected Product'],
                    y=melted_df_check['elasticity'],
                    text=melted_df_check['elasticity'], textfont=dict(
                                size=15,
                                color='white',  # Text color
                                family='Graphik' # Font
                            ),
                    marker_color=melted_df_check['Color'],
                    name='Elasticites',
                    orientation='v',

                )
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(trace1)
                fig.update_layout(title_text="Price Elasticites",paper_bgcolor="white",plot_bgcolor="white")
                fig.update_xaxes(showgrid=False)
                fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6)
                fig.update_xaxes(showline=False,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'),range = [-1.5,0],dtick=0.5)


                # Set y-axes titles
                fig.update_yaxes(
                    title_text="Elasticity", 
                    secondary_y=False,showgrid=False)
                
                fig.update_layout(
                xaxis=dict(
                        title_standoff=25),
                                                        )
                st.plotly_chart(fig, theme=None,use_container_width=True,height=354)


            with cl3:
                df_filtered['Distribution Elasticity']= df_filtered['Distribution_coeff']
                df['Distribution Elasticity']= df['Distribution_coeff']
                df_mod = (df_filtered.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm']).agg({
                            'Distribution Elasticity':'mean',
                            }).reset_index().round(2))
                df_mod_all = (df.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm']).agg({
                            'Distribution Elasticity':'mean',
                            }).reset_index().round(2))
                df_mod2 = round(df_mod_all['Distribution Elasticity'].mean(),2)

                df_mod['Category Distribution Elasticity']=df_mod2
                melted_df = df_mod.melt(id_vars=['manufacturer_nm','brand_nm','retailer_id','ppg_nm'], var_name='Drivers', value_name='elasticity')
                melted_df_check = (melted_df.groupby(['Drivers'])['elasticity'].mean().reset_index().round(2))

                custom_order = ['Category Distribution Elasticity', 'Distribution Elasticity']

                # Convert the 'Name' column to a categorical data type with custom order
                melted_df_check['Drivers'] = pd.Categorical(melted_df_check['Drivers'], categories=custom_order, ordered=True)

                # Sort the DataFrame by the 'Drivers' column
                melted_df_check = melted_df_check.sort_values(by='Drivers')


                
                melted_df_check["Color"] = np.where(melted_df_check["elasticity"]<0,  '#1E3D7D', '#06C480')
                trace1 = go.Bar(
                    x=['Category Benchmark', 'Selected Product'],
                    y=melted_df_check['elasticity'],
                    text=melted_df_check['elasticity'], 
                    textfont=dict(
                            size=15,
                            color='black',  # Text color
                            family='Graphik' # Font
                        ),
                    marker_color=melted_df_check['Color'],
                    name='Elasticites',
                    orientation='v',

                )
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(trace1)
                fig.update_layout(title_text=" Distribution Elasticites",paper_bgcolor="white",plot_bgcolor="white")
                fig.update_xaxes(showgrid=False)
                fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6)
                fig.update_xaxes(showline=False,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'),range = [0,1.5],dtick=0.5)


                # Set y-axes titles
                fig.update_yaxes(
                    title_text="Elasticity", 
                    secondary_y=False,showgrid=False)
                
                fig.update_layout(xaxis=dict(
                        title_standoff=25),
                        )
                st.plotly_chart(fig, theme=None,use_container_width=True,height=354)
            
            with cl2:
                df_filtered['Cross Price Elasticity']= df_filtered['com_price_coef']
                df['Cross Price Elasticity']= df['com_price_coef']
                df_mod = (df_filtered.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm']).agg({
                            'Cross Price Elasticity':'mean',
                            }).reset_index().round(2))
                df_mod_all = (df.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm']).agg({
                            'Cross Price Elasticity':'mean',
                            }).reset_index().round(2))
                df_mod2 = round(df_mod_all['Cross Price Elasticity'].mean(),2)
                df_mod['Category Cross Price Elasticity']=df_mod2
                df_mod=df_mod[['manufacturer_nm','brand_nm','retailer_id','ppg_nm','Category Cross Price Elasticity','Cross Price Elasticity']]
                melted_df = df_mod.melt(id_vars=['manufacturer_nm','brand_nm','retailer_id','ppg_nm'], var_name='Drivers', value_name='elasticity')
                melted_df_check = (melted_df.groupby(['Drivers'])['elasticity'].mean().reset_index().round(2))

                custom_order = ['Category Cross Price Elasticity', 'Cross Price Elasticity']

                # Convert the 'Drivers' column to a categorical data type with custom order
                melted_df_check['Drivers'] = pd.Categorical(melted_df_check['Drivers'], categories=custom_order, ordered=True)

                # Sort the DataFrame by the 'Drivers' column
                melted_df_check = melted_df_check.sort_values(by='Drivers')


                
                melted_df_check["Color"] = np.where(melted_df_check["elasticity"]<0,  '#1E3D7D', '#06C480')
                trace1 = go.Bar(
                    x=['Category Benchmark', 'Selected Product'],
                    y=melted_df_check['elasticity'],
                    text=melted_df_check['elasticity'], 
                    textfont=dict(
                                size=15,
                                color='black',  # Text color
                                family='Graphik' # Font
                            ),
                    marker_color=melted_df_check['Color'],
                    name='Elasticites',
                    orientation='v',

                )
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(trace1)
                fig.update_layout(title_text="Cross Price Elasticites",paper_bgcolor="white",plot_bgcolor="white")
                fig.update_xaxes(showgrid=False)
                fig.update_layout(title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6)
                fig.update_xaxes(showline=False,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
                fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'),range = [0,1.5],dtick=0.5)


                # Set y-axes titles
                fig.update_yaxes(
                    title_text="Elasticity", 
                    secondary_y=False,showgrid=False)
                
                fig.update_layout(xaxis=dict(
                        title_standoff=25),
                )
                
                st.plotly_chart(fig, theme=None,use_container_width=True,height=354)
            #chart2
            df_filtered['Baseline']= df_filtered['baseline']
            df_filtered['Price Driver']= df_filtered['price_driver']
            df_filtered['Promotion']= df_filtered['promo']
            df_filtered['Distribution']= df_filtered['distribution']
            df_filtered['Holiday']= df_filtered['holiday']
            df_filtered['Cannibalization']= df_filtered['cannibalization']
            df_filtered['Seasonality']= df_filtered['seasonlaity']
            df_filtered['Pantry Loading']= df_filtered['pantry loading']



                
            df_mod = df_filtered.groupby(['manufacturer_nm','brand_nm','retailer_id','ppg_nm','year']).agg({
                        'Baseline':'sum',
                        'Promotion':'sum',
                        'Price Driver':'sum',
                        'Pantry Loading':'sum',
                        'Distribution':'sum',
                        'Holiday':'sum',
                        'Cannibalization':'sum',
                        'Seasonality':'sum',
                        'Price_coeff':'mean',
                        'Distribution_coeff':'mean',
                        'com_price_coef':'mean',}).reset_index()

            # Define colors for each driver
            colors = {
            'Baseline': '#C6DE35',
            'Promotion': '#E7B3DE',
            'Price Driver': '#06C480',
            'Pantry Loading': '#7977CB',
            'Distribution': '#35F4C6',
            'Holiday': '#4E5960',
            'Cannibalization': '#0996CE',
            'Seasonality': '#1E3D7D'}
 

            year_list = (sorted(df_mod['year'].unique().tolist())[-2:])
            df_mod=df_mod[df_mod['year'].isin(year_list)]
            df_mod=pd.pivot_table(df_mod,index=['manufacturer_nm','brand_nm','retailer_id','ppg_nm'], columns=['year'],
                            values=['Baseline','Promotion','Price Driver',
                                    'Pantry Loading','Distribution','Holiday','Cannibalization','Seasonality','Price_coeff', 'Distribution_coeff', 'com_price_coef']).reset_index()


            new_cols=[('{1} {0}'.format(*tup)) for tup in df_mod.columns]

            df_mod.columns = new_cols

            df_mod.columns =df_mod.columns.str.replace(' ', '')

            




            df_mod['total_Baseline_'+str(year_list[0])] = df_mod[str(year_list[0])+
                                    'Baseline']+df_mod[str(year_list[0])+'Cannibalization']+df_mod[str(year_list[0])+
                                    'Distribution']+df_mod[str(year_list[0])+'Holiday']+df_mod[str(year_list[0])+'PantryLoading']+df_mod[str(year_list[0])+'PriceDriver']+df_mod[str(year_list[0])+'Seasonality']


            df_mod['total_Baseline_'+str(year_list[1])] = df_mod[str(year_list[1])+
                                    'Baseline']+df_mod[str(year_list[1])+'Cannibalization']+df_mod[str(year_list[1])+
                                    'Distribution']+df_mod[str(year_list[1])+'Holiday']+df_mod[str(year_list[1])+'PantryLoading']+df_mod[str(year_list[1])+'PriceDriver']+df_mod[str(year_list[1])+'Seasonality']
            df_mod['baseline_diff']=df_mod['total_Baseline_'+str(year_list[1])]-df_mod['total_Baseline_'+str(year_list[0])]





            np.random.seed(10)
            df_mod['price_contri']=0.35 + (0.9 - 0.35) * np.random.rand(df_mod.shape[0])
            df_mod['price_contri']=df_mod['price_contri']*-1
            df_mod['distribution_contri']=0.36 + (0.8 - 0.36) * np.random.rand(df_mod.shape[0])
            df_mod['com_price_contri']=1-(df_mod['price_contri']+df_mod['distribution_contri'])
            df_mod['Price_Driver'] = df_mod['baseline_diff']*df_mod['price_contri']
            df_mod['Distribution'] = df_mod['baseline_diff']*df_mod['distribution_contri']
            df_mod['Cannibalization'] = df_mod['baseline_diff']*df_mod['com_price_contri']

            df_mod['baseline_total_diff']=df_mod['Price_Driver']+df_mod['Distribution']+df_mod['Cannibalization']




            Baseline_22 =df_mod['total_Baseline_'+str(year_list[1])].sum()
            Baseline_21 =df_mod['total_Baseline_'+str(year_list[0])].sum()
            Price_Driver = df_mod['Price_Driver'].sum()
            Distribution=df_mod['Distribution'].sum()
            Cannibalization = df_mod['Cannibalization'].sum()




            baseline_diff = ((Baseline_22/Baseline_21)-1)*100
            price_diff = df_mod['price_contri'].mean()*100*((Baseline_22/Baseline_21)-1)
            dist_diff = df_mod['distribution_contri'].mean()*100*((Baseline_22/Baseline_21)-1)
            com_price_diff = df_mod['com_price_contri'].mean()*100*((Baseline_22/Baseline_21)-1)
            percentage_changes=[dist_diff,com_price_diff]
            baseline_ch=[price_diff,baseline_diff]
            cat_baseline=['Own Price','Baseline'+' '+str(year_list[1])]
            val_baseline=[Baseline_21,Baseline_22 ]
            categories = ['Baseline'+' '+str(year_list[0]),'Own Price','Own Distribution','Competitor Price','Baseline'+' '+str(year_list[1])]
            values=[Baseline_21,Price_Driver,Distribution,Cannibalization,Baseline_22 ]
            values2=[Baseline_22,-Cannibalization,-Distribution,-Price_Driver,Baseline_21 ]
            categories2 = ['Baseline'+' '+str(year_list[1]),'Competitor Price','Own Distribution','Own Price','Baseline'+' '+str(year_list[0])]

            fig = go.Figure(go.Waterfall(
                    orientation = "h",
                    measure = ["absolute","relative", "relative","relative","absolute"],
                    x = values2,
                    textposition = "outside",
                    y = categories2,
                    # connector = {"line":{"color":colors}},
                    decreasing = {"marker":{"color":"#06C480"}},
        increasing = {"marker":{"color":"#D91E18"}},
        totals = {"marker":{"color":"#1E3D7D"}} 
                ))
            # Add annotations with percentage changes
            for i, value in enumerate(percentage_changes):
                x_axe=values[0]+values[1]
                if value is not None:

                    fig.add_annotation(
                        x=x_axe,
                        y=categories[i+2],
                        text=f'{value:.2f}%',
                        showarrow=False,
                        font=dict( size=15, color="Black"),
                        xshift=85,
                    )
            for j, values in enumerate(baseline_ch):

                if values is not None:

                    fig.add_annotation(
                        y=cat_baseline[j],
                        x=val_baseline[j],
                        text=f'{values:.2f}%',
                        showarrow=False,
                        font=dict(size=15, color="Black"),
                        xshift=30
                    )

            fig.update_layout(title_text="Contribution by Drivers",title_x=0.45,
                title_font=dict(size=24, family="Graphik",color='#555867'),bargap=0.6
            ,paper_bgcolor="white", plot_bgcolor="white" ,yaxis=dict(
                    title_standoff=30),xaxis=dict(
                    title_standoff=30),margin=dict(t=60, l=100, r=100, b=10)
                                                        )
            fig.update_xaxes(title_text="Drivers", showgrid=False)
            fig.update_yaxes(showgrid=False)
            # fig.update_layout(title_font=dict(size=24, family="Arial",color='#4E5960'))
            fig.update_xaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))
            fig.update_yaxes(showline=True,linewidth=1,linecolor='black',mirror=False,title_font=dict(size=16, family='Graphik', color='black'),  # Change font for y-axis title
                                                                tickfont=dict(size=14, family='Graphik', color='black'))


            st.plotly_chart(fig, use_container_width=True)

