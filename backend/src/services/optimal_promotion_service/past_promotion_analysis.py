from __future__ import annotations

import time
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

from src.model.promotion.past_promotion import (
    KPI,
    PastPromotionFilters,
    PastPromotionOptions,
    DualLine,
    ComboChart,
    PastPromotionResponse,
)
from src.utility.logger import AppLogger

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "df_hist_check.csv"
logger = AppLogger.get_logger(__name__)


class PastPromotionAnalysis:

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path
        self.df_raw = self._load_and_clean_df()

    def _load_and_clean_df(self) -> pd.DataFrame:
        if not self.data_path.exists():
            # Fallback or error handling
            msg = f"Data file not found: {self.data_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        df = pd.read_csv(self.data_path)

        # Promo Tactic Cleaning
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "unknown", "Display & TPR", df["promo_tactic"]
        )
        df["promo_tactic"] = np.where(
            df["promo_tactic"] == "No Tactic", "Feature & TPR", df["promo_tactic"]
        )
        df["segment"] = df["subsegment_name"].str.split("|").str[0]
        df["month"] = pd.to_datetime(df["start_date"]).dt.month

        # Standardizing Tactics
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

        # Retailer Cleaning
        df["retailer"] = np.where(
            df["retailer"] == "Target PT", "Target", df["retailer"]
        )
        df["retailer"] = np.where(
            df["retailer"] == "Publix Total TA", "Publix", df["retailer"]
        )
        df["retailer"] = np.where(
            df["retailer"] == "CVS Total Corp ex HI TA", "CVS", df["retailer"]
        )
        df["retailer"] = df["retailer"].apply(lambda x: x.upper())

        # ROI & Mechanics
        df["ROI"] = df["roi"]
        df["offer_mechanic"] = np.where(
            df["offer_mechanic"] == "unknown", "special x off", df["offer_mechanic"]
        )

        # Bins
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

        # Offer Type
        df["offer_type"] = np.where(
            df["offer_type"] == "unknown", "spend_reward", df["offer_type"]
        )
        df["offer_type"] = df["offer_type"].str.upper()
        df["offer_type"] = df["offer_type"].replace("_", " ", regex=True)

        # Year Standardization
        df["year"] = np.where(df["year"] == 2022, 2023, df["year"])
        df["year"] = np.where(df["year"] == 2021, 2022, df["year"])

        # Date & Brand
        df["date"] = pd.to_datetime(
            df["year"].astype(str) + df["month"].astype(str), format="%Y%m"
        )
        df["brand_nm"] = df["ppg_id"].str.split("|").str[2]
        df["retailer"] = df["retailer"].apply(lambda x: x.upper())

        return df

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
        self, df: pd.DataFrame, filters: PastPromotionFilters
    ) -> pd.DataFrame:
        df_fil = df.copy()

        # Helper to check if filter is active (not None and not "All")
        def is_active(f_val):
            return f_val is not None and len(f_val) > 0 and "All" not in f_val

        if is_active(filters.brands):
            df_fil = df_fil[df_fil["brand_nm"].isin(filters.brands)]
        if is_active(filters.segment):
            df_fil = df_fil[df_fil["segment"].isin(filters.segment)]
        if is_active(filters.ppgs):
            df_fil = df_fil[df_fil["ppg_id"].isin(filters.ppgs)]
        if is_active(filters.retailers):
            df_fil = df_fil[df_fil["retailer"].isin(filters.retailers)]
        if is_active(filters.offer_type):
            df_fil = df_fil[df_fil["offer_type"].isin(filters.offer_type)]
        if is_active(filters.promo_tactics):
            df_fil = df_fil[df_fil["promo_tactic"].isin(filters.promo_tactics)]
        if is_active(filters.year):
            df_fil = df_fil[df_fil["year"].isin(filters.year)]
        if is_active(filters.month):
            df_fil = df_fil[df_fil["month"].isin(filters.month)]

        return df_fil

    def _calculate_metrics(self, df: pd.DataFrame) -> List[KPI]:
        df_filtered = df.copy()
        incremental_volume_raw = int(df["incremental_volume"].sum())
        volume = int(df["total_volume"].sum())
        investment = int(df["promo_investment"].sum())
        baseline = int(df["baseline"].sum())
        inc_rev = int(df["incr_revenue"].sum())
        count_retails = df_filtered["retailer"].nunique()
        count_segment = df_filtered["segment"].nunique()
        count_ppg = df_filtered["ppg_id"].nunique()

        # Avoid division by zero
        volume_lift_pct = (
            round((((volume / baseline) - 1) * 100), 2) if baseline else 0.0
        )
        roi = (inc_rev / investment) + 1 if investment else 0.0

        incremental_volume = self._format_big_number(incremental_volume_raw)
        volume_lift_pct = str(volume_lift_pct) + "%"

        return [
            KPI(label="Retailer Count", value=count_retails),
            KPI(label="Segment Count", value=count_segment),
            KPI(label="PPG Count", value=count_ppg),
            KPI(label="Average ROI", value=round(roi, 2)),
            KPI(label="Average Uplift %", value=volume_lift_pct),
            KPI(label="Incremental Volume", value=incremental_volume),
        ]

    def _vol_vs_baseline(self, df: pd.DataFrame) -> List[DualLine]:
        df_pl1 = df.groupby(["date"])[["baseline", "total_volume"]].sum().reset_index()
        df_pl1["date"] = pd.to_datetime(df_pl1["date"])
        df_pl1["date_str"] = df_pl1["date"].dt.strftime("%b %Y")

        return [
            DualLine(
                x=row["date_str"],
                avg_baseline=float(row["baseline"]),
                avg_total_volume=float(row["total_volume"]),
            )
            for _, row in df_pl1.iterrows()
        ]

    def _chart_uplift_vs_depth(self, df: pd.DataFrame) -> List[ComboChart]:
        df2 = (
            df.groupby(["promo_depth"])
            .agg(
                {
                    "incr_revenue": "sum",
                    "baseline": "sum",
                    "total_volume": "sum",
                    "promo_investment": "sum",
                }
            )
            .reset_index()
        )

        # Calculations
        with np.errstate(divide="ignore", invalid="ignore"):
            df2["volume_lift_pct"] = ((df2["total_volume"] / df2["baseline"]) - 1) * 100
            df2["ROI"] = (df2["incr_revenue"] / df2["promo_investment"]) + 1

        # Manual Logic from script
        df2["ROI"] = np.where(
            df2["promo_depth"] == "60%-70%", df2["ROI"].shift(1) - 0.05, df2["ROI"]
        )
        df2["ROI"] = np.where(
            df2["promo_depth"] == "70%-80%", df2["ROI"].shift(1) - 0.1, df2["ROI"]
        )

        return [
            ComboChart(
                uplift=(
                    row["volume_lift_pct"] if not pd.isna(row["volume_lift_pct"]) else 0
                ),
                avg_roi=float(row["ROI"]) if not pd.isna(row["ROI"]) else 0.0,
                promo_depth=str(row["promo_depth"]),
            )
            for _, row in df2.iterrows()
        ]

    def _chart_uplift_vs_mechanic(self, df: pd.DataFrame) -> List[ComboChart]:
        # Filter top 5 logic
        top_offer = (
            df.groupby("offer_mechanic")["volume_lift_pct"]
            .mean()
            .nlargest(5)
            .reset_index()["offer_mechanic"]
            .unique()
            .tolist()
        )
        df_mod = df.copy()
        df_mod["offer_mechanic"] = df_mod["offer_mechanic"].apply(
            lambda x: x if x in top_offer else "Buy 5 get 2 free"
        )

        df3 = (
            df_mod.groupby(["offer_mechanic"])
            .agg(
                {
                    "incr_revenue": "sum",
                    "baseline": "sum",
                    "total_volume": "sum",
                    "promo_investment": "sum",
                }
            )
            .reset_index()
        )

        with np.errstate(divide="ignore", invalid="ignore"):
            df3["volume_lift_pct"] = ((df3["total_volume"] / df3["baseline"]) - 1) * 100
            df3["ROI"] = (df3["incr_revenue"] / df3["promo_investment"]) + 1

        return [
            ComboChart(
                uplift=(
                    row["volume_lift_pct"] if not pd.isna(row["volume_lift_pct"]) else 0
                ),
                avg_roi=float(row["ROI"]) if not pd.isna(row["ROI"]) else 0.0,
                offer_mechanic=str(row["offer_mechanic"]),
            )
            for _, row in df3.iterrows()
        ]

    def _chart_uplift_vs_tactic(self, df: pd.DataFrame) -> List[ComboChart]:
        df3 = (
            df.groupby(["promo_tactic"])
            .agg(
                {
                    "incr_revenue": "sum",
                    "baseline": "sum",
                    "total_volume": "sum",
                    "promo_investment": "sum",
                }
            )
            .reset_index()
        )

        with np.errstate(divide="ignore", invalid="ignore"):
            df3["volume_lift_pct"] = ((df3["total_volume"] / df3["baseline"]) - 1) * 100
            df3["ROI"] = (df3["incr_revenue"] / df3["promo_investment"]) + 1

        # Custom Ordering
        custom_order = ["TPR", "Display", "Feature", "Feature & Display"]
        df3["promo_tactic"] = pd.Categorical(
            df3["promo_tactic"], categories=custom_order, ordered=True
        )
        df3 = df3.sort_values(by="promo_tactic").reset_index(drop=True)

        # Custom Sorting Logic (Bubble sort logic from original script)
        # Ensure we have enough rows to avoid index errors
        if len(df3) >= 4:
            if df3.at[3, "volume_lift_pct"] < df3.at[2, "volume_lift_pct"]:
                df3.iloc[[2, 3]] = df3.iloc[[3, 2]].values

            if df3.at[1, "volume_lift_pct"] < df3.at[0, "volume_lift_pct"]:
                df3.iloc[[0, 1]] = df3.iloc[[1, 0]].values

            if df3.at[2, "volume_lift_pct"] < df3.at[0, "volume_lift_pct"]:
                df3.iloc[[0, 2]] = df3.iloc[[2, 0]].values

        return [
            ComboChart(
                uplift=(
                    row["volume_lift_pct"] if not pd.isna(row["volume_lift_pct"]) else 0
                ),
                avg_roi=float(row["ROI"]) if not pd.isna(row["ROI"]) else 0.0,
                promo_tactic=str(row["promo_tactic"]),
            )
            for _, row in df3.iterrows()
        ]

    def build_options(
        self, df: pd.DataFrame, filters: PastPromotionFilters
    ) -> PastPromotionOptions:
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

        return PastPromotionOptions(
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

    def build_past_performance(
        self, filters: PastPromotionFilters
    ) -> PastPromotionResponse:
        start_total = time.time()
        df_filtered = self._apply_filters(self.df_raw, filters)

        metrics = self._calculate_metrics(df_filtered)
        vol_vs_baseline = self._vol_vs_baseline(df_filtered)
        uplift_vs_depth = self._chart_uplift_vs_depth(df_filtered)
        uplift_vs_mechanic = self._chart_uplift_vs_mechanic(df_filtered)
        uplift_vs_tactic = self._chart_uplift_vs_tactic(df_filtered)

        logger.info(
            f"Past promotion Generated in {time.time() - start_total:.3f} seconds total"
        )

        return PastPromotionResponse(
            metrics=metrics,
            volume_vs_baseline=vol_vs_baseline,
            uplift_vs_discount=uplift_vs_depth,
            uplift_vs_offer=uplift_vs_mechanic,
            uplift_vs_promo=uplift_vs_tactic,
        )
