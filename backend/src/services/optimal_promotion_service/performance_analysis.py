from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from src.utility.logger import AppLogger

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "df_hist_check.csv"
logger = AppLogger.get_logger(__name__)


class PerformanceFilters(BaseModel):
    categories: Optional[List[str]] = Field(default=None)
    brands: Optional[List[str]] = Field(default=None)
    ppgs: Optional[List[str]] = Field(default=None)
    retailers: Optional[List[str]] = Field(default=None)
    segment: Optional[List[str]] = Field(default=None)
    offer_type: Optional[List[str]] = Field(default=None)
    promo_tactics: Optional[List[str]] = Field(default=None)
    year: Optional[List[str]] = Field(
        default=None,
    )
    month: Optional[List[str]] = Field(default=None)


class FilterOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)
    segment: List[str] = Field(default=None)
    offer_type: List[str] = Field(default_factory=list)
    promo_tactics: List[str] = Field(default_factory=list)
    year: List[str] = Field(default_factory=list)
    month: List[str] = Field(default_factory=list)


class KeyMetrics(BaseModel):
    count_retails: int
    count_segment: int
    count_ppg: int
    roi: float
    volume_lift_pct: float
    incremental_volume: float


class DFTable(BaseModel):
    columns: List[str]
    rows: List[Dict[str, str]]


class PerformanceResponse(BaseModel):
    metrics: KeyMetrics
    mechanics: DFTable
    ppg: DFTable
    subsegment: DFTable
    retailer: DFTable


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

        return df

    def format_number(self, x):
        if isinstance(x, (int, float)):
            return "{:.2f}".format(x)  # Format numbers to two decimal places
        return str(x)

    def _apply_filters(df: pd.DataFrame, filters: PerformanceFilters) -> pd.DataFrame:
        df_fil = df.copy()

        if filters.brands and "All" not in filters.brands:
            df_fil = df_fil[df_fil["brand_nm"].isin(filters.brands)]

        if filters.segment and "All" not in filters.segment:
            df_fil = df_fil[df_fil["segment"].isin(filters.brands)]

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

    def _key_metrics(self, df: pd.DataFrame) -> KeyMetrics:

        df_filtered = df.copy()
        incremental_volume = int(df_filtered["incremental_volume"].sum())
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
        return KeyMetrics(
            count_retails=count_retails,
            count_segment=count_segment,
            count_ppg=count_ppg,
            roi=ROI,
            volume_lift_pct=volume_lift_pct,
            incremental_volume=incremental_volume,
        )

    def _offer_mechanics(self, df: pd.DataFrame) -> DFTable:
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

        return self._df_to_table(df_new)

    def _PPG(self, df: pd.DataFrame) -> DFTable:
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

        return self._df_to_table(df_new)

    def _subsegment(self, df: pd.DataFrame) -> DFTable:
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

        return self._df_to_table(df_new)

    def _retailer(self, df: pd.DataFrame) -> DFTable:
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
        return self._df_to_table(df_new)

    @staticmethod
    def build_options(df: pd.DataFrame) -> FilterOptions:
        categories = (
            df["category"].dropna().unique().tolist()
            if "category" in df.columns
            else ["SurfaceCare"]
        )
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
        segment = sorted(df["segment"].dropna().unique().tolist())
        offer_type = sorted(df["offer_type"].dropna().unique().tolist())
        promo_tactic = sorted(df["promo_tactic"].unique().tolist())
        years = sorted(df["year"].astype(str).unique().tolist())
        month = sorted(df["month"].unique().tolist())

        return FilterOptions(
            categories=categories,
            brands=brands,
            ppgs=ppgs,
            retailers=retailers,
            segment=segment,
            offer_type=offer_type,
            promo_tactics=promo_tactic,
            year=years,
            month=month,
        )

    def build_performance(self, filters: PerformanceFilters) -> PerformanceResponse:
        df = self._load_df()
        df_filtered = self._apply_filters(df, filters)
        df_metrics = self._key_metrics(df_filtered)
        df_adjusted = self._apply_adjustments(df_filtered)
        df_offer_mechanics = self._offer_mechanics(df_adjusted)
        df_ppg = self._PPG(df_adjusted)
        df_segment = self._subsegment(df_adjusted)
        df_retailer = self._retailer(df_adjusted)

        return PerformanceResponse(
            metrics=df_metrics,
            mechanics=df_offer_mechanics,
            ppg=df_ppg,
            subsegment=df_segment,
            retailer=df_retailer,
        )
