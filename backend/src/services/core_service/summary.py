from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import warnings

warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from src.utility.logger import AppLogger

# repo root -> .../RGM_Dasboard
ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "final_pricing_consolidated_file.csv"
logger = AppLogger.get_logger(__name__)


class SummaryFilters(BaseModel):
    # categories: Optional[List[str]] = Field(default=None, description="Category filter")
    manufacturers: Optional[List[str]] = Field(
        default=None, description="Manufacturer names (None or empty = all)"
    )
    retailers: Optional[List[str]] = Field(
        default=None, description="Retailer ids (None or empty = all)"
    )
    time_periods: Optional[List[str]] = Field(
        default=None,
        description="Year/H1/H2/Q1/Q2/Q3/Q4 (e.g., '2023', '2023 H1', '2023 Q2')",
    )


class KPI(BaseModel):
    label: str
    value: float


class RevenueShareEntry(BaseModel):
    manufacturer: str
    fair_share: float
    revenue_share: float


class SeriesPoint(BaseModel):
    period: str
    value: float


class RevenueSeries(BaseModel):
    manufacturer: str
    points: List[SeriesPoint]


class RevenueTable(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    value_unit: str = "M"


class RetailerRevenueShare(BaseModel):
    retailer_id: str
    rev_share_retailer: float
    rev_share_retailer_fair_share: float
    revenue_share: float
    revenue_share_label: float


class SummaryResponse(BaseModel):
    assessment_period: str
    kpis: List[KPI]
    fair_share_vs_revenue: List[RevenueShareEntry]
    revenue_by_manufacturer: List[RevenueSeries]
    revenue_table: RevenueTable
    revenue_by_retailer_table: RevenueTable
    revenue_by_retailer_chart: RevenueTable
    revenue_by_retailer: List[RetailerRevenueShare]


class FilterOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    manufacturers: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)
    time_periods: List[str] = Field(default_factory=list)


