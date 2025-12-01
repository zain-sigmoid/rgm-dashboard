from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pydantic import BaseModel, Field, ConfigDict
from src.utility.logger import AppLogger

# Setup Logger (Mocking src.utility.logger if not available in your env)
import logging
logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
logger = AppLogger.get_logger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT_DIR / "df_hist_check.csv"


# --- Pydantic Models ---

class PromotionFilters(BaseModel):
    categories: Optional[List[str]] = Field(default=None)
    brands: Optional[List[str]] = Field(default=None)
    segments: Optional[List[str]] = Field(default=None)
    ppgs: Optional[List[str]] = Field(default=None)
    retailers: Optional[List[str]] = Field(default=None)
    offer_types: Optional[List[str]] = Field(default=None)
    promo_tactics: Optional[List[str]] = Field(default=None)
    years: Optional[List[str]] = Field(default=None)
    months: Optional[List[int]] = Field(default=None)


class KeyMetrics(BaseModel):
    count_retails: int
    count_segment: int
    count_ppg: int
    roi: float
    volume_lift_pct: float
    incremental_volume: int
    total_volume: int
    investment: int
    baseline: int
    inc_rev: int


class ChartsResponse(BaseModel):
    # Pydantic config to allow arbitrary types (Plotly Figures)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    vol_vs_baseline: go.Figure
    uplift_vs_depth: go.Figure
    uplift_vs_mechanic: go.Figure
    uplift_vs_tactic: go.Figure


class PerformanceResponse(BaseModel):
    metrics: KeyMetrics
    charts: ChartsResponse
    filter_options: Dict[str, List[Any]] # To populate frontend dropdowns


# --- Main Logic Class ---

