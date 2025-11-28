# backend/src/services/core_service/contribution_service.py
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go

ROOT_DIR = Path(__file__).resolve().parents[3]
CSV_PATH = ROOT_DIR / "data" / "final_pricing_consolidated_file.csv"

def load_and_clean_csv(path: Optional[str] = None) -> pd.DataFrame:
    """
    Load CSV and perform light cleaning shared across analytical endpoints.
    Mirror the cleaning used in other services to keep parity.
    """
    p = path or CSV_PATH
    df = pd.read_csv(p)
    df = df.dropna(how='all')

    # Standardize retailer labels if present
    if "retailer_id" in df.columns:
        df['retailer_id'] = df['retailer_id'].astype(str).str.upper()
        df['retailer_id'] = np.where(df['retailer_id'] == 'TARGET PT', 'TARGET', df['retailer_id'])
        df['retailer_id'] = np.where(df['retailer_id'] == 'PUBLIX TOTAL TA', 'PUBLIX', df['retailer_id'])
        df['retailer_id'] = np.where(df['retailer_id'] == 'CVS TOTAL CORP EX HI TA', 'CVS', df['retailer_id'])

    # year/date parse like descriptive service
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
    """
    Apply basic filters: ppg, retailer, year, month, maybe sku.
    The frontend should send lists for these keys or None to skip.
    """
    df_f = df.copy()
    if not filters:
        return df_f

    if filters.get('ppg'):
        df_f = df_f[df_f['ppg_nm'].isin(filters['ppg'])]
    if filters.get('retailer'):
        rlist = [r.upper() for r in filters['retailer']]
        df_f = df_f[df_f['retailer_id'].isin(rlist)]
    if filters.get('year'):
        df_f = df_f[df_f['year'].isin(filters['year'])]
    if filters.get('month'):
        try:
            months_int = [int(m) for m in filters['month']]
            df_f = df_f[df_f['date'].dt.month.isin(months_int)]
        except Exception:
            df_f = df_f[df_f['date'].dt.month.astype(str).isin(filters['month'])]
    if filters.get('sku'):
        df_f = df_f[df_f['sku'].isin(filters['sku'])]
    return df_f

def compute_contribution(df: pd.DataFrame,
                         group_by: str = "ppg_nm",
                         metric: str = "revenue",
                         top_n: int = 10,
                         include_other: bool = True) -> Dict[str, Any]:
    """
    Compute contribution breakdown:
     - aggregate by group_by, sum metric & volume
     - compute contribution percent and cumulative contribution
     - optionally return timeseries for top contributors
    Returns a dict: { table: [...], fig: fig_dict, by_time: [...], row_count: int }
    """
    if group_by not in df.columns:
        raise ValueError(f"group_by column '{group_by}' not in dataframe")

    if metric not in df.columns:
        raise ValueError(f"metric column '{metric}' not in dataframe")

    # Aggregate to get totals per group
    agg = df.groupby(group_by).agg({metric: "sum", "volume": "sum"}).reset_index()
    total_metric = agg[metric].sum()
    # If total is zero, avoid div by zero
    if total_metric == 0:
        agg['contribution_pct'] = 0.0
    else:
        agg['contribution_pct'] = agg[metric] / total_metric * 100.0
    agg = agg.sort_values(by=metric, ascending=False).reset_index(drop=True)
    agg['cumulative_pct'] = agg['contribution_pct'].cumsum()

    # Top N and optionally 'Other' bucket
    top_n = int(top_n) if top_n else 10
    top_df = agg.head(top_n).copy()
    other_df = agg.iloc[top_n:].copy()
    if include_other and not other_df.empty:
        other_row = {
            group_by: "Other",
            metric: float(other_df[metric].sum()),
            "volume": float(other_df['volume'].sum()),
            "contribution_pct": float(other_df['contribution_pct'].sum()),
            "cumulative_pct": float(100.0)  # since Other completes to ~100
        }
        top_df = pd.concat([top_df, pd.DataFrame([other_row])], ignore_index=True)

    # Prepare table serializable
    table = top_df[[group_by, metric, "volume", "contribution_pct", "cumulative_pct"]].to_dict(orient='records')

    # Build a Plotly bar chart for contribution
    x = top_df[group_by].astype(str).tolist()
    y = top_df[metric].tolist()
    y_pct = top_df['contribution_pct'].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y, name=metric, yaxis='y1'))
    fig.add_trace(go.Scatter(x=x, y=y_pct, name='Contribution %', yaxis='y2', mode='lines+markers'))

    fig.update_layout(
        title=f"Contribution by {group_by} ({metric})",
        xaxis=dict(title=group_by),
        yaxis=dict(title=metric, side='left'),
        yaxis2=dict(title='Contribution %', overlaying='y', side='right', rangemode='tozero'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=40, r=40, t=60, b=80)
    )

    # Optionally compute contribution over time for the top groups (time-series)
    # We'll do monthly aggregation for the top groups (excluding Other)
    top_groups = top_df[group_by].tolist()
    # if 'Other' in top_groups remove it before time series breakdown
    if "Other" in top_groups:
        top_groups_no_other = [g for g in top_groups if g != "Other"]
    else:
        top_groups_no_other = top_groups

    by_time = []
    if df['date'].notnull().any() and len(top_groups_no_other) > 0:
        df_time = df[df[group_by].isin(top_groups_no_other)].copy()
        if df_time.empty:
            by_time = []
        else:
            df_time = df_time.set_index('date').groupby([pd.Grouper(freq='M'), group_by]).agg({metric: 'sum'}).reset_index()
            # pivot so each group becomes a column
            pivot = df_time.pivot(index='date', columns=group_by, values=metric).fillna(0)
            pivot = pivot.reset_index()
            # format date
            pivot['date'] = pivot['date'].dt.strftime('%Y-%m-%d')
            by_time = pivot.to_dict(orient='records')

    result = {
        "table": table,
        "fig": fig.to_dict(),
        "by_time": by_time,
        "row_count": int(df.shape[0])
    }
    return result
