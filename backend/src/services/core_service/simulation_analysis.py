from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from src.utility.logger import AppLogger

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "final_pricing_consolidated_file.csv"
logger = AppLogger.get_logger(__name__)


def _convert_to_abbreviated(num: float) -> str:
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


class SimulationFilters(BaseModel):
    categories: Optional[List[str]] = Field(default=None)
    manufacturers: Optional[List[str]] = Field(default=None)
    brands: Optional[List[str]] = Field(default=None)
    ppgs: Optional[List[str]] = Field(default=None)
    retailers: Optional[List[str]] = Field(default=None)


class SimulationAdjustments(BaseModel):
    price_change_pct: float = 0.0
    new_price: Optional[float] = None
    competitor_price_change_pct: float = 0.0
    new_competitor_price: Optional[float] = None
    new_distribution: Optional[float] = None


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
    adjustments: SimulationAdjustments
    filters_applied: SimulationFilters
    summary_cards: List[MetricCard]
    volume_bars: ComparisonBars
    revenue_bars: ComparisonBars
    table: SimulationTable
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
        retailer_map = {
            "Target PT": "Target",
            "Publix Total TA": "Publix",
            "CVS Total Corp ex HI TA": "CVS",
        }
        df["retailer_id"] = df["retailer_id"].replace(retailer_map).str.upper()
        df["year"] = pd.to_datetime(df["year"].astype(str), format="%Y").dt.strftime(
            "%Y"
        )
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
    def _apply_filters(df: pd.DataFrame, filters: SimulationFilters) -> pd.DataFrame:
        df_fil = df.copy()
        # if filters.categories and "All" not in filters.categories:
        #     if "category" in df_fil.columns:
        #         df_fil = df_fil[df_fil["category"].isin(filters.categories)]
        #     else:
        #         logger.warning(
        #             "Category filter provided but 'category' column not found; skipping category filter."
        #         )
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

        latest_year = df_fil["year"].max()
        if "week" in df_fil.columns:
            week_mask = df_fil["week"].eq(52)
        else:
            week_mask = pd.Series([False] * len(df_fil), index=df_fil.index)

        price_latest = df_fil[(df_fil["year"] == latest_year) & week_mask]
        price_latest = price_latest[["ppg_nm", "retailer_id", "price"]].rename(
            columns={"price": "price_latest"}
        )

        df_new = df_fil[df_fil["year"].isin(["2021", "2022"])].copy()
        df_new["year"] = df_new["year"].replace({"2021": 2023, "2022": 2024})
        df_new = df_new[df_new["year"] == 2024]

        df_future = pd.merge(
            df_new, price_latest, on=["ppg_nm", "retailer_id"], how="left"
        )
        df_future["price"] = df_future["price_latest"].fillna(df_future["price"])

        grouped = (
            df_future.groupby(
                ["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm", "year"],
                dropna=False,
            )
            .agg(
                Price_coeff=("Price_coeff", "mean"),
                price=("price", "mean"),
                acv_wtd_distribution=("acv_wtd_distribution", "mean"),
                Distribution_coeff=("Distribution_coeff", "mean"),
                xpi_final=("xpi_final", "mean"),
                com_price_coef=("com_price_coef", "mean"),
                re_intercept=("re_intercept", "mean"),
                d_intercept=("d_intercept", "mean"),
                volume=("volume", "sum"),
            )
            .reset_index()
        )
        return grouped

    @staticmethod
    def _build_base_inputs(df_future: pd.DataFrame) -> pd.DataFrame:
        df = df_future.copy()
        df["new_price"] = np.nan
        df["change_pct"] = np.nan
        df["comp_new_price"] = np.nan
        df["comp_change_pct"] = np.nan
        df["new_distribution"] = np.nan

        df_input = df[
            [
                "manufacturer_nm",
                "brand_nm",
                "retailer_id",
                "ppg_nm",
                "year",
                "Price_coeff",
                "price",
                "acv_wtd_distribution",
                "Distribution_coeff",
                "xpi_final",
                "com_price_coef",
                "re_intercept",
                "d_intercept",
                "volume",
            ]
        ].copy()

        df_input.columns = [
            "Manufacturer",
            "Brand",
            "Retailer",
            "PPG",
            "Year",
            "Elasticity",
            "Price",
            "Distribution",
            "Distribution Elasticity",
            "Competitor Price",
            "Competitor Price Elasticity",
            "re_Intercept",
            "Intercept",
            "Volume",
        ]
        df_input["Intercept"] = df_input["Intercept"].abs()
        df_input["re_Intercept"] = df_input["re_Intercept"].abs()
        return df_input

    @staticmethod
    def _apply_adjustments(
        df_input: pd.DataFrame, adj: SimulationAdjustments
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        df = df_input.copy()

        base_price = float(df["Price"].mean()) if not df.empty else 0.0
        base_comp_price = float(df["Competitor Price"].mean()) if not df.empty else 0.0
        base_distribution = float(df["Distribution"].mean()) if not df.empty else 0.0
        # Price adjustments (match Streamlit: if no change, keep per-row price; else use global scalar)
        if adj.new_price is None and adj.price_change_pct == 0:
            df["New Price"] = df["Price"]
        else:
            scalar_new_price = (
                adj.new_price
                if adj.new_price is not None
                else base_price * (1 + adj.price_change_pct / 100)
            )
            df["New Price"] = scalar_new_price

        # Competitor price adjustments
        if adj.new_competitor_price is None and adj.competitor_price_change_pct == 0:
            df["New Competitor Price"] = df["Competitor Price"]
        else:
            scalar_new_comp = (
                adj.new_competitor_price
                if adj.new_competitor_price is not None
                else base_comp_price * (1 + adj.competitor_price_change_pct / 100)
            )
            df["New Competitor Price"] = scalar_new_comp

        # Distribution adjustments
        if adj.new_distribution is None:
            df["New Distribution"] = df["Distribution"]
        else:
            df["New Distribution"] = adj.new_distribution

        df["Change%"] = np.where(
            df["Price"] == 0,
            0,
            ((df["New Price"] / df["Price"]) - 1) * 100,
        )
        df["Competitor Price Change%"] = np.where(
            df["Competitor Price"] == 0,
            0,
            ((df["New Competitor Price"] / df["Competitor Price"]) - 1) * 100,
        )
        df["New Distribution Change%"] = np.where(
            df["Distribution"] == 0,
            0,
            ((df["New Distribution"] / df["Distribution"]) - 1) * 100,
        )

        df["New Volume"] = df["Volume"] * (
            1
            + ((df["Change%"] / 100) * df["Elasticity"])
            + (
                (df["Competitor Price Change%"] / 100)
                * df["Competitor Price Elasticity"]
            )
            + ((df["New Distribution Change%"] / 100) * df["Distribution Elasticity"])
        )

        df["Volume Impact(%)"] = ((df["New Volume"] / df["Volume"]) - 1) * 100
        df["Old Revenue"] = df["Volume"] * df["Price"]
        df["New Revenue"] = df["New Volume"] * df["New Price"]
        df["Revenue Impact(%)"] = ((df["New Revenue"] / df["Old Revenue"]) - 1) * 100
        df["Incremental Revenue"] = df["New Revenue"] - df["Old Revenue"]

        new_price_mean = float(df["New Price"].mean()) if not df.empty else 0.0
        new_comp_price_mean = (
            float(df["New Competitor Price"].mean()) if not df.empty else 0.0
        )
        new_distribution_mean = (
            float(df["New Distribution"].mean()) if not df.empty else 0.0
        )

        context = {
            "base_price": base_price,
            "new_price": new_price_mean,
            "price_change_pct": float(adj.price_change_pct),
            "base_comp_price": base_comp_price,
            "new_comp_price": new_comp_price_mean,
            "comp_price_change_pct": float(adj.competitor_price_change_pct),
            "base_distribution": base_distribution,
            "new_distribution": new_distribution_mean,
            "distribution_change_pct": (
                float(((new_distribution_mean / base_distribution) - 1) * 100)
                if base_distribution
                else 0.0
            ),
        }
        return df, context

    @staticmethod
    def _build_cards(df_calc: pd.DataFrame) -> List[MetricCard]:
        if df_calc.empty:
            return []

        old_rev = df_calc["Old Revenue"].sum()
        new_rev = df_calc["New Revenue"].sum()
        rev_change = df_calc["Revenue Impact(%)"].mean()
        old_vol = df_calc["Volume"].sum()
        new_vol = df_calc["New Volume"].sum()
        vol_change = df_calc["Volume Impact(%)"].mean()

        return [
            MetricCard(label="Current Revenue", value=_convert_to_abbreviated(old_rev)),
            MetricCard(label="New Revenue", value=_convert_to_abbreviated(new_rev)),
            MetricCard(label="Revenue Change(%)", value=f"{round(rev_change, 2)}%"),
            MetricCard(label="Current Volume", value=_convert_to_abbreviated(old_vol)),
            MetricCard(label="New Volume", value=_convert_to_abbreviated(new_vol)),
            MetricCard(label="Volume Change(%)", value=f"{round(vol_change, 2)}%"),
            MetricCard(
                label="Incremental Revenue",
                value=_convert_to_abbreviated(new_rev - old_rev),
            ),
        ]

    @staticmethod
    def _bars(df_calc: pd.DataFrame) -> Tuple[ComparisonBars, ComparisonBars]:
        if df_calc.empty:
            empty = ComparisonBars(title="", unit="", bars=[])
            return empty, empty

        old_vol = df_calc["Volume"].sum()
        new_vol = df_calc["New Volume"].sum()
        old_rev = df_calc["Old Revenue"].sum()
        new_rev = df_calc["New Revenue"].sum()

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

    @staticmethod
    def _table(df_calc: pd.DataFrame) -> SimulationTable:
        if df_calc.empty:
            return SimulationTable(columns=[], rows=[])

        table_cols = [
            "Manufacturer",
            "Brand",
            "Retailer",
            "PPG",
            "Year",
            "Elasticity",
            "Price",
            "New Price",
            "Change%",
            "Distribution",
            "New Distribution",
            "New Distribution Change%",
            "Competitor Price Elasticity",
            "Competitor Price",
            "New Competitor Price",
            "Competitor Price Change%",
            "Volume",
            "New Volume",
            "Volume Impact(%)",
            "Incremental Revenue",
            "Old Revenue",
            "New Revenue",
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

        return SimulationTable(columns=table_cols, rows=rows)

    def build_options(
        self, df: pd.DataFrame, filters: SimulationFilters
    ) -> SimulationOptions:
        selected_manufacturers = filters.manufacturers or []
        selected_brands = filters.brands or []

        # Categories (independent)
        categories = (
            df["category"].dropna().unique().tolist()
            if "category" in df.columns
            else ["SurfaceCare"]
        )
        manufacturers = (
            sorted(df["manufacturer_nm"].dropna().unique().tolist())
            if "manufacturer_nm" in df.columns
            else []
        )

        # ---------- 1) FILTER FOR BRANDS (depends ONLY on manufacturers) ----------
        if selected_manufacturers:
            df_for_brands = df[df["manufacturer_nm"].isin(selected_manufacturers)]
        else:
            df_for_brands = df

        if "brand_nm" in df.columns:
            brands = sorted(df_for_brands["brand_nm"].dropna().unique().tolist())
        else:
            brands = []

        # ---------- 2) FILTER FOR PPGs + RETAILERS (depends on manufacturers + brands) ----------
        df_for_ppg = df_for_brands

        if selected_brands:
            df_for_ppg = df_for_ppg[df_for_ppg["brand_nm"].isin(selected_brands)]

        if "ppg_nm" in df.columns:
            ppgs = sorted(df_for_ppg["ppg_nm"].dropna().unique().tolist())
        else:
            ppgs = []

        if "retailer_id" in df.columns:
            retailers = sorted(df_for_ppg["retailer_id"].dropna().unique().tolist())
        else:
            retailers = []

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
        df_calc, context = self._apply_adjustments(df_input, adjustments)

        cards = self._build_cards(df_calc)
        volume_bars, revenue_bars = self._bars(df_calc)
        table = self._table(df_calc)

        logger.info(
            "Built simulation payload | rows=%s filtered=%s",
            len(df),
            len(df_calc),
        )

        return SimulationResponse(
            adjustments=adjustments,
            filters_applied=filters,
            summary_cards=cards,
            volume_bars=volume_bars,
            revenue_bars=revenue_bars,
            table=table,
            context=context,
        )
