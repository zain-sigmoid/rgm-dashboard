# backend/src/services/core_service/descriptive_service.py
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import plotly.graph_objects as go

from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[3]
CSV_PATH = ROOT_DIR / "data" / "final_pricing_consolidated_file.csv"

def load_and_clean_csv(path: Optional[str] = None) -> pd.DataFrame:
    p = path or CSV_PATH
    df = pd.read_csv(p)
    df = df.dropna(how='all')
    # retailer normalization
    if 'retailer_id' in df.columns:
        df['retailer_id'] = df['retailer_id'].astype(str).str.upper()
        df['retailer_id'] = np.where(df['retailer_id']=='TARGET PT','TARGET',df['retailer_id'])
        df['retailer_id'] = np.where(df['retailer_id']=='PUBLIX TOTAL TA','PUBLIX',df['retailer_id'])
        df['retailer_id'] = np.where(df['retailer_id']=='CVS TOTAL CORP EX HI TA','CVS',df['retailer_id'])
    # year/date parse
    if 'year' in df.columns:
        try:
            df['year'] = pd.to_datetime(df['year'].astype(str), errors='coerce').dt.strftime("%Y")
        except Exception:
            df['year'] = df['year'].astype(str)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        if 'year' in df.columns and 'month' in df.columns:
            def build_date(r):
                try:
                    return pd.Timestamp(year=int(r['year']), month=int(r['month']), day=1)
                except Exception:
                    return pd.NaT
            df['date'] = df.apply(build_date, axis=1)
    for col in ['volume', 'revenue', 'price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    df_fil = df.copy()
    if not filters:
        return df_fil
    if filters.get('ppg'):
        df_fil = df_fil[df_fil['ppg_nm'].isin(filters['ppg'])]
    if filters.get('retailer'):
        rlist = [r.upper() for r in filters['retailer']]
        df_fil = df_fil[df_fil['retailer_id'].isin(rlist)]
    if filters.get('year'):
        df_fil = df_fil[df_fil['year'].isin(filters['year'])]
    if filters.get('month'):
        try:
            months_int = [int(m) for m in filters['month']]
            df_fil = df_fil[df_fil['date'].dt.month.isin(months_int)]
        except Exception:
            df_fil = df_fil[df_fil['date'].dt.month.astype(str).isin(filters['month'])]
    return df_fil

def compute_descriptive(filters: Dict[str, Any]) -> Dict[str, Any]:
    df = load_and_clean_csv()
    df_fil = apply_filters(df, filters)

    if df_fil.shape[0] == 0:
        return {"timeseries": [], "top_table": [], "fig": None, "row_count": 0}

    date_freq = filters.get('date_freq', 'M')
    df_ts = df_fil.set_index('date').resample(date_freq).agg({'volume': 'sum', 'revenue': 'sum'}).reset_index()
    df_ts['date'] = df_ts['date'].dt.strftime('%Y-%m-%d')
    timeseries = df_ts.to_dict(orient='records')

    top_n = int(filters.get('top_n', 10))
    if 'sku' in df_fil.columns:
        top_table_df = df_fil.groupby(['sku', 'ppg_nm']).agg({'volume': 'sum', 'revenue': 'sum'}).reset_index()
        top_table_df = top_table_df.sort_values(by='revenue', ascending=False).head(top_n)
    else:
        top_table_df = df_fil.groupby(['ppg_nm']).agg({'volume': 'sum', 'revenue': 'sum'}).reset_index().sort_values(by='revenue', ascending=False).head(top_n)
    top_table = top_table_df.to_dict(orient='records')

    # Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_ts['date'], y=df_ts['volume'], name='Volume', yaxis='y1'))
    fig.add_trace(go.Scatter(x=df_ts['date'], y=df_ts['revenue'], name='Revenue', yaxis='y2', mode='lines'))
    fig.update_layout(
        title="Volume and Revenue over time",
        xaxis=dict(title='Date'),
        yaxis=dict(title='Volume'),
        yaxis2=dict(title='Revenue', overlaying='y', side='right'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    fig_json = fig.to_dict()

    return {"timeseries": timeseries, "top_table": top_table, "fig": fig_json, "row_count": int(df_fil.shape[0])}
