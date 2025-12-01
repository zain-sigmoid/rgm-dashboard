from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import datetime
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pydantic import BaseModel, Field, ConfigDict

from src.utility.logger import AppLogger
# Setup Logger
import logging
logging.basicConfig(level=logging.INFO)
logger = AppLogger.get_logger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT_DIR / "simulation_data.csv"


# --- Helper Functions ---
def convert_to_abbreviated(number):
    """Helper to replicate utils function for chart text."""
    try:
        num = float(number)
        if abs(num) >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif abs(num) >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return f"{num:.1f}"
    except (ValueError, TypeError):
        return str(number)


# --- Pydantic Models ---

class GlobalFilters(BaseModel):
    """Filters applied to the dataset before simulation logic."""
    category: Optional[List[str]] = Field(default=None)
    brand: Optional[List[str]] = Field(default=None)
    segment: Optional[List[str]] = Field(default=None)
    ppg: Optional[List[str]] = Field(default=None)
    retailer: Optional[List[str]] = Field(default=None)


class SimulationEventInput(BaseModel):
    """Represents one row of user input for a promotion event."""
    promo_tactic: List[str] = Field(default_factory=list)
    offer_type: List[str] = Field(default_factory=list)
    offer_mechanic: List[str] = Field(default_factory=list)
    start_date: Optional[datetime.date] = None
    duration: Optional[int] = None
    discount: Optional[float] = None
    redemption_rate: Optional[float] = None


class CalendarData(BaseModel):
    """Holds data structure for the frontend calendar component."""
    events_json: List[Dict[str, str]]
    week_grid_df: pd.DataFrame 
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SimulationCharts(BaseModel):
    """Holds Plotly figures."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    waterfall_chart: go.Figure
    stacked_bar_chart: go.Figure


class SimulationResponse(BaseModel):
    """Master response object."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    drill_down_table: pd.DataFrame
    calendar_data: CalendarData
    charts: SimulationCharts
    filter_options: Dict[str, List[Any]]


# --- Main Logic Class ---

