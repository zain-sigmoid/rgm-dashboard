from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import math
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from src.utility.logger import AppLogger

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "final_pricing_consolidated_file.csv"
logger = AppLogger.get_logger(__name__)


class SimulationFilters(BaseModel):
    categories: Optional[List[str]] = Field(default=None)
    manufacturers: Optional[List[str]] = Field(default=None)
    brands: Optional[List[str]] = Field(default=None)
    ppgs: Optional[List[str]] = Field(default=None)
    retailers: Optional[List[str]] = Field(default=None)


class SimulationAdjustments(BaseModel):
    price_change_pct: float = 0.0
    new_price: Optional[float] = 0.0
    competitor_price_change_pct: float = 0.0
    new_competitor_price: Optional[float] = 0.0
    new_distribution: Optional[float] = 0.0


class MetricCard(BaseModel):
    label: str
    value: str


class BarDatum(BaseModel):
    label: str
    value: float


class ComparisonBars(BaseModel):
    title: str
    unit: str
    bars: List[BarDatum]


class SimulationTable(BaseModel):
    columns: List[str]
    rows: List[Dict[str, str]]


class SimulationOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    manufacturers: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)


class SimulationResponse(BaseModel):
    summary_cards: List[MetricCard]
    volume_bars: ComparisonBars
    revenue_bars: ComparisonBars
    table: SimulationTable
    context_table: SimulationTable
    context: Dict[str, float]


