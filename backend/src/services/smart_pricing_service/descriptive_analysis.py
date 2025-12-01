# backend/src/services/core_service/descriptive_service.py
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from pathlib import Path
from src.utility.logger import AppLogger
from src.model.response import (
    DescriptiveResponse,
    TimeSeriesPoint,
    DescriptiveOptions,
    DescriptiveFilters,
)

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "final_pricing_consolidated_file.csv"
logger = AppLogger.get_logger(__name__)


class DescriptiveAnalysis:

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH):
        self.data_path = data_path

    def load_and_clean_csv(self) -> pd.DataFrame:
        p = self.data_path
        df = pd.read_csv(p)
        df = df.dropna(how="all")
        df["retailer_id"] = df["retailer_id"].apply(lambda x: x.upper())
        df["retailer_id"] = np.where(
            df["retailer_id"] == "Target PT", "Target", df["retailer_id"]
        )
        df["retailer_id"] = np.where(
            df["retailer_id"] == "Publix Total TA", "Publix", df["retailer_id"]
        )
        df["retailer_id"] = np.where(
            df["retailer_id"] == "CVS Total Corp ex HI TA", "CVS", df["retailer_id"]
        )
        df["year"] = pd.to_datetime(df["year"].astype(str), format="%Y")
        df["year"] = df["year"].dt.strftime("%Y")  # **change**
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
        # Define the order of the month names
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

        # Convert month_name column to categorical data type with specified order
        df["month_name"] = pd.Categorical(
            df["month_name"], categories=month_order, ordered=True
        )
        df["year"] = np.where(df["year"] == "2022", "2023", df["year"])
        df["year"] = np.where(df["year"] == "2021", "2022", df["year"])
        df["date"] = pd.to_datetime(
            df["year"].astype(str) + df["month"].astype(str), format="%Y%m"
        )
        return df

    def apply_filters(
        self, df: pd.DataFrame, filters: DescriptiveFilters
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_fil = df.copy()
        df_comp = pd.DataFrame(columns=df.columns)
        if not filters:
            return df_fil, df_comp

        if filters.categories and "All" not in filters.categories:
            if "category" in df_fil.columns:
                df_fil = df_fil[df_fil["category"].isin(filters.categories)]

        if filters.manufacturers and "All" not in filters.manufacturers:
            df_fil = df_fil[df_fil["manufacturer_nm"].isin(filters.manufacturers)]
        if filters.brands and "All" not in filters.brands:
            df_fil = df_fil[df_fil["brand_nm"].isin(filters.brands)]
        if filters.ppgs and "All" not in filters.ppgs:
            df_fil = df_fil[df_fil["ppg_nm"].isin(filters.ppgs)]
        if filters.retailers and "All" not in filters.retailers:
            rlist = [r.upper() for r in filters.retailers]
            df_fil = df_fil[df_fil["retailer_id"].isin(rlist)]
        if filters.years:
            df_fil = df_fil[df_fil["year"].isin(filters.years)]
        if filters.months:
            try:
                months_int = [int(m) for m in filters.months]
                df_fil = df_fil[df_fil["date"].dt.month.isin(months_int)]
            except Exception:
                df_fil = df_fil[
                    df_fil["date"].dt.month.astype(str).isin(filters.months)
                ]

        if filters.include_competitor:
            df_comp = df.copy()
            if filters.competitor_manufacturers:
                df_comp = df_comp[
                    df_comp["manufacturer_nm"].isin(filters.competitor_manufacturers)
                ]
            if filters.competitor_brands:
                df_comp = df_comp[df_comp["brand_nm"].isin(filters.competitor_brands)]
            if filters.competitor_ppgs:
                df_comp = df_comp[df_comp["ppg_nm"].isin(filters.competitor_ppgs)]
            if filters.competitor_retailers:
                rlist_comp = [r.upper() for r in filters.competitor_retailers]
                df_comp = df_comp[df_comp["retailer_id"].isin(rlist_comp)]
            if filters.years:
                df_comp = df_comp[df_comp["year"].isin(filters.years)]
            if filters.months:
                try:
                    months_int = [int(m) for m in filters.months]
                    df_comp = df_comp[df_comp["date"].dt.month.isin(months_int)]
                except Exception:
                    df_comp = df_comp[
                        df_comp["date"].dt.month.astype(str).isin(filters.months)
                    ]

        return df_fil, df_comp

    def _kpi_trend(self, df: pd.DataFrame, tab: str):
        if tab == "volume_vs_revenue":
            df_vol_rev = (
                df.groupby(["date"])
                .agg({"volume": "sum", "revenue": "sum"})
                .reset_index()
            )
            df_vol_rev["date"] = pd.to_datetime(df_vol_rev["date"])
            df_vol_rev["date"] = df_vol_rev["date"].dt.strftime("%Y-%m-%d")
            return df_vol_rev
        elif tab == "volume_vs_price":
            df_plot = df.copy()
            df_plot = (
                df_plot.groupby(["date"])
                .agg({"volume": "sum", "price": "mean"})
                .reset_index()
                .round(2)
            )
            df_plot = df_plot.sort_values("date")

            df_plot["date"] = pd.to_datetime(df_plot["date"])
            df_plot["date"] = df_plot["date"].dt.strftime("%Y-%m-%d")

            return df_plot
        elif tab == "volume_vs_ditribution":
            df_plot = df.copy()
            # df_plot['date']=pd.to_datetime(df_plot[['year', 'month', 'day']])
            df_plot = (
                df_plot.groupby(["date"])
                .agg({"volume": "sum", "acv_wtd_distribution": "mean"})
                .reset_index()
                .round(2)
            )
            df_plot = df_plot.sort_values("date")
            #  df_plot=df_plot.sort_values('date')
            df_plot["date"] = pd.to_datetime(df_plot["date"])
            df_plot["date"] = df_plot["date"].dt.strftime("%Y-%m-%d")

            return df_plot

    def _comparison_vs_competition(
        self, df: pd.DataFrame, df_com: pd.DataFrame, tab: str
    ):
        if tab == "own_price_vs_competitor_price":
            df_price = (
                df.groupby(["date"]).agg({"price": "mean"}).reset_index().round(2)
            )
            df_price_com = (
                df_com.groupby(["date"]).agg({"price": "mean"}).reset_index().round(2)
            )

            df_price = df_price.sort_values(["date"])
            df_price["date"] = pd.to_datetime(df_price["date"])
            df_price["date"] = df_price["date"].dt.strftime("%b %Y")
            df_price_com = df_price_com.sort_values(["date"])
            df_price_com["date"] = pd.to_datetime(df_price_com["date"])
            df_price_com["date"] = df_price_com["date"].dt.strftime("%b %Y")

            return df_price, df_price_com
        elif tab == "own_distribution_vs_competitor_distribution":
            df_price = (
                df.groupby(["date"])
                .agg({"acv_wtd_distribution": "mean"})
                .reset_index()
                .round(0)
            )
            df_price_com = (
                df_com.groupby(["date"])
                .agg({"acv_wtd_distribution": "mean"})
                .reset_index()
                .round(0)
            )

            df_price = df_price.sort_values(["date"])
            df_price["date"] = pd.to_datetime(df_price["date"])
            df_price["date"] = df_price["date"].dt.strftime("%b %Y")
            df_price_com = df_price_com.sort_values(["date"])
            df_price_com["date"] = pd.to_datetime(df_price_com["date"])
            df_price_com["date"] = df_price_com["date"].dt.strftime("%b %Y")

            return df_price, df_price_com

    def build_options(
        self, df: pd.DataFrame, filters: DescriptiveFilters
    ) -> DescriptiveOptions:
        # ---- Categories ----
        categories = (
            df["category"].dropna().unique().tolist()
            if "category" in df.columns
            else ["SurfaceCare"]
        )

        # ---- Base scope (for manu/brand/ppg/retailer) ----
        df_base = df.copy()

        # NOTE: do NOT filter by year here
        if filters.months:
            df_base = df_base[df_base["month"].isin(filters.months)]
        if filters.retailers:
            df_base = df_base[df_base["retailer_id"].isin(filters.retailers)]

        # ---- 1) Manufacturer options ----
        manufacturers = sorted(df_base["manufacturer_nm"].dropna().unique().tolist())

        # ---- 2) Brand options (filtered by manufacturer) ----
        df_brand_scope = df_base.copy()
        if filters.manufacturers:
            df_brand_scope = df_brand_scope[
                df_brand_scope["manufacturer_nm"].isin(filters.manufacturers)
            ]
        brands = sorted(df_brand_scope["brand_nm"].dropna().unique().tolist())

        # ---- 3) PPG options (filtered by brand) ----
        df_ppg_scope = df_brand_scope.copy()
        if filters.brands:
            df_ppg_scope = df_ppg_scope[df_ppg_scope["brand_nm"].isin(filters.brands)]
        ppgs = sorted(df_ppg_scope["ppg_nm"].dropna().unique().tolist())

        # ---- 4) Retailer options (filtered by ppg) ----
        df_retailer_scope = df_ppg_scope.copy()
        if filters.ppgs:
            df_retailer_scope = df_retailer_scope[
                df_retailer_scope["ppg_nm"].isin(filters.ppgs)
            ]
        retailers = sorted(df_retailer_scope["retailer_id"].dropna().unique().tolist())

        # ---- Years & months options (do NOT filter by selected years) ----
        df_time_scope = df.copy()
        # you may optionally apply category / retailer filter here if you want them to depend
        if filters.retailers:
            df_time_scope = df_time_scope[
                df_time_scope["retailer_id"].isin(filters.retailers)
            ]
        years = sorted(df_time_scope["year"].dropna().astype(str).unique().tolist())
        months = sorted(df_time_scope["month"].dropna().unique().tolist())

        # ---- Competitor side ----
        competitor_manufacturers: List[str] = []
        competitor_brands: List[str] = []
        competitor_ppgs: List[str] = []
        competitor_retailers: List[str] = []

        if filters.include_competitor:
            # All manufacturers in the base scope
            all_manus = set(df_base["manufacturer_nm"].dropna().unique().tolist())
            selected_manus = set(filters.manufacturers or [])

            # 1) Competitor manufacturer options = all others except selected manu
            competitor_manufacturers = sorted(all_manus - selected_manus)

            # Active competitor manufacturers for drilling down brands/ppgs
            active_comp_manus = (
                filters.competitor_manufacturers
                if filters.competitor_manufacturers
                else competitor_manufacturers
            )

            if active_comp_manus:
                df_comp_brand_scope = df_base[
                    df_base["manufacturer_nm"].isin(active_comp_manus)
                ]

                # 2) Competitor brand options (filtered by competitor manufacturers, not by brand)
                competitor_brands = sorted(
                    df_comp_brand_scope["brand_nm"].dropna().unique().tolist()
                )

                # 3) Competitor PPG options (filtered by competitor manu + competitor brand)
                df_comp_ppg_scope = df_comp_brand_scope.copy()
                if filters.competitor_brands:
                    df_comp_ppg_scope = df_comp_ppg_scope[
                        df_comp_ppg_scope["brand_nm"].isin(filters.competitor_brands)
                    ]

                competitor_ppgs = sorted(
                    df_comp_ppg_scope["ppg_nm"].dropna().unique().tolist()
                )

                # 4) Competitor retailer options (optional: depend on ppgs)
                df_comp_retailer_scope = df_comp_ppg_scope.copy()
                if filters.competitor_ppgs:
                    df_comp_retailer_scope = df_comp_retailer_scope[
                        df_comp_retailer_scope["ppg_nm"].isin(filters.competitor_ppgs)
                    ]
                if filters.competitor_retailers:
                    df_comp_retailer_scope = df_comp_retailer_scope[
                        df_comp_retailer_scope["retailer_id"].isin(
                            filters.competitor_retailers
                        )
                    ]

                competitor_retailers = sorted(
                    df_comp_retailer_scope["retailer_id"].dropna().unique().tolist()
                )

        return DescriptiveOptions(
            categories=categories,
            manufacturers=manufacturers,
            brands=brands,
            ppgs=ppgs,
            retailers=retailers,
            years=years,
            months=months,
            competitor_manufacturers=competitor_manufacturers,
            competitor_brands=competitor_brands,
            competitor_ppgs=competitor_ppgs,
            competitor_retailers=competitor_retailers,
        )

    def compute_descriptive(self, filters: DescriptiveFilters) -> DescriptiveResponse:
        df = self.load_and_clean_csv()
        filter_obj = (
            filters
            if isinstance(filters, DescriptiveFilters)
            else DescriptiveFilters(**filters)
        )
        df_fil, df_comp = self.apply_filters(df, filter_obj)

        if df_fil.shape[0] == 0:
            return DescriptiveResponse(
                volume_vs_revenue=[],
                volume_vs_price=[],
                volume_vs_distribution=[],
                competitor_price=[],
                competitor_distribution=[],
                top_table=[],
                row_count=0,
            )

        # KPI Trend tabs
        vol_rev_df = self._kpi_trend(df_fil, "volume_vs_revenue")
        vol_price_df = self._kpi_trend(df_fil, "volume_vs_price")
        vol_dist_df = self._kpi_trend(df_fil, "volume_vs_ditribution")

        volume_vs_revenue: List[TimeSeriesPoint] = [
            TimeSeriesPoint(
                date=row["date"],
                volume=float(row["volume"]),
                revenue=float(row["revenue"]),
            )
            for _, row in vol_rev_df.iterrows()
        ]
        volume_vs_price: List[TimeSeriesPoint] = [
            TimeSeriesPoint(
                date=row["date"],
                volume=float(row["volume"]),
                price=float(row["price"]),
            )
            for _, row in vol_price_df.iterrows()
        ]
        volume_vs_distribution: List[TimeSeriesPoint] = [
            TimeSeriesPoint(
                date=row["date"],
                volume=float(row["volume"]),
                distribution=float(row["acv_wtd_distribution"]),
            )
            for _, row in vol_dist_df.iterrows()
        ]

        competitor_price: List[TimeSeriesPoint] = []
        competitor_distribution: List[TimeSeriesPoint] = []
        if not df_comp.empty:
            df_price, df_price_com = self._comparison_vs_competition(
                df_fil, df_comp, "own_price_vs_competitor_price"
            )
            competitor_price = [
                TimeSeriesPoint(
                    date=row["date"],
                    price=float(row["price"]),
                    competitor_price=float(row_com["price"]),
                    volume=0.0,
                )
                for (_, row), (_, row_com) in zip(
                    df_price.iterrows(), df_price_com.iterrows()
                )
            ]
            df_dist, df_dist_com = self._comparison_vs_competition(
                df_fil, df_comp, "own_distribution_vs_competitor_distribution"
            )
            competitor_distribution = [
                TimeSeriesPoint(
                    date=row["date"],
                    distribution=float(row["acv_wtd_distribution"]),
                    competitor_distribution=float(row_com["acv_wtd_distribution"]),
                    volume=0.0,
                )
                for (_, row), (_, row_com) in zip(
                    df_dist.iterrows(), df_dist_com.iterrows()
                )
            ]

        logger.info(f"Trend Computed with {int(df_fil.shape[0])} rows")
        return DescriptiveResponse(
            volume_vs_revenue=volume_vs_revenue,
            volume_vs_price=volume_vs_price,
            volume_vs_distribution=volume_vs_distribution,
            competitor_price=competitor_price,
            competitor_distribution=competitor_distribution,
            # top_table=top_table,
            row_count=int(df_fil.shape[0]),
        )