class Summary:
    """
    Pure-Python summary transformer. Reads the consolidated pricing file,
    applies filters, and returns chart-ready payloads for the frontend.
    """

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path

    def load_dataframe(self) -> pd.DataFrame:
        if not self.data_path.exists():
            msg = f"Data file not found: {self.data_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        data = pd.read_csv(self.data_path, low_memory=False)
        df = data.copy()

        retailer_map = {
            "Target PT": "Target",
            "Publix TOTAL TA": "Publix",
            "CVS TOTAL Corp ex HI TA": "CVS",
        }
        df["retailer_id"] = df["retailer_id"].replace(retailer_map).str.upper()
        df = df.dropna()

        df["year"] = pd.to_datetime(df["year"].astype(str), format="%Y").dt.strftime(
            "%Y"
        )
        df["year"] = np.where(df["year"] == "2022", "2023", df["year"])
        df["year"] = np.where(df["year"] == "2021", "2022", df["year"])
        df["day"] = 1
        df["month_name"] = df["month"].map(
            {
                1: "Jan",
                2: "Feb",
                3: "Mar",
                4: "Apr",
                5: "May",
                6: "Jun",
                7: "Jul",
                8: "Aug",
                9: "Sep",
                10: "Oct",
                11: "Nov",
                12: "Dec",
            }
        )
        month_order = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        df["month_name"] = pd.Categorical(
            df["month_name"], categories=month_order, ordered=True
        )
        return df

    @staticmethod
    def _subset_for_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
        if " " not in period:
            return df[df["year"] == period].assign(time_period=period)

        year, bucket = period.split(" ", 1)
        if bucket.upper() in {"H1", "H2"}:
            months = list(range(1, 7)) if bucket.upper() == "H1" else list(range(7, 13))
        elif bucket.upper().startswith("Q"):
            quarter = int(bucket[1])
            start = (quarter - 1) * 3 + 1
            months = [start, start + 1, start + 2]
        else:
            return df[df["year"] == year].assign(time_period=period)

        return df[(df["year"] == year) & (df["month"].isin(months))].assign(
            time_period=period
        )

    def _format_number(self, n):
        if n is None:
            return None
        if n >= 1_000_000:
            return f"{n/1_000_000:.2f}M"
        elif n >= 1_000:
            return f"{n/1_000:.2f}K"
        else:
            return f"{n:.2f}"

    def _apply_filters(
        self, df: pd.DataFrame, filters: SummaryFilters
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Returns:
            df_filtered: dataframe with all filters applied (used for most payloads)
            df_fair_share: dataframe with retailer/time filters applied (no manufacturer filter)
            df_fair_share_original: dataframe with only time filters applied (baseline for fair share)
        """
        df_base = df.copy()

        # if filters.categories and "category" in df_filtered.columns:
        #     df_filtered = df_filtered[df_filtered["category"].isin(filters.categories)]
        # elif filters.categories:
        #     logger.warning(
        #         "Category filter provided but 'category' column not found; skipping category filter."
        #     )

        if filters.retailers:
            selected = [] if "All" in filters.retailers else filters.retailers
            if selected:
                df_base = df_base[df_base["retailer_id"].isin(selected)]

        time_periods = (
            None
            if not filters.time_periods or "All" in filters.time_periods
            else filters.time_periods
        )

        if time_periods:
            df_fair_share = pd.concat(
                [self._subset_for_period(df_base, p) for p in time_periods],
                ignore_index=True,
            )
            df_fair_share_original = pd.concat(
                [self._subset_for_period(df, p) for p in time_periods],
                ignore_index=True,
            )
        else:
            df_fair_share = df_base.assign(time_period=df_base["year"])
            df_fair_share_original = df.assign(time_period=df["year"])

        df_filtered = df_fair_share.copy()
        if filters.manufacturers:
            selected = [] if "All" in filters.manufacturers else filters.manufacturers
            if selected:
                df_filtered = df_filtered[df_filtered["manufacturer_nm"].isin(selected)]

        return df_filtered, df_fair_share, df_fair_share_original

    @staticmethod
    def _assessment_period(df_filtered: pd.DataFrame) -> str:
        if df_filtered.empty:
            return "No data"
        min_year = df_filtered["year"].min()
        max_year = df_filtered["year"].max()
        month_min = df_filtered["month"].min()
        month_max = df_filtered["month"].max()
        start = df_filtered[df_filtered["month"] == month_min].iloc[0]
        end = df_filtered[df_filtered["month"] == month_max].iloc[0]
        return f"{start['month_name']} {min_year} - {end['month_name']} {max_year}"

    @staticmethod
    def _kpis(df_filtered: pd.DataFrame) -> List[KPI]:
        return [
            KPI(
                label="Manufacturer Count",
                value=int(df_filtered["manufacturer_nm"].nunique()),
            ),
            KPI(label="Brand Count", value=int(df_filtered["brand_nm"].nunique())),
            KPI(
                label="Retailer Count", value=int(df_filtered["retailer_id"].nunique())
            ),
            KPI(label="PPG Count", value=int(df_filtered["ppg_nm"].nunique())),
        ]

    @staticmethod
    def _fair_share(
        df_filtered: pd.DataFrame,
        baseline: pd.DataFrame,
        manufacturers_filter: Optional[List[str]] = None,
    ) -> List[RevenueShareEntry]:
        if df_filtered.empty or baseline.empty:
            return []

        rev_filtered = (
            df_filtered.groupby("manufacturer_nm")["revenue"].sum().rename("revenue")
        )
        rev_baseline = (
            baseline.groupby("manufacturer_nm")["revenue"].sum().rename("revenue_fair")
        )
        total_filtered = rev_filtered.sum() or 1
        total_baseline = rev_baseline.sum() or 1

        merged = (
            pd.concat([rev_filtered, rev_baseline], axis=1).fillna(0.0).reset_index()
        )
        merged["revenue_share"] = (merged["revenue"] / total_filtered) * 100
        merged["fair_share"] = (merged["revenue_fair"] / total_baseline) * 100

        if manufacturers_filter:
            selected = [m for m in manufacturers_filter if m != "All"]
            if selected:
                merged = merged[merged["manufacturer_nm"].isin(selected)]

        merged = merged.sort_values("revenue_share", ascending=True)

        return [
            RevenueShareEntry(
                manufacturer=row["manufacturer_nm"],
                fair_share=round(float(row["fair_share"]), 2),
                revenue_share=round(float(row["revenue_share"]), 2),
            )
            for _, row in merged.iterrows()
        ]

    @staticmethod
    def _revenue_series(df_filtered: pd.DataFrame) -> List[RevenueSeries]:
        if df_filtered.empty:
            return []
        period_col = "time_period" if "time_period" in df_filtered.columns else "year"
        df_mod = (
            df_filtered.assign(revenue=lambda d: d["revenue"] / 1e6)
            .groupby(["manufacturer_nm", period_col])["revenue"]
            .sum()
            .reset_index()
            .round(2)
        )
        series: List[RevenueSeries] = []
        for manufacturer, group in df_mod.groupby("manufacturer_nm"):
            points = [
                SeriesPoint(period=row[period_col], value=float(row["revenue"]))
                for _, row in group.sort_values(period_col).iterrows()
            ]
            series.append(RevenueSeries(manufacturer=manufacturer, points=points))
        return series

    @staticmethod
    def _revenue_table(df_filtered: pd.DataFrame) -> RevenueTable:
        if df_filtered.empty:
            return RevenueTable(columns=[], rows=[], value_unit="M")

        period_col = "time_period" if "time_period" in df_filtered.columns else "year"
        df_mod = (
            df_filtered.assign(revenue=lambda d: d["revenue"] / 1e6)
            .groupby(["manufacturer_nm", period_col])["revenue"]
            .sum()
            .reset_index()
            .round(2)
        )

        pivot = df_mod.pivot_table(
            index="manufacturer_nm", columns=period_col, values="revenue", fill_value=0
        )
        pivot = pivot.sort_index(axis=1)
        periods = pivot.columns.tolist()

        for i in range(len(periods) - 1):
            left, right = periods[i], periods[i + 1]
            pct_change = ((pivot[right] / pivot[left].replace(0, np.nan)) - 1) * 100
            pivot[f"%Change {right}"] = pct_change.replace([np.inf, -np.inf], np.nan)

        pivot = pivot.reset_index().rename(columns={"manufacturer_nm": "Manufacturer"})

        rows = []
        for _, row in pivot.iterrows():
            row_dict: Dict[str, float] = {"Manufacturer": row["Manufacturer"]}
            for col in pivot.columns[1:]:
                val = row[col]
                if pd.isna(val):
                    continue
                row_dict[col] = round(float(val), 2)
            rows.append(row_dict)

        columns = ["Manufacturer"] + [c for c in pivot.columns[1:]]
        return RevenueTable(columns=columns, rows=rows, value_unit="M")

    @staticmethod
    def build_options(df: pd.DataFrame) -> FilterOptions:
        categories = (
            df["category"].dropna().unique().tolist()
            if "category" in df.columns
            else ["SurfaceCare"]
        )
        manufacturers = sorted(df["manufacturer_nm"].dropna().unique().tolist())
        brands = (
            sorted(df["brand_nm"].dropna().unique().tolist())
            if "brand_nm" in df.columns
            else []
        )
        ppgs = (
            sorted(df["ppg_nm"].dropna().unique().tolist())
            if "ppg_nm" in df.columns
            else []
        )
        retailers = sorted(df["retailer_id"].dropna().unique().tolist())

        years = sorted(df["year"].astype(str).unique().tolist())
        time_periods: List[str] = []
        for year in years:
            time_periods.append(year)
            time_periods.append(f"{year} H1")
            time_periods.append(f"{year} H2")
            time_periods.extend(
                [f"{year} Q1", f"{year} Q2", f"{year} Q3", f"{year} Q4"]
            )
        return FilterOptions(
            categories=categories,
            manufacturers=manufacturers,
            brands=brands,
            ppgs=ppgs,
            retailers=retailers,
            time_periods=time_periods,
        )

    def _revenue_by_retailer_table(
        self, df: pd.DataFrame, filters: SummaryFilters
    ) -> RevenueTable:
        period_col = "time_period" if "time_period" in df.columns else "year"

        def _period_order(val: Any) -> int:
            """
            Provides a sortable integer for periods (year, H1/H2, Q1-Q4).
            Falls back to string ordering when unrecognized.
            """
            try:
                # plain year like "2022"
                if isinstance(val, (int, float)) or (
                    isinstance(val, str) and val.isdigit()
                ):
                    year_int = int(val)
                    return year_int * 100
                if isinstance(val, str) and " " in val:
                    year_str, bucket = val.split(" ", 1)
                    year_int = int(year_str)
                    b = bucket.upper()
                    if b == "H1":
                        return year_int * 100 + 1
                    if b == "H2":
                        return year_int * 100 + 7
                    if b.startswith("Q") and len(b) == 2 and b[1].isdigit():
                        q = int(b[1])
                        start_month = (q - 1) * 3 + 1
                        return year_int * 100 + start_month
                # fallback
                return hash(val) % 10_000_000
            except Exception:
                return hash(val) % 10_000_000

        # Aggregate revenue by retailer/period
        df_mod = df.groupby(["retailer_id", period_col])["revenue"].sum().reset_index()

        # Identify top retailers based on total revenue (across periods)
        top_retailers = (
            df_mod.groupby("retailer_id")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(4)
            .index.tolist()
        )
        df_mod_5 = df_mod[df_mod["retailer_id"].isin(top_retailers)]
        df_mod_other = df_mod[~df_mod["retailer_id"].isin(top_retailers)]

        if not df_mod_other.empty:
            df_mod_other = (
                df_mod_other.groupby([period_col])["revenue"]
                .sum()
                .reset_index()
                .assign(retailer_id="OTHERS")
                .drop_duplicates()
            )

        df_mod = pd.concat([df_mod_5, df_mod_other], axis=0, ignore_index=True)

        # Only compute % change when working with year buckets; otherwise leave NaN
        df_mod["_period_order"] = df_mod[period_col].apply(_period_order)
        if df_mod[period_col].nunique() > 1:
            df_mod["%Change"] = (
                df_mod.sort_values(["retailer_id", "_period_order"])
                .groupby("retailer_id")["revenue"]
                .pct_change()
                * 100
            )

        dfn = df_mod.copy()
        if "%Change" not in dfn.columns:
            dfn["%Change"] = np.nan
        dfn.loc[:, "%Change"] = dfn["%Change"].round(2)
        change_df = (
            dfn.sort_values(["retailer_id", "_period_order"])
            .groupby("retailer_id")["%Change"]
            .last()
            .reset_index()
        )

        pivot_chart = df_mod.pivot_table(
            index="retailer_id",
            columns=period_col,
            values="revenue",
            aggfunc="sum",
        ).reset_index()
        period_cols = [c for c in pivot_chart.columns if c != "retailer_id"]
        period_cols = sorted(period_cols, key=_period_order)
        pivot_chart = pivot_chart[["retailer_id"] + period_cols]

        # Build table copy with % change between consecutive periods
        pivot_table = pivot_chart.copy()
        change_cols: List[str] = []
        for i in range(len(period_cols) - 1):
            left, right = period_cols[i], period_cols[i + 1]
            change_col = f"%Change {right}"
            pct_change = (
                pivot_table[right] / pivot_table[left].replace(0, np.nan) - 1
            ) * 100
            pivot_table[change_col] = pct_change.replace([np.inf, -np.inf], np.nan)
            change_cols.append(change_col)

        pivot_formatted = pivot_table.copy()
        for col in period_cols:
            pivot_formatted[col] = pivot_formatted[col].apply(
                lambda x: self._format_number(x) if isinstance(x, (int, float)) else x
            )
        for col in change_cols:
            pivot_formatted[col] = pivot_formatted[col].round(2)

        pivot_formatted.columns = ["retailer_id"] + [
            str(c) for c in pivot_formatted.columns[1:]
        ]
        # Guard against accidental duplicate column labels before merging
        pivot_formatted = pivot_formatted.loc[:, ~pivot_formatted.columns.duplicated()]
        change_df = change_df.loc[:, ~change_df.columns.duplicated()]
        pivots = pd.merge(pivot_formatted, change_df, on="retailer_id", how="left")
        if "%Change" in pivots.columns:
            pivots = pivots.drop(columns=["%Change"])

        records = pivots.to_dict(orient="records")
        records_chart = pivot_chart.to_dict(orient="records")
        columns = pivots.columns.values
        col_chart = pivot_chart.columns.values
        resp = RevenueTable(columns=columns, rows=records, value_unit="M")
        resp_chart = RevenueTable(columns=col_chart, rows=records_chart, value_unit="M")
        return resp, resp_chart

    def _revenue_by_retailer(
        self,
        df_time_filtered: pd.DataFrame,
        manufacturers_filter: Optional[List[str]] = None,
        retailers_filter: Optional[List[str]] = None,
    ):
        """
        revenue share uses selected manufacturers (if any)
        but not the retailer filter; fair share uses full baseline with only time filters.
        """
        if df_time_filtered.empty:
            return []

        # Revenue share pool: time-filtered + optional manufacturer filter, no retailer filter
        rev_pool = df_time_filtered.copy()
        if manufacturers_filter:
            selected = [m for m in manufacturers_filter if m != "All"]
            if selected:
                rev_pool = rev_pool[rev_pool["manufacturer_nm"].isin(selected)]

        final_df = pd.DataFrame()
        total_rev = rev_pool["revenue"].sum() or 1
        for retailer in rev_pool["retailer_id"].unique():
            temp = rev_pool[rev_pool["retailer_id"] == retailer]
            temp["rev_share_retailer"] = (sum(temp["revenue"]) / total_rev) * 100
            final_df = pd.concat([final_df, temp], axis=0)

        # Fair share baseline: time-filtered only (no manufacturer filter)
        baseline = df_time_filtered.copy()
        total_baseline = baseline["revenue"].sum() or 1
        final_df2 = pd.DataFrame()
        for retailer in baseline["retailer_id"].unique():
            temp = baseline[baseline["retailer_id"] == retailer]
            temp["rev_share_retailer"] = (sum(temp["revenue"]) / total_baseline) * 100
            final_df2 = pd.concat([final_df2, temp], axis=0)

        if retailers_filter:
            selected_retailers = [r for r in retailers_filter if r != "All"]
            if selected_retailers:
                final_df = final_df[final_df["retailer_id"].isin(selected_retailers)]

        final_df2 = final_df2[["retailer_id", "rev_share_retailer"]].drop_duplicates()
        final_df2.columns = ["retailer_id", "rev_share_retailer_fair_share"]

        final_df = pd.merge(final_df, final_df2, on=["retailer_id"], how="left")
        df_mod = (
            final_df.groupby(["retailer_id"])[
                ["rev_share_retailer", "rev_share_retailer_fair_share"]
            ]
            .mean()
            .reset_index()
        )
        df_mod["revenue_share"] = df_mod["rev_share_retailer"]
        df_mod["revenue_share"] = df_mod["revenue_share"].round(2)
        df_mod = df_mod.sort_values(by="revenue_share", ascending=False)
        df_mod_5 = df_mod[
            df_mod["retailer_id"].isin(df_mod.head(4)["retailer_id"].unique().tolist())
        ]
        df_mod_other = df_mod[
            ~(
                df_mod["retailer_id"].isin(
                    df_mod.head(4)["retailer_id"].unique().tolist()
                )
            )
        ]

        df_mod_other.loc[:, "rev_share_retailer"] = df_mod_other[
            "rev_share_retailer"
        ].sum()
        df_mod_other.loc[:, "rev_share_retailer_fair_share"] = df_mod_other[
            "rev_share_retailer_fair_share"
        ].sum()
        df_mod_other.loc[:, "revenue_share"] = df_mod_other["revenue_share"].sum()
        df_mod_other.loc[:, "retailer_id"] = "OTHERS"
        df_mod_other = df_mod_other.drop_duplicates()
        df_mod = pd.concat([df_mod_5, df_mod_other], axis=0)
        df_mod = df_mod.sort_values("revenue_share")
        df_mod["revenue_share_label"] = df_mod["revenue_share"].round(2)
        df_mod_records = df_mod.to_dict(orient="records")
        retailer_share_list = [RetailerRevenueShare(**row) for row in df_mod_records]
        return retailer_share_list

    def build_summary(self, filters: SummaryFilters) -> SummaryResponse:
        df = self.load_dataframe()
        df_filtered, df_fair_share, df_fair_share_original = self._apply_filters(
            df, filters
        )
        assessment_period = self._assessment_period(df_filtered)
        kpis = self._kpis(df_filtered)
        fair_share_vs_revenue = self._fair_share(
            df_fair_share, df_fair_share_original, filters.manufacturers
        )
        revenue_by_manufacturer = self._revenue_series(df_filtered)
        revenue_table = self._revenue_table(df_filtered)
        revenue_by_retailer_table, revenue_chart = self._revenue_by_retailer_table(
            df_filtered, filters.time_periods
        )
        retailer_share_list = self._revenue_by_retailer(
            df_fair_share_original, filters.manufacturers, filters.retailers
        )
        logger.info(
            "Built summary payload | rows=%s filtered=%s",
            len(df),
            len(df_filtered),
        )

        return SummaryResponse(
            assessment_period=assessment_period,
            kpis=kpis,
            fair_share_vs_revenue=fair_share_vs_revenue,
            revenue_by_manufacturer=revenue_by_manufacturer,
            revenue_table=revenue_table,
            revenue_by_retailer_table=revenue_by_retailer_table,
            revenue_by_retailer_chart=revenue_chart,
            revenue_by_retailer=retailer_share_list,
        )