class SimulationAnalysisService:
    """
    Returns a JSON-friendly payload
    for the frontend to render charts, cards, and tables.
    """

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path

    def _load_df(self) -> pd.DataFrame:
        if not self.data_path.exists():
            msg = f"Data file not found: {self.data_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        df = pd.read_csv(self.data_path)
        df = df.dropna()
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
        return df

    def _convert_to_abbreviated(self, num: float) -> str:
        n = abs(num)
        if n < 1_000:
            return str(round(num, 2))
        if n < 1_000_000:
            return f"{round(num / 1_000, 2)}K"
        if n < 1_000_000_000:
            return f"{round(num / 1_000_000, 2)}M"
        if n < 1_000_000_000_000:
            return f"{round(num / 1_000_000_000, 2)}B"
        return f"{round(num / 1_000_000_000_000, 2)}T"

    @staticmethod
    def _apply_filters(df: pd.DataFrame, filters: SimulationFilters) -> pd.DataFrame:
        df_fil = df.copy()
        if filters.manufacturers and "All" not in filters.manufacturers:
            df_fil = df_fil[df_fil["manufacturer_nm"].isin(filters.manufacturers)]
        if filters.brands and "All" not in filters.brands:
            df_fil = df_fil[df_fil["brand_nm"].isin(filters.brands)]
        if filters.ppgs and "All" not in filters.ppgs:
            df_fil = df_fil[df_fil["ppg_nm"].isin(filters.ppgs)]
        if filters.retailers and "All" not in filters.retailers:
            df_fil = df_fil[df_fil["retailer_id"].isin(filters.retailers)]
        return df_fil

    @staticmethod
    def _prepare_future_frame(df_fil: pd.DataFrame) -> pd.DataFrame:
        if df_fil.empty:
            return df_fil

        price_latest = df_fil[
            (df_fil["year"] == df_fil["year"].max()) & (df_fil["week"] == 52)
        ][["ppg_nm", "retailer_id", "price"]]
        df_new = df_fil[df_fil["year"].isin(["2021", "2022"])].copy()
        df_new["year"] = df_new["year"].replace({"2021": 2023, "2022": 2024})
        df_new = df_new[df_new["year"] == 2024]
        df_future = pd.merge(
            df_new,
            price_latest,
            on=["ppg_nm", "retailer_id"],
            how="left",
            suffixes=("", "_latest"),
        )

        df_future = (
            df_future.groupby(
                ["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm", "year"]
            )
            .agg(
                {
                    "Price_coeff": "mean",
                    "price": "mean",
                    "acv_wtd_distribution": "mean",
                    "Distribution_coeff": "mean",
                    "xpi_final": "mean",
                    "com_price_coef": "mean",
                    "re_intercept": "mean",
                    "d_intercept": "mean",
                    "volume": "sum",
                }
            )
            .reset_index()
        )
        return df_future

    @staticmethod
    def _build_base_inputs(df_future: pd.DataFrame) -> pd.DataFrame:
        df_filtered_temp = df_future.copy()
        df_filtered_temp["new_price"] = np.nan
        df_filtered_temp["chnage%"] = np.nan
        df_filtered_temp["com_new_price"] = np.nan
        df_filtered_temp["com_chnage%"] = np.nan
        df_filtered_temp["distribution"] = np.nan
        df_filtered_temp["New cometitor Price"] = False
        df_filtered_temp["New Price"] = False
        df_filtered_temp["Change Distribution"] = False

        df_input = df_filtered_temp[
            [
                "manufacturer_nm",
                "brand_nm",
                "retailer_id",
                "ppg_nm",
                "year",
                "Price_coeff",
                "price",
                "New Price",
                "new_price",
                "chnage%",
                "acv_wtd_distribution",
                "Change Distribution",
                "distribution",
                "Distribution_coeff",
                "xpi_final",
                "com_price_coef",
                "New cometitor Price",
                "com_new_price",
                "com_chnage%",
                "volume",
                "re_intercept",
                "d_intercept",
            ]
        ]

        df_input.columns = [
            "Manufacturer",
            "Brand",
            "Retailer",
            "PPG",
            "Year",
            "Elasticity",
            "Price",
            "Price Flag",
            "New Price",
            "Change%",
            "Distribution",
            "Distribution Flag",
            "New Distribution",
            "Distribution Elasticity",
            "Competitor Price",
            "Competitor Price Elasticity",
            "Competitor Price Flag",
            "New Competitor Price",
            "Competitor Price Change%",
            "Volume",
            "re_Intercept",
            "Intercept",
        ]
        return df_input

    @staticmethod
    def _apply_adjustments(
        df: pd.DataFrame, adj: SimulationAdjustments
    ) -> Dict[str, float]:

        df_input = df.copy()
        base_price = df_input["Price"].mean()
        base_comp_price = df_input["Competitor Price"].mean()
        base_dist = df_input["Distribution"].mean()
        base_volume = df_input["Volume"].sum()

        e_p = df_input["Elasticity"].mean()
        e_pc = df_input["Competitor Price Elasticity"].mean()
        e_d = df_input["Distribution Elasticity"].mean()

        new_price = base_price + (base_price * (adj.price_change_pct / 100))
        new_comp_price = base_comp_price + (
            base_comp_price * (adj.competitor_price_change_pct / 100)
        )
        new_dist = adj.new_distribution if adj.new_distribution != 0.0 else base_dist

        own_pct = (new_price - base_price) / base_price if base_price else 0
        comp_pct = (
            (new_comp_price - base_comp_price) / base_comp_price
            if base_comp_price
            else 0
        )
        dist_pct = (new_dist - base_dist) / base_dist if base_dist else 0

        total_effect = e_p * own_pct + e_pc * comp_pct + e_d * dist_pct

        new_volume = base_volume * (1 + total_effect)
        new_revenue = new_volume * new_price
        old_revenue = base_volume * base_price

        dist_impact_pct = ((new_dist / base_dist) - 1) * 100
        revenue_impact_pct = ((new_revenue / old_revenue) - 1) * 100
        volume_impact_pct = ((new_volume / base_volume) - 1) * 100

        context = {
            "base_price": base_price,
            "new_price": new_price,
            "price_change_pct": float(adj.price_change_pct),
            "base_comp_price": base_comp_price,
            "new_comp_price": new_comp_price,
            "comp_price_change_pct": float(adj.competitor_price_change_pct),
            "base_distribution": base_dist,
            "new_dist": new_dist,
            "dist_impact_pct": dist_impact_pct,
            "old_volume": base_volume,
            "new_volume": new_volume,
            "volume_impact": volume_impact_pct,
            "new_revenue": new_revenue,
            "old_revenue": old_revenue,
            "revenue_impact": revenue_impact_pct,
            "price_e": e_p,
            "comp_price_e": e_pc,
            "dist_e": e_d,
        }
        return context

    def _build_cards(self, context: Dict[str, float]) -> List[MetricCard]:

        old_rev = context.get("old_revenue", 0.0)
        new_rev = context.get("new_revenue", 0.0)
        rev_change = context.get("revenue_impact", 0.0)
        old_vol = context.get("old_volume", 0.0)
        new_vol = context.get("new_volume", 0.0)
        vol_change = context.get("volume_impact", 0.0)

        return [
            MetricCard(
                label="Current Revenue", value=self._convert_to_abbreviated(old_rev)
            ),
            MetricCard(
                label="New Revenue", value=self._convert_to_abbreviated(new_rev)
            ),
            MetricCard(label="Revenue Change(%)", value=f"{round(rev_change, 2)}%"),
            MetricCard(
                label="Current Volume", value=self._convert_to_abbreviated(old_vol)
            ),
            MetricCard(label="New Volume", value=self._convert_to_abbreviated(new_vol)),
            MetricCard(label="Volume Change(%)", value=f"{round(vol_change, 2)}%"),
            MetricCard(
                label="Incremental Revenue",
                value=self._convert_to_abbreviated(new_rev - old_rev),
            ),
        ]

    @staticmethod
    def _bars(context: Dict[str, float]) -> Tuple[ComparisonBars, ComparisonBars]:
        if not context:
            empty = ComparisonBars(title="", unit="", bars=[])
            return empty, empty

        old_vol = context.get("old_volume", 0.0)
        new_vol = context.get("new_volume", 0.0)
        old_rev = context.get("old_revenue", 0.0)
        new_rev = context.get("new_revenue", 0.0)

        volume_bars = ComparisonBars(
            title="Change in Volume",
            unit="units",
            bars=[
                BarDatum(label="Current Volume", value=float(old_vol)),
                BarDatum(label="New Volume", value=float(new_vol)),
            ],
        )
        revenue_bars = ComparisonBars(
            title="Change in Revenue",
            unit="currency",
            bars=[
                BarDatum(label="Current Revenue", value=float(old_rev)),
                BarDatum(label="New Revenue", value=float(new_rev)),
            ],
        )
        return volume_bars, revenue_bars

    def _table(
        self, df_calc: pd.DataFrame, context: Dict[str, float]
    ) -> tuple[SimulationTable, SimulationTable]:
        if not context:
            return SimulationTable(columns=[], rows=[])

        df_calc["Old Revenue"] = df_calc["Volume"] * df_calc["Price"]
        table_cols = [
            "Manufacturer",
            "Brand",
            "Retailer",
            "PPG",
            "Year",
            "Elasticity",
            "Price",
            "Distribution",
            "Competitor Price Elasticity",
            "Competitor Price",
            "Volume",
            "Old Revenue",
        ]

        rows: List[Dict[str, str]] = []
        for _, row in df_calc[table_cols].iterrows():
            entry: Dict[str, str] = {}
            for col in table_cols:
                val = row[col]
                if isinstance(val, (int, float, np.number)):
                    entry[col] = f"{val:,.2f}"
                else:
                    entry[col] = str(val)
            rows.append(entry)

        flat_context = {
            "Base Price": round(context["base_price"], 3),
            "New Price": round(context["new_price"], 3),
            "Price Change (%)": round(context["price_change_pct"], 2),
            "Base Competitor Price": round(context["base_comp_price"], 3),
            "New Competitor Price": round(context["new_comp_price"], 3),
            "Comp Price Change (%)": round(context["comp_price_change_pct"], 2),
            "Base Distribution": round(context["base_distribution"], 3),
            "New Distribution": round(context["new_dist"], 3),
            "Distribution Impact (%)": round(context["dist_impact_pct"], 2),
            "Base Volume": self._convert_to_abbreviated(context["old_volume"]),
            "New Volume": self._convert_to_abbreviated(context["new_volume"]),
            "Volume Impact (%)": round(context["volume_impact"], 3),
            "Base Revenue": self._convert_to_abbreviated(context["old_revenue"]),
            "New Revenue": self._convert_to_abbreviated(context["new_revenue"]),
            "Revenue Impact (%)": round(context["revenue_impact"], 3),
            "Own Price Elasticity": round(context["price_e"], 3),
            "Competitor Price Elasticity": round(context["comp_price_e"], 3),
            "Distribution Elasticity": round(context["dist_e"], 3),
        }

        # Build table
        # df_summary = pd.DataFrame(
        #     {"Metric": list(flat_context.keys()), "Value": list(flat_context.values())}
        # )
        df_summary = pd.DataFrame([flat_context])

        context_table = SimulationTable(
            columns=list(df_summary.columns),
            rows=df_summary.astype(str).to_dict(orient="records"),
        )

        return SimulationTable(columns=table_cols, rows=rows), context_table

    def build_options(
        self, df: pd.DataFrame, filters: SimulationFilters
    ) -> SimulationOptions:

        df_base = df.copy()
        categories = (
            df_base["category"].dropna().unique().tolist()
            if "category" in df_base.columns
            else ["SurfaceCare"]
        )

        # 1) Manufacturer options -> do NOT filter by selected manufacturers
        manufacturers = sorted(df_base["manufacturer_nm"].dropna().unique().tolist())

        # 2) Brand options -> filtered by selected manufacturers, but NOT by brand itself
        df_brand_scope = df_base.copy()
        if filters.manufacturers:
            df_brand_scope = df_brand_scope[
                df_brand_scope["manufacturer_nm"].isin(filters.manufacturers)
            ]

        brands = sorted(df_brand_scope["brand_nm"].dropna().unique().tolist())

        # 3) PPG options -> filtered by manufacturer + brand
        df_ppg_scope = df_brand_scope.copy()
        if filters.brands:
            df_ppg_scope = df_ppg_scope[df_ppg_scope["brand_nm"].isin(filters.brands)]

        ppgs = sorted(df_ppg_scope["ppg_nm"].dropna().unique().tolist())

        # 4) Retailer options -> filtered by manufacturer + brand + ppg
        df_retailer_scope = df_ppg_scope.copy()
        if filters.ppgs:
            df_retailer_scope = df_retailer_scope[
                df_retailer_scope["ppg_nm"].isin(filters.ppgs)
            ]

        retailers = sorted(df_retailer_scope["retailer_id"].dropna().unique().tolist())

        return SimulationOptions(
            categories=categories,
            manufacturers=manufacturers,
            brands=brands,
            ppgs=ppgs,
            retailers=retailers,
        )

    def build_simulation(
        self, filters: SimulationFilters, adjustments: SimulationAdjustments
    ) -> SimulationResponse:

        df = self._load_df()
        df_filtered = self._apply_filters(df, filters)
        df_future = self._prepare_future_frame(df_filtered)
        df_input = self._build_base_inputs(df_future)

        context = self._apply_adjustments(df_input, adjustments)

        cards = self._build_cards(context)
        volume_bars, revenue_bars = self._bars(context)
        table, context_table = self._table(df_input, context)
        logger.info(
            "Built simulation payload | rows=%s filtered=%s",
            len(df),
            len(df_input),
        )

        return SimulationResponse(
            summary_cards=cards,
            volume_bars=volume_bars,
            revenue_bars=revenue_bars,
            table=table,
            context_table=context_table,
            context=context,
        )