class SimulationAnalysis:

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path
        self.df_raw = self._load_and_clean_df()

    def _load_and_clean_df(self) -> pd.DataFrame:
        if not self.data_path.exists():
            msg = f"Data file not found: {self.data_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        df2 = pd.read_csv(self.data_path)

        # Basic text cleaning & Extraction
        df2['segment'] = df2['subsegment_name'].str.split('|').str[0]
        df2['month'] = pd.to_datetime(df2['start_date']).dt.month
        
        # Promo Tactic Logic
        df2['promo_tactic'] = np.where(df2['promo_tactic']=='unknown','Display & TPR', df2['promo_tactic'] )
        df2['promo_tactic'] = np.where(df2['promo_tactic']=='No Tactic','Feature & TPR', df2['promo_tactic'] )
        df2['promo_tactic'] = np.where(df2['promo_tactic']=='Feature & TPR','Feature', df2['promo_tactic'] )
        df2['promo_tactic'] = np.where(df2['promo_tactic']=='Display & TPR','Display', df2['promo_tactic'] )
        df2['promo_tactic'] = np.where(df2['promo_tactic']=='Feature Only','Feature', df2['promo_tactic'] )
        df2['promo_tactic'] = np.where(df2['promo_tactic']=='Display Only','Display', df2['promo_tactic'] )
        df2['promo_tactic'] = np.where(df2['promo_tactic']=='TPR Only','TPR', df2['promo_tactic'] )

        df2['ROI'] = df2['roi']
        df2['offer_mechanic'] = np.where(df2['offer_mechanic']=='unknown','special x off',df2['offer_mechanic'])
        
        # Bins
        bins = [0,10,20,30,40,50,60,70,80]
        labels = ['0%-10%','10%-20%','20%-30%','30%-40%','40%-50%','50%-60%','60%-70%','70%-80%']
        df2['promo_bins'] = pd.cut(df2['discount'], bins=bins,labels=labels, right=False) 

        # Offer Type
        df2['offer_type'] = np.where(df2['offer_type']=='unknown','spend_reward',df2['offer_type'])
        df2['offer_type'] = df2['offer_type'].str.upper()
        df2['offer_type'] = df2['offer_type'].replace('_', ' ', regex=True)

        # Date adjustments (Last Sunday Logic)
        df2['start_dates'] = pd.to_datetime(df2['start_date']) 
        days_to_subtract = df2['start_dates'].dt.dayofweek + 1
        df2['start_dates'] = df2['start_dates'] - pd.to_timedelta(days_to_subtract, unit='D')
        df2['start_dates'] = df2['start_dates'].dt.strftime("%Y/%m/%d")

        # Retailer cleaning
        df2['retailer'] = np.where(df2['retailer']=='Target PT','Target',df2['retailer'])
        df2['retailer'] = np.where(df2['retailer']=='Publix Total TA','Publix',df2['retailer'])
        df2['retailer'] = np.where(df2['retailer']=='CVS Total Corp ex HI TA','CVS',df2['retailer'])
        
        df2['brand_nm'] = df2['ppg_id'].str.split('|').str[2]
        df2['retailer'] = df2['retailer'].apply(lambda x: x.upper())

        return df2

    def get_filter_options(self) -> Dict[str, List[str]]:
        """Returns unique values for global filters."""
        # Helper to safely get unique sorted lists
        def get_unique(col):
            return sorted(self.df_raw[col].dropna().unique().tolist())

        return {
            "category": ["SurfaceCare"], # Default from original
            "brand": get_unique("brand_nm"),
            "segment": get_unique("segment"),
            "ppg": get_unique("ppg_id"),
            "retailer": get_unique("retailer"),
            # Options for the simulation inputs
            "promo_tactic": get_unique("promo_tactic"),
            "offer_type": get_unique("offer_type"),
            "offer_mechanic": get_unique("offer_mechanic")
        }

    def _apply_global_filters(self, filters: GlobalFilters) -> pd.DataFrame:
        df_fil = self.df_raw.copy()

        def is_active(f_val):
            return f_val is not None and len(f_val) > 0 and "All" not in f_val

        # Category is hardcoded in original but we check it here
        # if is_active(filters.category): ... 

        if is_active(filters.brand):
            df_fil = df_fil[df_fil['brand_nm'].isin(filters.brand)]
        
        if is_active(filters.segment):
            df_fil = df_fil[df_fil['segment'].isin(filters.segment)]
        
        if is_active(filters.ppg):
            df_fil = df_fil[df_fil['ppg_id'].isin(filters.ppg)]
            
        if is_active(filters.retailer):
            df_fil = df_fil[df_fil['retailer'].isin(filters.retailer)]
            
        return df_fil

    def _process_simulations(self, df_base: pd.DataFrame, events: List[SimulationEventInput]):
        """
        Iterates through inputs, applies logic, and aggregates results.
        Returns aggregated DataFrame, list of valid inputs for Calendar/Charts, 
        and the filtered event data.
        """
        event_filtered_data = pd.DataFrame()
        valid_events_meta = [] # To store metadata for calendar/charts
        
        for i, event in enumerate(events):
            # Start with the globally filtered data
            df_temp = df_base.copy()

            # Apply Simulation Filters
            if event.promo_tactic and "All" not in event.promo_tactic:
                df_temp = df_temp[df_temp['promo_tactic'].isin(event.promo_tactic)]
            
            if event.offer_type and "All" not in event.offer_type:
                df_temp = df_temp[df_temp['offer_type'].isin(event.offer_type)]
            
            if event.offer_mechanic and "All" not in event.offer_mechanic:
                df_temp = df_temp[df_temp['offer_mechanic'].isin(event.offer_mechanic)]
            
            if event.start_date:
                # Ensure type matching for date comparison
                df_temp = df_temp[pd.to_datetime(df_temp['start_dates']) == pd.to_datetime(event.start_date)]
            
            if event.duration:
                df_temp = df_temp[df_temp['promo_duration_days'] == int(event.duration)]
            
            if event.discount:
                df_temp = df_temp[df_temp['discount'] == int(event.discount)]
            
            if event.redemption_rate:
                df_temp['Redemption Rate'] = event.redemption_rate / 100
            
            # Check validity (similar to original: if fields are empty, we might skip logic)
            # The original code logic for 'ROI' calculation inside loop implies 
            # if specific fields are missing, ROI is 0. 
            # Here we assume valid inputs are provided if they reach this stage.
            
            # Logic to determine if this event is "Complete" enough to add to results
            is_valid = (
                (event.promo_tactic) and 
                (event.offer_type) and 
                (event.offer_mechanic) and 
                (event.start_date) and 
                (event.duration) and 
                (event.discount) and 
                (event.redemption_rate)
            )

            if is_valid:
                df_temp['input_number'] = i
                event_filtered_data = pd.concat([event_filtered_data, df_temp])
                
                # Metadata for Calendar/Waterfall
                valid_events_meta.append({
                    'index': i,
                    'start_date': event.start_date,
                    'duration': int(event.duration),
                    'label': f'Promo {i+1}'
                })
        
        return event_filtered_data, valid_events_meta

    def _generate_calendar_data(self, valid_events_meta: List[Dict]) -> CalendarData:
        event_list = []
        
        # Prepare Weeks Columns
        weeks = ['W{}'.format(i) for i in range(1, 53)]
        df_weeks = pd.DataFrame(columns=['Promo Event'] + weeks)

        for meta in valid_events_meta:
            idx = meta['index']
            s_date = meta['start_date']
            dur = meta['duration']
            label = meta['label']

            # 1. Calendar Events (JSON format for frontend)
            end_date_obj = pd.to_datetime(s_date) + pd.DateOffset(days=dur)
            event_list.append({
                'title': label,
                'color': '#FF6C6C',
                'start': str(s_date),
                'end': end_date_obj.strftime('%Y-%m-%d')
            })

            # 2. Week Grid Logic
            start_dt = pd.to_datetime(s_date)
            end_dt = start_dt + pd.DateOffset(days=dur)
            
            week_number_start = start_dt.isocalendar().week
            week_number_end = end_dt.isocalendar().week
            
            df_weeks.at[idx, 'Promo Event'] = label

            for j in range(week_number_start, week_number_end + 1):
                col_name = 'W{}'.format(j)
                if j != week_number_start and j != week_number_end:
                    df_weeks.at[idx, col_name] = 7
                elif j == week_number_end:
                    # Calculate days lived in the last week
                    # Find start of that specific week
                    start_of_last_week = end_dt - datetime.timedelta(days=end_dt.weekday())
                    lived_days = (end_dt - start_of_last_week).days + 1
                    df_weeks.at[idx, col_name] = lived_days
                else:
                     # Fallback for start week if needed (original code logic focused on end week mostly)
                     # adhering strictly to original logic flow:
                     pass

        df_weeks = df_weeks.fillna(' ')
        return CalendarData(events_json=event_list, week_grid_df=df_weeks)

    def _create_charts(self, df_base_filtered: pd.DataFrame, event_filtered_data: pd.DataFrame, valid_events_meta: List[Dict]) -> SimulationCharts:
        
        # --- Waterfall Prep ---
        # 1. Baseline Yearly (First value)
        if not df_base_filtered.empty:
            baseline_yearly = df_base_filtered.groupby(['ppg_id','brand_nm','retailer','segment','start_date'])['baseline'].first().reset_index()
            initial_baseline = baseline_yearly.groupby(['ppg_id','brand_nm','retailer','segment'])['baseline'].sum().sum() # Summing if multiple selected
        else:
            initial_baseline = 0
            
        baseline_uplift = [initial_baseline]
        label_list = ['Baseline']

        # 2. Incremental for each valid event
        # Note: Logic relies on 'input_number' in event_filtered_data corresponding to valid_events_meta order
        for meta in valid_events_meta:
            idx = meta['index']
            temp = event_filtered_data[event_filtered_data['input_number'] == idx]
            increment = temp['incremental_volume'].sum()
            baseline_uplift.append(increment)
            label_list.append(f'Incremental Sales Promo{idx+1}')
        
        # 3. Total
        baseline_uplift.append(sum(baseline_uplift))
        label_list.append("Total")

        # --- Waterfall Chart ---
        fig_waterfall = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute"] + ["relative"] * (len(label_list) - 2) + ["total"],
            x=label_list,
            textposition="outside",
            y=baseline_uplift,
            connector={"mode": "between"},
            decreasing={"marker": {"color": "#D91E18"}},
            increasing={"marker": {"color": "#06C480"}},
            totals={"marker": {"color": "#1E3D7D"}}
        ))
        fig_waterfall.data[0].connector.visible = False

        # Annotations (Total Labels)
        y_axe = 0
        for i, value in enumerate(baseline_uplift[:-1]):
            if value is not None:
                y_axe += baseline_uplift[i]
                fig_waterfall.add_annotation(
                    x=label_list[i], y=y_axe, text=convert_to_abbreviated(round(value, 0)),
                    showarrow=False, font=dict(size=16, color="Black"), yshift=15
                )
        
        # Final Total Annotation
        final_val = baseline_uplift[-1]
        fig_waterfall.add_annotation(
             x=label_list[-1], y=final_val, text=convert_to_abbreviated(round(final_val, 0)),
             showarrow=False, font=dict(size=16, color="Black"), yshift=15
        )

        self._apply_chart_layout(fig_waterfall, "Baseline sales Vs Promotional Sales")

        # --- Stacked Bar Chart ---
        values1 = [baseline_uplift[0]]
        values2 = [sum(baseline_uplift[1:-1])] # Sum of incrementals

        trace1 = go.Bar(
            x=['Total Sales'], y=values1, name='Baseline', marker=dict(color='#1E3D7D'),
            text=convert_to_abbreviated(round(values1[0], 1)), textposition='inside',
            textfont=dict(size=14, color='black', family='Graphik')
        )
        trace2 = go.Bar(
            x=['Total Sales'], y=values2, name='Incremental Sales', marker=dict(color='#06C480'),
            text=convert_to_abbreviated(round(values2[0], 0)), textposition='inside',
            textfont=dict(size=14, color='black', family='Graphik')
        )

        fig_bar = go.Figure(data=[trace1, trace2])
        fig_bar.update_layout(yaxis_title='Volume', barmode='stack')
        
        # Specific layout tweak for bar
        fig_bar.update_layout(
             title_text="Total Sales",
             title_x=0.5, plot_bgcolor="white", paper_bgcolor="white", bargap=0.5, height=550,
             title_font=dict(size=24, family="Graphik", color='#555867'), bargroupgap=0.6,
             legend=dict(orientation='h', yanchor="top", y=0.5, xanchor="center", x=1.2,
                         bgcolor='white', font=dict(size=12, family='Graphik', color='black'))
        )
        self._apply_axis_style(fig_bar)

        return SimulationCharts(waterfall_chart=fig_waterfall, stacked_bar_chart=fig_bar)

    def _apply_chart_layout(self, fig, title):
        fig.update_layout(
            title=title, title_x=0.5, plot_bgcolor="white",
            paper_bgcolor="white", bargap=0.5, height=550,
            title_font=dict(size=24, family="Graphik", color='#555867'),
            bargroupgap=0.6,
            yaxis=dict(title_standoff=30), margin=dict(l=100), xaxis=dict(title_standoff=30),
        )
        self._apply_axis_style(fig)

    def _apply_axis_style(self, fig):
        style = dict(size=16, family='Graphik', color='black')
        tick_style = dict(size=12, family='Graphik', color='black')
        fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=False, title_font=style, tickfont=tick_style, showgrid=False)
        fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=False, title_font=style, tickfont=tick_style, showgrid=False, title_text='Volume')

    def _generate_drill_down_table(self, event_filtered_data: pd.DataFrame) -> pd.DataFrame:
        if event_filtered_data.empty:
            return pd.DataFrame()

        # Aggregation Logic
        df_agg = event_filtered_data.groupby([
            'retailer','brand_nm','segment','ppg_id','promo_tactic','offer_mechanic',
            'offer_type','start_dates','promo_duration_days','discount','Redemption Rate'
        ]).agg({
            'incr_revenue':'sum','incremental_volume':'sum','promo_investment':'sum','baseline':'sum',
            'promo_price_unit':'mean','no_promo_price_unit':'mean','avg_price_unit':'mean'
        }).reset_index()

        # Metrics
        with np.errstate(divide='ignore', invalid='ignore'):
            df_agg['ROI'] = (df_agg['incr_revenue'] / df_agg['promo_investment']) + 1
            df_agg['volume_lift_pct'] = (df_agg['incremental_volume'] / df_agg['baseline']) * 100

        # Formatting
        edited_df = df_agg[['retailer','brand_nm','segment','ppg_id','promo_tactic','offer_mechanic','offer_type','start_dates','promo_duration_days','discount',"incremental_volume"
                                    ,"volume_lift_pct",'ROI','baseline','promo_price_unit','no_promo_price_unit','avg_price_unit','Redemption Rate']]

        edited_df.columns = ['Retailer','Brand','Segment','PPG','Promo Tactic','Offer Mechanic','Offer Type','Start Date','Promo Duration Days','Discount',
                                        'Incremental Volume','Volume Uplift','ROI','Baseline','Promo Price Unit','No Promo Price Unit','Average Price Unit','Redemption Rate']
        
        edited_df = edited_df.drop_duplicates()
        return edited_df

    def run_simulation(self, global_filters: GlobalFilters, simulation_inputs: List[SimulationEventInput]) -> SimulationResponse:
        """
        Master function to run the simulation based on filters and user inputs.
        """
        # 1. Apply Global Filters
        df_base_filtered = self._apply_global_filters(global_filters)

        # 2. Process Simulation Logic
        event_filtered_data, valid_events_meta = self._process_simulations(df_base_filtered, simulation_inputs)

        # 3. Generate Outputs
        calendar_data = self._generate_calendar_data(valid_events_meta)
        charts = self._create_charts(df_base_filtered, event_filtered_data, valid_events_meta)
        drill_down_df = self._generate_drill_down_table(event_filtered_data)

        return SimulationResponse(
            drill_down_table=drill_down_df,
            calendar_data=calendar_data,
            charts=charts,
            filter_options=self.get_filter_options()
        )