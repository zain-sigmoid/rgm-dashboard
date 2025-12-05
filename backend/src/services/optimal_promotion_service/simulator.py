from __future__ import annotations

import time
from pathlib import Path
from typing import List, Any

import numpy as np
import pandas as pd

from src.model.promotion.simulation import (
    GlobalFilters,
    SimulationEventFilters,
    SimulationOptions,
    SimulationResponse,
    PieChart,
    PieSegment,
    DFTable,
    SalesLinePoint,
    EventROI,
)
from src.utility.logger import AppLogger

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "simulation_data.csv"
logger = AppLogger.get_logger(__name__)


def _is_active(value: List[Any] | None) -> bool:
    return value is not None and len(value) > 0 and "All" not in value


class SimulationAnalysis:

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path
        self.df_raw = self._load_and_clean_df()

    def _load_and_clean_df(self) -> pd.DataFrame:
        if not self.data_path.exists():
            msg = f"Data file not found: {self.data_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        df = pd.read_csv(self.data_path)

        # Text cleaning & feature engineering copied from Simulation_Tool
        df["segment"] = df["subsegment_name"].str.split("|").str[0]
        df["month"] = pd.to_datetime(df["start_date"]).dt.month

        # Promo tactic standardization
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
        df["offer_mechanic"] = np.where(
            df["offer_mechanic"] == "unknown", "special x off", df["offer_mechanic"]
        )

        # Discount bins
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80]
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
        df["promo_bins"] = pd.cut(df["discount"], bins=bins, labels=labels, right=False)

        # Offer type cleaning
        df["offer_type"] = np.where(
            df["offer_type"] == "unknown", "spend_reward", df["offer_type"]
        )
        df["offer_type"] = df["offer_type"].str.upper()
        df["offer_type"] = df["offer_type"].replace("_", " ", regex=True)

        # Dates normalized to last Sunday of the week
        df["start_dates"] = pd.to_datetime(df["start_date"])
        days_to_subtract = df["start_dates"].dt.dayofweek + 1
        df["start_dates"] = df["start_dates"] - pd.to_timedelta(
            days_to_subtract, unit="D"
        )
        df["start_dates"] = df["start_dates"].dt.date

        # Retailer cleaning
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

        df["brand_nm"] = df["ppg_id"].str.split("|").str[2]

        return df

    def build_options(self, filters: GlobalFilters) -> SimulationOptions:
        """Return unique options for all global filters."""
        df_base = self.df_raw
        categories = (
            df_base["category"].dropna().unique().tolist()
            if "category" in df_base.columns
            else ["SurfaceCare"]
        )

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

        # 5) Offer type, offer mechanic & promo tactics -> filtered by same scope as retailer
        offer_type = sorted(df_retailer_scope["offer_type"].dropna().unique().tolist())
        promo_tactics = sorted(
            df_retailer_scope["promo_tactic"].dropna().unique().tolist()
        )
        offer_mechanic = sorted(
            df_retailer_scope["offer_mechanic"].dropna().unique().tolist()
        )

        return SimulationOptions(
            categories=categories,
            brands=brands,
            segment=segment,
            ppgs=ppgs,
            retailers=retailers,
            offer_type=offer_type,
            promo_tactics=promo_tactics,
            offer_mechanic=offer_mechanic,
        )

    def _apply_global_filters(self, filters: GlobalFilters) -> pd.DataFrame:
        df_fil = self.df_raw.copy()

        if _is_active(filters.brands):
            df_fil = df_fil[df_fil["brand_nm"].isin(filters.brands)]
        if _is_active(filters.segment):
            df_fil = df_fil[df_fil["segment"].isin(filters.segment)]
        if _is_active(filters.ppgs):
            df_fil = df_fil[df_fil["ppg_id"].isin(filters.ppgs)]
        if _is_active(filters.retailers):
            df_fil = df_fil[df_fil["retailer"].isin(filters.retailers)]

        return df_fil

    def _apply_event_filters(
        self, df: pd.DataFrame, event: SimulationEventFilters
    ) -> pd.DataFrame:
        df_temp = df.copy()
        if _is_active(event.promo_tactic):
            df_temp = df_temp[df_temp["promo_tactic"].isin(event.promo_tactic)]
        if _is_active(event.offer_type):
            df_temp = df_temp[df_temp["offer_type"].isin(event.offer_type)]
        if _is_active(event.offer_mechanic):
            df_temp = df_temp[df_temp["offer_mechanic"].isin(event.offer_mechanic)]
        if event.start_date:
            df_temp = df_temp[
                df_temp["start_dates"] == pd.to_datetime(event.start_date).date()
            ]
        if event.duration is not None:
            df_temp = df_temp[df_temp["promo_duration_days"] == event.duration]
        if event.discount is not None:
            df_temp = df_temp[df_temp["discount"] == event.discount]
        if event.redemption_rate is not None:
            df_temp = df_temp.copy()
            df_temp["Redemption Rate"] = event.redemption_rate / 100.0
        return df_temp

    def _roi_for_event(self, df_event: pd.DataFrame, idx: int) -> EventROI:
        investment = df_event["promo_investment"].sum()
        incr_rev = df_event["incr_revenue"].sum()
        roi = (incr_rev / investment) + 1 if investment else 0.0
        return EventROI(promo_index=idx + 1, roi=round(float(roi), 2))

    def _baseline_vs_promo(self, df: pd.DataFrame) -> List[SalesLinePoint]:
        baseline_sales = float(df["baseline"].sum()) if not df.empty else 0.0
        promo_sales = float(df["total_volume"].sum()) if not df.empty else 0.0
        return [
            SalesLinePoint(
                label="All",
                baseline_sales=baseline_sales,
                promo_sales=promo_sales,
            )
        ]

    def _pie_chart(self, baseline: float, promo: float) -> PieChart:
        incremental = max(promo - baseline, 0)
        total_sales = baseline + incremental
        segments = [
            PieSegment(name="Baseline Sales", value=round(baseline, 2)),
            PieSegment(name="Incremental Sales", value=round(incremental, 2)),
        ]
        return PieChart(
            label="Total Sales", total_sales=round(total_sales, 2), segments=segments
        )

    def _drill_table(self, df: pd.DataFrame) -> DFTable:
        if df.empty:
            return DFTable(columns=[], rows=[])

        event_filtered_data = (
            df.groupby(
                [
                    "retailer",
                    "brand_nm",
                    "segment",
                    "ppg_id",
                    "promo_tactic",
                    "offer_mechanic",
                    "offer_type",
                    "start_dates",
                    "promo_duration_days",
                    "discount",
                    "Redemption Rate",
                ]
            )
            .agg(
                {
                    "incr_revenue": "sum",
                    "incremental_volume": "sum",
                    "promo_investment": "sum",
                    "baseline": "sum",
                    "promo_price_unit": "mean",
                    "no_promo_price_unit": "mean",
                    "avg_price_unit": "mean",
                }
            )
            .reset_index()
        )
        event_filtered_data["ROI"] = (
            event_filtered_data["incr_revenue"]
            / event_filtered_data["promo_investment"]
        ) + 1
        event_filtered_data["volume_lift_pct"] = (
            event_filtered_data["incremental_volume"] / event_filtered_data["baseline"]
        ) * 100

        edited_df = event_filtered_data[
            [
                "retailer",
                "brand_nm",
                "segment",
                "ppg_id",
                "promo_tactic",
                "offer_mechanic",
                "offer_type",
                "start_dates",
                "promo_duration_days",
                "discount",
                "incremental_volume",
                "volume_lift_pct",
                "ROI",
                "baseline",
                "promo_price_unit",
                "no_promo_price_unit",
                "avg_price_unit",
                "Redemption Rate",
            ]
        ]

        edited_df.columns = [
            "Retailer",
            "Brand",
            "Segment",
            "PPG",
            "Promo Tactic",
            "Offer Mechanic",
            "Offer Type",
            "Start Date",
            "Promo Duration Days",
            "Discount",
            "Incremental Volume",
            "Volume Uplift",
            "ROI",
            "Baseline",
            "Promo Price Unit",
            "No Promo Price Unit",
            "Average Price Unit",
            "Redemption Rate",
        ]

        edited_df = edited_df.drop_duplicates()
        edited_df["Baseline"] = edited_df["Baseline"].astype(int).map("{:,}".format)
        edited_df["Incremental Volume"] = (
            edited_df["Incremental Volume"].astype(int).map("{:,}".format)
        )

        df_local = edited_df.fillna("")
        df_local = df_local.apply(
            lambda col: col.round(2) if col.dtype != "object" else col
        )

        shape = df_local.shape[0]
        if df.shape[0] > 1000:
            df_local = df_local.head(1000)

        return df_local, shape, df_local.shape[0]

    def _df_to_df_table(self, df: pd.DataFrame) -> DFTable:
        rows = [
            {col: str(val) for col, val in row.items()}
            for row in df.to_dict(orient="records")
        ]
        columns: List[str] = [str(col) for col in df.columns]
        return DFTable(columns=columns, rows=rows)

    def run_simulation(
        self,
        global_filters: GlobalFilters,
        event_filters: List[SimulationEventFilters],
    ) -> SimulationResponse:
        start_total = time.time()
        logger.info("starting simulation")
        df_global = self._apply_global_filters(global_filters)

        # Apply each event filter and collect results
        all_event_frames: List[pd.DataFrame] = []
        rois: List[EventROI] = []
        for idx, event in enumerate(event_filters):
            df_event = self._apply_event_filters(df_global, event)
            if not df_event.empty:
                df_event = df_event.copy()
                df_event["input_number"] = idx
                all_event_frames.append(df_event)
            rois.append(self._roi_for_event(df_event, idx))

        event_df = (
            pd.concat(all_event_frames, axis=0) if all_event_frames else pd.DataFrame()
        )

        baseline_vs_promo = self._baseline_vs_promo(df_global)
        pie_chart = self._pie_chart(
            baseline=baseline_vs_promo[0].baseline_sales,
            promo=baseline_vs_promo[0].promo_sales,
        )
        drill_df, shape, final_shape = self._drill_table(
            event_df if not event_df.empty else df_global
        )

        logger.info(
            f"time talen: {time.time() - start_total:.3f} seconds | rows={shape} | returning rows={final_shape}"
        )
        drill_table = self._df_to_df_table(drill_df)
        return SimulationResponse(
            baseline_vs_promo=baseline_vs_promo,
            pie_chart=pie_chart,
            df_table=drill_table,
            events=rois,
        )
