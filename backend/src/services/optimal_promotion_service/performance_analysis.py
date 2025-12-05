from __future__ import annotations

import time
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List

from src.model.promotion.performance import (
    PerformanceFilters,
    FilterOptions,
    DFTable,
    KPI,
    PerformanceResponse,
)
from src.utility.logger import AppLogger

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "df_hist_check.csv"
logger = AppLogger.get_logger(__name__)


class PerformanceAnalysis:

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path

    def _load_df(
        self,
    ) -> pd.DataFrame:
        if not self.data_path.exists():
            msg = f"Data file not found: {self.data_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        df = pd.read_csv(self.data_path)

        df["segment"] = df["subsegment_name"].str.split("|").str[0]
        df["year"] = np.where(df["year"] == 2022, 2023, df["year"])
        df["year"] = np.where(df["year"] == 2021, 2022, df["year"])
        df["month"] = pd.to_datetime(df["start_date"]).dt.month
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "unknown", "Display & TPR", df["promo_tactic"]
        )
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "No Tactic", "Feature & TPR", df["promo_tactic"]
        )
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "Feature & TPR", "Feature", df["promo_tactic"]
        )
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "Display & TPR", "Display", df["promo_tactic"]
        )
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "Feature Only", "Feature", df["promo_tactic"]
        )
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "Display Only", "Display", df["promo_tactic"]
        )
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "TPR Only", "TPR", df["promo_tactic"]
        )
        df["ROI"] = df["roi"]
        df["retailer"] = np.where(
            df["retailer"] == "Target PT", "Target", df["retailer"]
        )
        df["retailer"] = np.where(
            df["retailer"] == "Publix Total TA", "Publix", df["retailer"]
        )
        df["retailer"] = np.where(
            df["retailer"] == "CVS Total Corp ex HI TA", "CVS", df["retailer"]
        )
        df["offer_mechanic"] = np.where(
            df["offer_mechanic"] == "unknown", "special x off", df["offer_mechanic"]
        )
        bins = [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
        labels = [
            "0%-10%",
            "10%-20%",
            "20%-30%",
            "30%-40%",
            "40%-50%",
            "50%-60%",
            "60%-70%",
            "70%-80%",
        ]
        df["promo_depth"] = pd.cut(
            df["discount"], bins=bins, labels=labels, right=False
        )
        df["offer_type"] = np.where(
            df["offer_type"] == "unknown", "spend_reward", df["offer_type"]
        )
        df["offer_type"] = df["offer_type"].str.upper()
        df["offer_type"] = df["offer_type"].replace("_", " ", regex=True)
        df["brand_nm"] = df["ppg_id"].str.split("|").str[2]
        df["retailer"] = df["retailer"].apply(lambda x: x.upper())
        df["brand_nm"] = df["brand_nm"].fillna("").astype(str).str.strip()

        return df

    def format_number(self, x):
        if isinstance(x, (int, float)):
            return "{:.2f}".format(x)  # Format numbers to two decimal places
        return str(x)

    def _format_big_number(self, value: float) -> str:
        abs_value = abs(value)

        if abs_value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif abs_value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif abs_value >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:,.0f}"

    def _apply_filters(
        self, df: pd.DataFrame, filters: PerformanceFilters
    ) -> pd.DataFrame:
        df_fil = df.copy()

        if filters.brands and "All" not in filters.brands:
            df_fil = df_fil[df_fil["brand_nm"].isin(filters.brands)]

        if filters.segment and "All" not in filters.segment:
            df_fil = df_fil[df_fil["segment"].isin(filters.segment)]

        if filters.ppgs and "All" not in filters.ppgs:
            df_fil = df_fil[df_fil["ppg_id"].isin(filters.ppgs)]

        if filters.retailers and "All" not in filters.retailers:
            df_fil = df_fil[df_fil["retailer"].isin(filters.retailers)]

        if filters.offer_type and "All" not in filters.offer_type:
            df_fil = df_fil[df_fil["offer_type"].isin(filters.offer_type)]

        if filters.promo_tactics and "All" not in filters.promo_tactics:
            df_fil = df_fil[df_fil["promo_tactic"].isin(filters.promo_tactics)]

        if filters.year and "All" not in filters.year:
            df_fil = df_fil[df_fil["year"].isin(filters.year)]

        if filters.month and "All" not in filters.month:
            df_fil = df_fil[df_fil["month"].isin(filters.month)]

        return df_fil

    def _df_to_table(self, df: pd.DataFrame) -> DFTable:
        columns: List[str] = [str(col) for col in df.columns]

        rows: List[Dict[str, str]] = []

        for _, row in df.iterrows():
            row_dict: Dict[str, str] = {}
            for col in columns:
                val = row[col]
                # Handle NaN / None
                if pd.isna(val):
                    formatted = ""
                else:
                    formatted = self.format_number(val)

                row_dict[col] = formatted

            rows.append(row_dict)

        return DFTable(columns=columns, rows=rows)

    def _apply_adjustments(self, df: pd.DataFrame) -> pd.DataFrame:
        df_filtered = df.copy()
        df_filtered["discount%"] = df_filtered["discount"] * 100
        df_filtered["Redemption Rate%"] = df_filtered["Redemption Rate"] * 100

        return df_filtered

    def _key_metrics(self, df: pd.DataFrame) -> List[KPI]:

        df_filtered = df.copy()
        incremental_volume_raw = int(df_filtered["incremental_volume"].sum())
        volume = int(df_filtered["total_volume"].sum())
        investment = int(df_filtered["promo_investment"].sum())
        baseline = int(df_filtered["baseline"].sum())
        inc_rev = int(df_filtered["incr_revenue"].sum())
        volume_lift_pct = round((((volume / baseline) - 1) * 100), 2)
        roi = (inc_rev / investment) + 1
        ROI = round(roi, 2)
        count_retails = df_filtered["retailer"].nunique()
        count_segment = df_filtered["segment"].nunique()
        count_ppg = df_filtered["ppg_id"].nunique()

        incremental_volume = self._format_big_number(incremental_volume_raw)
        volume_lift_pct = str(volume_lift_pct) + "%"

        return [
            KPI(label="Retailer Count", value=count_retails),
            KPI(label="Segment Count", value=count_segment),
            KPI(label="PPG Count", value=count_ppg),
            KPI(label="Average ROI", value=ROI),
            KPI(label="Average Uplift %", value=volume_lift_pct),
            KPI(label="Incremental Volume", value=incremental_volume),
        ]

    def _offer_mechanics(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = (
            df.groupby(["offer_mechanic", "retailer", "ppg_id"])
            .agg(
                {
                    "baseline": "sum",
                    "promo_investment": "sum",
                    "no_promo_price_unit": "mean",
                    "avg_price_unit": "mean",
                    "promo_price_unit": "mean",
                    "volume_lift_pct": "mean",
                    "incremental_volume": "sum",
                    "Redemption Rate%": "mean",
                    "discount%": "mean",
                    "promo_duration_days": "mean",
                }
            )
            .reset_index()
        )
        df_new["ROI"] = (df_new["incremental_volume"] / df_new["promo_investment"]) + 1
        df_new["Redemption Rate%"] = (
            (df_new["no_promo_price_unit"] - df_new["avg_price_unit"])
            / (df_new["no_promo_price_unit"] - df_new["promo_price_unit"])
            * 100
        )
        df_new["discount%"] = (
            (df_new["avg_price_unit"] - df_new["promo_price_unit"])
            / (df_new["avg_price_unit"])
            * 100
        )
        df_new["volume_lift_pct"] = (
            df_new["incremental_volume"] / df_new["baseline"]
        ) * 100
        df_new = df_new.drop(
            [
                "promo_price_unit",
                "no_promo_price_unit",
                "avg_price_unit",
                "promo_investment",
            ],
            axis=1,
        )
        df_new.columns = [
            "Offer Mechanics",
            "Retailer",
            "PPG",
            "Baseline",
            "Avg Volume Uplift%",
            "Incremental Volume",
            "Avg Redemption Rate%",
            "Avg Promo Discount%",
            "Avg Promo Duration Days",
            "ROI",
        ]
        # st.dataframe(df_new,use_container_width=True)
        df_new["Baseline"] = df_new["Baseline"].astype(int).map("{:,}".format)
        df_new["Incremental Volume"] = (
            df_new["Incremental Volume"].astype(int).map("{:,}".format)
        )

        return df_new

    def _PPG(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = (
            df.groupby(["ppg_id", "retailer"])
            .agg(
                {
                    "baseline": "sum",
                    "promo_investment": "sum",
                    "no_promo_price_unit": "mean",
                    "avg_price_unit": "mean",
                    "promo_price_unit": "mean",
                    "volume_lift_pct": "mean",
                    "incremental_volume": "sum",
                    "Redemption Rate%": "mean",
                    "discount%": "mean",
                    "promo_duration_days": "mean",
                }
            )
            .reset_index()
        )
        df_new["ROI"] = (df_new["incremental_volume"] / df_new["promo_investment"]) + 1
        df_new["Redemption Rate%"] = (
            (df_new["no_promo_price_unit"] - df_new["avg_price_unit"])
            / (df_new["no_promo_price_unit"] - df_new["promo_price_unit"])
            * 100
        )
        df_new["discount%"] = (
            (df_new["avg_price_unit"] - df_new["promo_price_unit"])
            / (df_new["avg_price_unit"])
            * 100
        )
        df_new["volume_lift_pct"] = (
            df_new["incremental_volume"] / df_new["baseline"]
        ) * 100
        df_new = df_new.drop(
            [
                "promo_price_unit",
                "no_promo_price_unit",
                "avg_price_unit",
                "promo_investment",
            ],
            axis=1,
        )
        df_new.columns = [
            "PPG",
            "Retailer",
            "Baseline",
            "Avg Vol Uplift",
            "Incremental Volume",
            "Avg Redemption Rate%",
            "Avg Promo Discount%",
            "Avg Promo Duration Days",
            "ROI",
        ]
        # st.dataframe(df_new,use_container_width=True)
        df_new["Baseline"] = df_new["Baseline"].astype(int).map("{:,}".format)
        df_new["Incremental Volume"] = (
            df_new["Incremental Volume"].astype(int).map("{:,}".format)
        )

        return df_new

    def _subsegment(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = (
            df.groupby(["subsegment_name", "retailer", "ppg_id"])
            .agg(
                {
                    "baseline": "sum",
                    "promo_investment": "sum",
                    "no_promo_price_unit": "mean",
                    "avg_price_unit": "mean",
                    "promo_price_unit": "mean",
                    "volume_lift_pct": "mean",
                    "incremental_volume": "sum",
                    "Redemption Rate%": "mean",
                    "discount%": "mean",
                    "promo_duration_days": "mean",
                }
            )
            .reset_index()
        )
        df_new["ROI"] = (df_new["incremental_volume"] / df_new["promo_investment"]) + 1
        df_new["Redemption Rate%"] = (
            (df_new["no_promo_price_unit"] - df_new["avg_price_unit"])
            / (df_new["no_promo_price_unit"] - df_new["promo_price_unit"])
            * 100
        )
        df_new["discount%"] = (
            (df_new["avg_price_unit"] - df_new["promo_price_unit"])
            / (df_new["avg_price_unit"])
            * 100
        )
        df_new["volume_lift_pct"] = (
            df_new["incremental_volume"] / df_new["baseline"]
        ) * 100
        df_new = df_new.drop(
            [
                "promo_price_unit",
                "no_promo_price_unit",
                "avg_price_unit",
                "promo_investment",
            ],
            axis=1,
        )
        df_new.columns = [
            "Subsegment",
            "Retailer",
            "PPG",
            "Baseline",
            "Avg Vol Uplift",
            "Incremental Volume",
            "Avg Redemption Rate%",
            "Avg Promo Discount%",
            "Avg Promo Duration Days",
            "ROI",
        ]
        # st.dataframe(df_new,use_container_width=True)
        df_new["Baseline"] = df_new["Baseline"].astype(int).map("{:,}".format)
        df_new["Incremental Volume"] = (
            df_new["Incremental Volume"].astype(int).map("{:,}".format)
        )

        return df_new

    def _retailer(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = (
            df.groupby(["retailer", "ppg_id"])
            .agg(
                {
                    "baseline": "sum",
                    "promo_investment": "sum",
                    "no_promo_price_unit": "mean",
                    "avg_price_unit": "mean",
                    "promo_price_unit": "mean",
                    "volume_lift_pct": "mean",
                    "incremental_volume": "sum",
                    "Redemption Rate%": "mean",
                    "discount%": "mean",
                    "promo_duration_days": "mean",
                }
            )
            .reset_index()
        )
        df_new["ROI"] = (df_new["incremental_volume"] / df_new["promo_investment"]) + 1
        df_new["Redemption Rate%"] = (
            (df_new["no_promo_price_unit"] - df_new["avg_price_unit"])
            / (df_new["no_promo_price_unit"] - df_new["promo_price_unit"])
            * 100
        )
        df_new["discount%"] = (
            (df_new["avg_price_unit"] - df_new["promo_price_unit"])
            / (df_new["avg_price_unit"])
            * 100
        )
        df_new["volume_lift_pct"] = (
            df_new["incremental_volume"] / df_new["baseline"]
        ) * 100
        df_new = df_new.drop(
            [
                "promo_price_unit",
                "no_promo_price_unit",
                "avg_price_unit",
                "promo_investment",
            ],
            axis=1,
        )
        df_new.columns = [
            "Retailer",
            "PPG",
            "Baseline",
            "Avg Vol Uplift",
            "Incremental Volume",
            "Avg Redemption Rate%",
            "Avg Promo Discount%",
            "Avg Promo Duration Days",
            "ROI",
        ]

        df_new["Baseline"] = df_new["Baseline"].astype(int).map("{:,}".format)
        df_new["Incremental Volume"] = (
            df_new["Incremental Volume"].astype(int).map("{:,}".format)
        )
        return df_new

    @staticmethod
    def build_options(df: pd.DataFrame, filters: PerformanceFilters) -> FilterOptions:
        # Base scope for all dependent fields (except brand itself)
        df_base = df.copy()
        categories = (
            df["category"].dropna().unique().tolist()
            if "category" in df.columns
            else ["SurfaceCare"]
        )

        # Example: years/month can narrow scope for other fields
        if filters.year:
            df_base = df_base[df_base["year"].isin(filters.year)]
        if filters.month:
            df_base = df_base[df_base["month"].isin(filters.month)]

        # 1) Brand options -> do NOT filter by selected brand
        brands = sorted(df_base["brand_nm"].dropna().unique().tolist())

        # 2) Segment options -> filtered by selected brand, but NOT by segment itself
        df_segment_scope = df_base.copy()
        if filters.brands:
            df_segment_scope = df_segment_scope[
                df_segment_scope["brand_nm"].isin(filters.brands)
            ]
        segment = sorted(df_segment_scope["segment"].dropna().unique().tolist())

        # 3) PPG options -> filtered by brand + segment
        df_ppg_scope = df_segment_scope.copy()
        if filters.segment:
            df_ppg_scope = df_ppg_scope[df_ppg_scope["segment"].isin(filters.segment)]
        ppgs = sorted(df_ppg_scope["ppg_id"].dropna().unique().tolist())

        # 4) Retailer options -> filtered by brand + segment + ppg
        df_retailer_scope = df_ppg_scope.copy()
        if filters.ppgs:
            df_retailer_scope = df_retailer_scope[
                df_retailer_scope["ppg_id"].isin(filters.ppgs)
            ]
        retailers = sorted(df_retailer_scope["retailer"].dropna().unique().tolist())

        # 5) Offer type & promo tactics -> filtered by same scope as retailer
        offer_type = sorted(df_retailer_scope["offer_type"].dropna().unique().tolist())
        promo_tactics = sorted(
            df_retailer_scope["promo_tactic"].dropna().unique().tolist()
        )

        # 6) Years & months options -> usually from a broader scope so they don't disappear
        years = sorted(df["year"].astype(str).dropna().unique().tolist())
        months = sorted(df["month"].dropna().unique().tolist())

        return FilterOptions(
            categories=categories,
            brands=brands,
            segment=segment,
            ppgs=ppgs,
            retailers=retailers,
            offer_type=offer_type,
            promo_tactics=promo_tactics,
            year=years,
            month=months,
        )

    def load_table(self, filters: PerformanceFilters, table_name: str) -> pd.DataFrame:
        """
        Compute and return a single DataFrame (mechanics/ppg/subsegment/retailer/metrics)
        based on the requested table_name.
        """
        df = self._load_df()
        df_filtered = self._apply_filters(df, filters)
        df_adjusted = self._apply_adjustments(df_filtered)

        table_name = table_name.lower()

        if table_name == "offer_mechanics":
            return self._offer_mechanics(df_adjusted)
        elif table_name == "ppgs":
            return self._PPG(df_adjusted)
        elif table_name == "subsegment":
            return self._subsegment(df_adjusted)
        elif table_name == "retailer":
            return self._retailer(df_adjusted)
        else:
            logger.error(f"Unknown table name: {table_name}")
            raise ValueError(f"Unknown table name: {table_name}")

    def build_performance(self, filters: PerformanceFilters) -> PerformanceResponse:
        start_total = time.time()
        df = self._load_df()
        df_filtered = self._apply_filters(df, filters)
        df_metrics = self._key_metrics(df_filtered)
        df_adjusted = self._apply_adjustments(df_filtered)
        df_offer_mechanics = self._offer_mechanics(df_adjusted)
        df_ppg = self._PPG(df_adjusted)
        df_segment = self._subsegment(df_adjusted)
        df_retailer = self._retailer(df_adjusted)

        logger.info(
            f"Performance Generated in {time.time() - start_total:.3f} seconds total"
        )

        return PerformanceResponse(
            metrics=df_metrics,
            mechanics=self._df_to_table(df_offer_mechanics),
            ppg=self._df_to_table(df_ppg),
            subsegment=self._df_to_table(df_segment),
            retailer=self._df_to_table(df_retailer),
        )
