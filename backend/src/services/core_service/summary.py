from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

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


class RetailerRevenueItem(BaseModel):
    retailer_id: str
    year: str  # or int if you prefer
    revenue: float


class RetailerRevenue(BaseModel):
    items: List[Dict[str, Any]]  # {retailer_id, "2022", "2023", ...}
    value_unit: str = "M"


class SummaryResponse(BaseModel):
    assessment_period: str
    kpis: List[KPI]
    fair_share_vs_revenue: List[RevenueShareEntry]
    revenue_by_manufacturer: List[RevenueSeries]
    revenue_table: RevenueTable
    revenue_by_retailer: RetailerRevenue


class FilterOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    manufacturers: List[str] = Field(default_factory=list)
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

    def _apply_filters(
        self, df: pd.DataFrame, filters: SummaryFilters
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_filtered = df.copy()

        # if filters.categories and "category" in df_filtered.columns:
        #     df_filtered = df_filtered[df_filtered["category"].isin(filters.categories)]
        # elif filters.categories:
        #     logger.warning(
        #         "Category filter provided but 'category' column not found; skipping category filter."
        #     )

        if filters.retailers:
            selected = [] if "All" in filters.retailers else filters.retailers
            if selected:
                df_filtered = df_filtered[df_filtered["retailer_id"].isin(selected)]

        baseline = df_filtered.copy()

        if filters.time_periods:
            if "All" in filters.time_periods:
                filters.time_periods = None
            else:
                parts = [
                    self._subset_for_period(df_filtered, p)
                    for p in filters.time_periods
                ]
                df_filtered = pd.concat(parts, ignore_index=True)
                baseline = pd.concat(
                    [self._subset_for_period(df, p) for p in filters.time_periods],
                    ignore_index=True,
                )
        else:
            df_filtered = df_filtered.assign(time_period=df_filtered["year"])
            baseline = df.assign(time_period=df["year"])

        if filters.manufacturers:
            selected = [] if "All" in filters.manufacturers else filters.manufacturers
            if selected:
                df_filtered = df_filtered[df_filtered["manufacturer_nm"].isin(selected)]

        return df_filtered, baseline

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
        df_filtered: pd.DataFrame, baseline: pd.DataFrame
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
            else []
        )
        manufacturers = sorted(df["manufacturer_nm"].dropna().unique().tolist())
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
            retailers=retailers,
            time_periods=time_periods,
        )

    def revenue_by_retailer(self, df: pd.DataFrame) -> List[RetailerRevenue]:
        df_mod = df.groupby(["retailer_id", "year"])["revenue"].sum().reset_index()
        df_mod = df_mod.sort_values(by=["revenue", "year"], ascending=False)
        df_mod_5 = df_mod[
            df_mod["retailer_id"].isin(df_mod.head(8)["retailer_id"].unique().tolist())
        ]
        df_mod_other = df_mod[
            ~(
                df_mod["retailer_id"].isin(
                    df_mod.head(8)["retailer_id"].unique().tolist()
                )
            )
        ]
        df_mod_other = df_mod_other.groupby(["year"])["revenue"].sum().reset_index()
        df_mod_other["retailer_id"] = "OTHERS"
        df_mod_other = df_mod_other.drop_duplicates()
        df_mod = pd.concat([df_mod_5, df_mod_other], axis=0)

        pivot = df_mod.pivot_table(
            index="retailer_id", columns="year", values="revenue", aggfunc="sum"
        ).reset_index()

        pivot.columns = ["retailer_id"] + [str(c) for c in pivot.columns[1:]]

        records = pivot.to_dict(orient="records")
        resp = RetailerRevenue(items=records)
        return resp

    def build_summary(self, filters: SummaryFilters) -> SummaryResponse:
        df = self.load_dataframe()
        df_filtered, baseline = self._apply_filters(df, filters)
        assessment_period = self._assessment_period(df_filtered)
        kpis = self._kpis(df_filtered)
        fair_share_vs_revenue = self._fair_share(df_filtered, baseline)
        revenue_by_manufacturer = self._revenue_series(df_filtered)
        revenue_table = self._revenue_table(df_filtered)
        revenue_by_retailer = self.revenue_by_retailer(df_filtered)

        logger.info(
            "Built summary payload | rows=%s filtered=%s manufacturers=%s",
            len(df),
            len(df_filtered),
            len({s.manufacturer for s in revenue_by_manufacturer}),
        )

        return SummaryResponse(
            assessment_period=assessment_period,
            kpis=kpis,
            fair_share_vs_revenue=fair_share_vs_revenue,
            revenue_by_manufacturer=revenue_by_manufacturer,
            revenue_table=revenue_table,
            revenue_by_retailer=revenue_by_retailer,
        )