class PromotionAnalysis:

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path
        self.df_raw = self._load_and_clean_df()

    def _load_and_clean_df(self) -> pd.DataFrame:
        if not self.data_path.exists():
            # Fallback or error handling
            msg = f"Data file not found: {self.data_path}"
            logger.error(msg)
            # For testing purposes, you might raise or return empty
            raise FileNotFoundError(msg)

        df = pd.read_csv(self.data_path)

        # Promo Tactic Cleaning
        df['promo_tactic'] = np.where(df['promo_tactic'] == 'unknown', 'Display & TPR', df['promo_tactic'])
        df['promo_tactic'] = np.where(df['promo_tactic'] == 'No Tactic', 'Feature & TPR', df['promo_tactic'])
        df['segment'] = df['subsegment_name'].str.split('|').str[0]
        df['month'] = pd.to_datetime(df['start_date']).dt.month

        # Standardizing Tactics
        df['promo_tactic'] = np.where(df['promo_tactic'] == 'Feature & TPR', 'Feature', df['promo_tactic'])
        df['promo_tactic'] = np.where(df['promo_tactic'] == 'Display & TPR', 'Display', df['promo_tactic'])
        df['promo_tactic'] = np.where(df['promo_tactic'] == 'Feature Only', 'Feature', df['promo_tactic'])
        df['promo_tactic'] = np.where(df['promo_tactic'] == 'Display Only', 'Display', df['promo_tactic'])
        df['promo_tactic'] = np.where(df['promo_tactic'] == 'TPR Only', 'TPR', df['promo_tactic'])

        # Retailer Cleaning
        df['retailer'] = np.where(df['retailer'] == 'Target PT', 'Target', df['retailer'])
        df['retailer'] = np.where(df['retailer'] == 'Publix Total TA', 'Publix', df['retailer'])
        df['retailer'] = np.where(df['retailer'] == 'CVS Total Corp ex HI TA', 'CVS', df['retailer'])
        df['retailer'] = df['retailer'].apply(lambda x: x.upper())

        # ROI & Mechanics
        df['ROI'] = df['roi']
        df['offer_mechanic'] = np.where(df['offer_mechanic'] == 'unknown', 'special x off', df['offer_mechanic'])
        
        # Bins
        bins = [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
        labels = ['0%-10%', '10%-20%', '20%-30%', '30%-40%', '40%-50%', '50%-60%', '60%-70%', '70%-80%']
        df['promo_depth'] = pd.cut(df['discount'], bins=bins, labels=labels, right=False)

        # Offer Type
        df['offer_type'] = np.where(df['offer_type'] == 'unknown', 'spend_reward', df['offer_type'])
        df['offer_type'] = df['offer_type'].str.upper()
        df['offer_type'] = df['offer_type'].replace('_', ' ', regex=True)

        # Year Standardization
        df['year'] = np.where(df['year'] == 2022, 2023, df['year'])
        df['year'] = np.where(df['year'] == 2021, 2022, df['year'])

        # Date & Brand
        df['date'] = pd.to_datetime(df['year'].astype(str) + df['month'].astype(str), format='%Y%m')
        df['brand_nm'] = df['ppg_id'].str.split('|').str[2]

        return df

    def get_filter_options(self) -> Dict[str, List[Any]]:
        """Returns unique values for all filters to populate frontend."""
        return {
            "categories": ["SurfaceCare"], # Hardcoded default from script
            "brands": sorted(self.df_raw['brand_nm'].dropna().unique().tolist()),
            "segments": sorted(self.df_raw['segment'].dropna().unique().tolist()),
            "ppgs": sorted(self.df_raw['ppg_id'].dropna().unique().tolist()),
            "retailers": sorted(self.df_raw['retailer'].dropna().unique().tolist()),
            "offer_types": sorted(self.df_raw['offer_type'].dropna().unique().tolist()),
            "promo_tactics": sorted(self.df_raw['promo_tactic'].dropna().unique().tolist()),
            "years": sorted(self.df_raw['year'].dropna().unique().tolist()),
            "months": sorted(self.df_raw['month'].dropna().unique().tolist())
        }

    def _apply_filters(self, df: pd.DataFrame, filters: PromotionFilters) -> pd.DataFrame:
        df_fil = df.copy()

        # Helper to check if filter is active (not None and not "All")
        def is_active(f_val):
            return f_val is not None and len(f_val) > 0 and "All" not in f_val

        if is_active(filters.brands):
            df_fil = df_fil[df_fil['brand_nm'].isin(filters.brands)]
        
        if is_active(filters.segments):
            df_fil = df_fil[df_fil['segment'].isin(filters.segments)]
            
        if is_active(filters.ppgs):
            df_fil = df_fil[df_fil['ppg_id'].isin(filters.ppgs)]
            
        if is_active(filters.retailers):
            df_fil = df_fil[df_fil['retailer'].isin(filters.retailers)]
            
        if is_active(filters.offer_types):
            df_fil = df_fil[df_fil['offer_type'].isin(filters.offer_types)]
            
        if is_active(filters.promo_tactics):
            df_fil = df_fil[df_fil['promo_tactic'].isin(filters.promo_tactics)]
            
        if is_active(filters.years):
            df_fil = df_fil[df_fil['year'].isin(filters.years)]
            
        if is_active(filters.months):
            df_fil = df_fil[df_fil['month'].isin(filters.months)]

        return df_fil

    def _calculate_metrics(self, df: pd.DataFrame) -> KeyMetrics:
        incremental_volume = int(df["incremental_volume"].sum())
        volume = int(df["total_volume"].sum())
        investment = int(df["promo_investment"].sum())
        baseline = int(df["baseline"].sum())
        inc_rev = int(df['incr_revenue'].sum())
        
        # Avoid division by zero
        volume_lift_pct = round((((volume/baseline)-1)*100), 2) if baseline else 0.0
        roi = (inc_rev/investment)+1 if investment else 0.0
        
        return KeyMetrics(
            count_retails=df["retailer"].nunique(),
            count_segment=df["segment"].nunique(),
            count_ppg=df["ppg_id"].nunique(),
            roi=round(roi, 2),
            volume_lift_pct=volume_lift_pct,
            incremental_volume=incremental_volume,
            total_volume=volume,
            investment=investment,
            baseline=baseline,
            inc_rev=inc_rev
        )

    # --- Chart Generation Methods ---

    def _make_layout(self, fig, title, x_title, y_title, y2_title=None):
        """Helper to apply the common styling."""
        fig.update_layout(
            title_text=title, 
            plot_bgcolor='white', 
            paper_bgcolor="white",
            bargap=0.1,
            title_font=dict(size=24, family="Graphik", color='#555867'),
            bargroupgap=0.6,
            legend=dict(orientation='h', yanchor="top", y=-0.3, xanchor="center", x=0.5,
                        bgcolor='white', font=dict(size=14, family='Graphik', color='black'))
        )
        
        axis_font = dict(size=16, family='Graphik', color='black')
        tick_font = dict(size=14, family='Graphik', color='black')

        fig.update_xaxes(
            title_text=x_title, showgrid=False, showline=True, linewidth=1, 
            linecolor='black', mirror=False, title_font=axis_font, tickfont=tick_font
        )
        
        fig.update_yaxes(
            title_text=y_title, secondary_y=False, showgrid=False, showline=True, 
            linewidth=1, linecolor='black', mirror=False, title_font=axis_font, tickfont=tick_font
        )

        if y2_title:
             fig.update_yaxes(
                title_text=y2_title, secondary_y=True, showgrid=False, showline=True, 
                linewidth=1, linecolor='black', mirror=True, title_font=axis_font, tickfont=tick_font
            )
        return fig

    def _chart_vol_vs_baseline(self, df: pd.DataFrame) -> go.Figure:
        df_pl1 = df.groupby(['date'])[['baseline','total_volume']].sum().reset_index()
        df_pl1['date'] = pd.to_datetime(df_pl1['date'])
        df_pl1['date_str'] = df_pl1['date'].dt.strftime("%b %Y")
        
        baseline_color = '#1E3D7D'
        total_volume_color = '#06C480'

        trace1 = go.Line(x=df_pl1['date_str'], y=df_pl1['baseline'], name='Avg Baseline', line=dict(color=baseline_color))
        trace3 = go.Line(x=df_pl1['date_str'], y=df_pl1['total_volume'], name='Avg Total Volume', line=dict(color=total_volume_color))

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(trace1)
        fig.add_trace(trace3, secondary_y=False)
        
        # Specific X-axis formatting for this chart
        tickvals = list(range(len(df_pl1['date_str'])))
        ticktext = [text[:3] + '<br>' + text[6:] if len(text) > 3 else text for text in df_pl1['date_str']]
        
        fig.update_layout(xaxis=dict(
            tickmode='array', tickvals=tickvals, ticktext=ticktext, tickangle=0, automargin=True
        ))
        
        return self._make_layout(fig, "Total Volume Vs Baseline", "Year", "Volume")

    def _chart_uplift_vs_depth(self, df: pd.DataFrame) -> go.Figure:
        df2 = df.groupby(['promo_depth']).agg(
            {'incr_revenue':'sum','baseline':'sum', 'total_volume':'sum','promo_investment':'sum'}
        ).reset_index()
        
        # Calculations
        with np.errstate(divide='ignore', invalid='ignore'):
            df2['volume_lift_pct'] = ((df2['total_volume']/df2['baseline'])-1)*100
            df2['ROI'] = (df2['incr_revenue']/df2['promo_investment'])+1
        
        # Manual Logic from script
        df2['ROI'] = np.where(df2['promo_depth']=='60%-70%', df2['ROI'].shift(1)-0.05, df2['ROI'])
        df2['ROI'] = np.where(df2['promo_depth']=='70%-80%', df2['ROI'].shift(1)-0.1, df2['ROI'])

        trace_bar = go.Bar(x=df2['promo_depth'], y=df2['volume_lift_pct'], name='Avg Uplift %', marker=dict(color='#1E3D7D'))
        trace_line = go.Line(x=df2['promo_depth'], y=df2['ROI'], name='Avg ROI', line=dict(color='#06C480'))

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(trace_bar)
        fig.add_trace(trace_line, secondary_y=True)

        fig = self._make_layout(fig, "Uplift % Vs Discount Depth", "Promo Depth", "Uplift(%)", "Avg ROI")
        
        # Set Range
        max_roi = df2['ROI'].max() if not df2['ROI'].isna().all() else 1
        fig.update_yaxes(range=[1, 0.5 + max_roi], secondary_y=True)
        return fig

    def _chart_uplift_vs_mechanic(self, df: pd.DataFrame) -> go.Figure:
        # Filter top 5 logic
        top_offer = df.groupby('offer_mechanic')['volume_lift_pct'].mean().nlargest(5).reset_index()['offer_mechanic'].unique().tolist()
        df_mod = df.copy()
        df_mod['offer_mechanic'] = df_mod['offer_mechanic'].apply(lambda x: x if x in top_offer else 'Buy 5 get 2 free')

        df3 = df_mod.groupby(['offer_mechanic']).agg(
            {'incr_revenue':'sum','baseline':'sum','total_volume':'sum','promo_investment':'sum'}
        ).reset_index()

        with np.errstate(divide='ignore', invalid='ignore'):
            df3['volume_lift_pct'] = ((df3['total_volume']/df3['baseline'])-1)*100
            df3['ROI'] = (df3['incr_revenue']/df3['promo_investment'])+1

        trace_bar = go.Bar(x=df3['offer_mechanic'], y=df3['volume_lift_pct'], name='Avg Uplift %', marker=dict(color='#1E3D7D'))
        trace_line = go.Line(x=df3['offer_mechanic'], y=df3['ROI'], name='Avg ROI', line=dict(color='#06C480'))

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(trace_bar)
        fig.add_trace(trace_line, secondary_y=True)

        fig = self._make_layout(fig, "Uplift % Vs Offer Mechanic", "Offer Mechanic", "Uplift(%)", "Avg ROI")
        
        max_roi = df3['ROI'].max() if not df3['ROI'].isna().all() else 1
        fig.update_yaxes(range=[1, 0.5 + max_roi], secondary_y=True)
        return fig

    def _chart_uplift_vs_tactic(self, df: pd.DataFrame) -> go.Figure:
        df3 = df.groupby(['promo_tactic']).agg(
            {'incr_revenue':'sum','baseline':'sum','total_volume':'sum','promo_investment':'sum'}
        ).reset_index()

        with np.errstate(divide='ignore', invalid='ignore'):
            df3['volume_lift_pct'] = ((df3['total_volume']/df3['baseline'])-1)*100
            df3['ROI'] = (df3['incr_revenue']/df3['promo_investment'])+1

        # Custom Ordering
        custom_order = ['TPR', 'Display', 'Feature', 'Feature & Display']
        df3['promo_tactic'] = pd.Categorical(df3['promo_tactic'], categories=custom_order, ordered=True)
        df3 = df3.sort_values(by='promo_tactic').reset_index(drop=True)

        # Custom Sorting Logic (Bubble sort logic from original script)
        # Ensure we have enough rows to avoid index errors
        if len(df3) >= 4:
            if df3.at[3, 'volume_lift_pct'] < df3.at[2, 'volume_lift_pct']:
                df3.iloc[[2, 3]] = df3.iloc[[3, 2]].values
            
            if df3.at[1, 'volume_lift_pct'] < df3.at[0, 'volume_lift_pct']:
                df3.iloc[[0, 1]] = df3.iloc[[1, 0]].values
                
            if df3.at[2, 'volume_lift_pct'] < df3.at[0, 'volume_lift_pct']:
                df3.iloc[[0, 2]] = df3.iloc[[2, 0]].values

        trace_bar = go.Bar(x=df3['promo_tactic'], y=df3['volume_lift_pct'], name='Avg Uplift %', marker=dict(color='#1E3D7D'))
        trace_line = go.Line(x=df3['promo_tactic'], y=df3['ROI'], name='Avg ROI', line=dict(color='#06C480'))

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(trace_bar)
        fig.add_trace(trace_line, secondary_y=True)

        fig = self._make_layout(fig, "Uplift % Vs Promo Tactic", "Promo Tactic", "Uplift(%)", "Avg ROI")
        
        max_roi = df3['ROI'].max() if not df3['ROI'].isna().all() else 1
        fig.update_yaxes(range=[1, 0.5 + max_roi], secondary_y=True)
        return fig

    # --- Public API ---

    def run_analysis(self, filters: PromotionFilters) -> PerformanceResponse:
        """
        Main method to call from the frontend.
        Applies filters, calculates metrics, generates charts, and returns a structured response.
        """
        df_filtered = self._apply_filters(self.df_raw, filters)

        metrics = self._calculate_metrics(df_filtered)
        
        charts = ChartsResponse(
            vol_vs_baseline=self._chart_vol_vs_baseline(df_filtered),
            uplift_vs_depth=self._chart_uplift_vs_depth(df_filtered),
            uplift_vs_mechanic=self._chart_uplift_vs_mechanic(df_filtered),
            uplift_vs_tactic=self._chart_uplift_vs_tactic(df_filtered)
        )

        return PerformanceResponse(
            metrics=metrics,
            charts=charts,
            filter_options=self.get_filter_options()
        )