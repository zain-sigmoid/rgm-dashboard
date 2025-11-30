# backend/src/services/core_service/contribution_service.py
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pydantic import BaseModel, Field

from src.utility.logger import AppLogger

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "final_pricing_consolidated_file.csv"
logger = AppLogger.get_logger(__name__)


class ContributionFilters(BaseModel):
    categories: Optional[List[str]] = None
    manufacturers: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    ppgs: Optional[List[str]] = None
    retailers: Optional[List[str]] = None


class ContributionOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    manufacturers: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)


class ElasticityBar(BaseModel):
    driver: str
    elasticity: float


class ElasticityPayload(BaseModel):
    title: str
    bars: List[ElasticityBar]


class ContributionBreakdown(BaseModel):
    categories: List[str]
    values: List[float]
    reverse_categories: List[str]
    reverse_values: List[float]
    baseline_categories: List[str]
    baseline_values: List[float]
    baseline_changes: List[float]
    percentage_changes: List[float]


class ContributionResponse(BaseModel):
    price_elasticity: ElasticityPayload
    cross_price_elasticity: ElasticityPayload
    distribution_elasticity: ElasticityPayload
    contribution_by_driver: ContributionBreakdown


class ContributionAnalysis:

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.data_path = data_path

    def load_and_clean_csv(
        self,
    ) -> pd.DataFrame:
        """
        Load CSV and perform light cleaning shared across analytical endpoints.
        Mirror the cleaning used in other services to keep parity.
        """
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
        df["Distribution_coeff"] = np.where(
            df["Distribution_coeff"] >= 1, 1, df["Distribution_coeff"]
        )
        df["year"] = pd.to_datetime(df["year"].astype(str), format="%Y")
        df["year"] = df["year"].dt.strftime("%Y")
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

        return df

    @staticmethod
    def apply_filters(df: pd.DataFrame, filters: ContributionFilters) -> pd.DataFrame:
        """
        Apply basic filters: manufacturer, brand, ppg, retailer.
        The frontend should send lists for these keys or None to skip.
        """
        df_fil = df.copy()
        if filters.categories and "category" in df_fil.columns:
            df_fil = df_fil[df_fil["category"].isin(filters.categories)]
        if filters.manufacturers and "All" not in filters.manufacturers:
            df_fil = df_fil[df_fil["manufacturer_nm"].isin(filters.manufacturers)]
        if filters.brands and "All" not in filters.brands:
            df_fil = df_fil[df_fil["brand_nm"].isin(filters.brands)]
        if filters.ppgs and "All" not in filters.ppgs:
            df_fil = df_fil[df_fil["ppg_nm"].isin(filters.ppgs)]
        if filters.retailers and "All" not in filters.retailers:
            df_fil = df_fil[df_fil["retailer_id"].isin(filters.retailers)]
        return df_fil

    def _price_elasticity(
        self, df_filtered: pd.DataFrame, df_all: pd.DataFrame
    ) -> ElasticityPayload:
        df_filtered = df_filtered.copy()
        df_all = df_all.copy()
        df_filtered["Price Elasticity"] = df_filtered["Price_coeff"]
        df_all["Price Elasticity"] = df_all["Price_coeff"]

        df_mod = (
            df_filtered.groupby(
                ["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"]
            )
            .agg(
                {
                    "Price Elasticity": "mean",
                }
            )
            .reset_index()
            .round(2)
        )
        df_mod_all = (
            df_all.groupby(["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"])
            .agg(
                {
                    "Price Elasticity": "mean",
                }
            )
            .reset_index()
            .round(2)
        )
        df_mod2 = round(df_mod_all["Price Elasticity"].mean(), 2)
        df_mod["Category Price Elasticity"] = df_mod2
        melted_df = df_mod.melt(
            id_vars=["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"],
            var_name="Drivers",
            value_name="elasticity",
        )
        melted_df_check = (
            melted_df.groupby(["Drivers"])["elasticity"].mean().reset_index().round(2)
        )
        custom_order = ["Category Price Elasticity", "Price Elasticity"]
        melted_df_check["Drivers"] = pd.Categorical(
            melted_df_check["Drivers"], categories=custom_order, ordered=True
        )
        melted_df_check = melted_df_check.sort_values(by="Drivers")
        final_res = self._serialize_elasticity("Price Elasticity", melted_df_check)
        return final_res

    def _distribution_elasticity(
        self, df_filtered: pd.DataFrame, df_all: pd.DataFrame
    ) -> ElasticityPayload:
        df_filtered = df_filtered.copy()
        df_all = df_all.copy()
        df_filtered["Distribution Elasticity"] = df_filtered["Distribution_coeff"]
        df_all["Distribution Elasticity"] = df_all["Distribution_coeff"]
        df_mod = (
            df_filtered.groupby(
                ["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"]
            )
            .agg(
                {
                    "Distribution Elasticity": "mean",
                }
            )
            .reset_index()
            .round(2)
        )
        df_mod_all = (
            df_all.groupby(["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"])
            .agg(
                {
                    "Distribution Elasticity": "mean",
                }
            )
            .reset_index()
            .round(2)
        )
        df_mod2 = round(df_mod_all["Distribution Elasticity"].mean(), 2)

        df_mod["Category Distribution Elasticity"] = df_mod2
        melted_df = df_mod.melt(
            id_vars=["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"],
            var_name="Drivers",
            value_name="elasticity",
        )
        melted_df_check = (
            melted_df.groupby(["Drivers"])["elasticity"].mean().reset_index().round(2)
        )

        custom_order = ["Category Distribution Elasticity", "Distribution Elasticity"]

        melted_df_check["Drivers"] = pd.Categorical(
            melted_df_check["Drivers"], categories=custom_order, ordered=True
        )
        melted_df_check = melted_df_check.sort_values(by="Drivers")
        final_res = self._serialize_elasticity(
            "Distribution Elasticity", melted_df_check
        )
        return final_res

    def _cross_price_elasticity(
        self, df_filtered: pd.DataFrame, df_all: pd.DataFrame
    ) -> ElasticityPayload:
        df_filtered = df_filtered.copy()
        df_all = df_all.copy()
        df_filtered["Cross Price Elasticity"] = df_filtered["com_price_coef"]
        df_all["Cross Price Elasticity"] = df_all["com_price_coef"]
        df_mod = (
            df_filtered.groupby(
                ["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"]
            )
            .agg(
                {
                    "Cross Price Elasticity": "mean",
                }
            )
            .reset_index()
            .round(2)
        )
        df_mod_all = (
            df_all.groupby(["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"])
            .agg(
                {
                    "Cross Price Elasticity": "mean",
                }
            )
            .reset_index()
            .round(2)
        )
        df_mod2 = round(df_mod_all["Cross Price Elasticity"].mean(), 2)
        df_mod["Category Cross Price Elasticity"] = df_mod2
        df_mod = df_mod[
            [
                "manufacturer_nm",
                "brand_nm",
                "retailer_id",
                "ppg_nm",
                "Category Cross Price Elasticity",
                "Cross Price Elasticity",
            ]
        ]
        melted_df = df_mod.melt(
            id_vars=["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"],
            var_name="Drivers",
            value_name="elasticity",
        )
        melted_df_check = (
            melted_df.groupby(["Drivers"])["elasticity"].mean().reset_index().round(2)
        )

        custom_order = ["Category Cross Price Elasticity", "Cross Price Elasticity"]

        # Convert the 'Drivers' column to a categorical data type with custom order
        melted_df_check["Drivers"] = pd.Categorical(
            melted_df_check["Drivers"], categories=custom_order, ordered=True
        )

        # Sort the DataFrame by the 'Drivers' column
        melted_df_check = melted_df_check.sort_values(by="Drivers")
        final_res = self._serialize_elasticity(
            "Cross Price Elasticity", melted_df_check
        )

        return final_res

    def _contribution_by_drivers(self, df: pd.DataFrame):
        df_filtered = df.copy()
        df_filtered["Baseline"] = df_filtered["baseline"]
        df_filtered["Price Driver"] = df_filtered["price_driver"]
        df_filtered["Promotion"] = df_filtered["promo"]
        df_filtered["Distribution"] = df_filtered["distribution"]
        df_filtered["Holiday"] = df_filtered["holiday"]
        df_filtered["Cannibalization"] = df_filtered["cannibalization"]
        df_filtered["Seasonality"] = df_filtered["seasonlaity"]
        df_filtered["Pantry Loading"] = df_filtered["pantry loading"]

        df_mod = (
            df_filtered.groupby(
                ["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm", "year"]
            )
            .agg(
                {
                    "Baseline": "sum",
                    "Promotion": "sum",
                    "Price Driver": "sum",
                    "Pantry Loading": "sum",
                    "Distribution": "sum",
                    "Holiday": "sum",
                    "Cannibalization": "sum",
                    "Seasonality": "sum",
                    "Price_coeff": "mean",
                    "Distribution_coeff": "mean",
                    "com_price_coef": "mean",
                }
            )
            .reset_index()
        )
        year_list = sorted(df_mod["year"].unique().tolist())[-2:]
        df_mod = df_mod[df_mod["year"].isin(year_list)]
        df_mod = pd.pivot_table(
            df_mod,
            index=["manufacturer_nm", "brand_nm", "retailer_id", "ppg_nm"],
            columns=["year"],
            values=[
                "Baseline",
                "Promotion",
                "Price Driver",
                "Pantry Loading",
                "Distribution",
                "Holiday",
                "Cannibalization",
                "Seasonality",
                "Price_coeff",
                "Distribution_coeff",
                "com_price_coef",
            ],
        ).reset_index()

        new_cols = [("{1} {0}".format(*tup)) for tup in df_mod.columns]

        df_mod.columns = new_cols

        df_mod.columns = df_mod.columns.str.replace(" ", "")

        df_mod["total_Baseline_" + str(year_list[0])] = (
            df_mod[str(year_list[0]) + "Baseline"]
            + df_mod[str(year_list[0]) + "Cannibalization"]
            + df_mod[str(year_list[0]) + "Distribution"]
            + df_mod[str(year_list[0]) + "Holiday"]
            + df_mod[str(year_list[0]) + "PantryLoading"]
            + df_mod[str(year_list[0]) + "PriceDriver"]
            + df_mod[str(year_list[0]) + "Seasonality"]
        )

        df_mod["total_Baseline_" + str(year_list[1])] = (
            df_mod[str(year_list[1]) + "Baseline"]
            + df_mod[str(year_list[1]) + "Cannibalization"]
            + df_mod[str(year_list[1]) + "Distribution"]
            + df_mod[str(year_list[1]) + "Holiday"]
            + df_mod[str(year_list[1]) + "PantryLoading"]
            + df_mod[str(year_list[1]) + "PriceDriver"]
            + df_mod[str(year_list[1]) + "Seasonality"]
        )
        df_mod["baseline_diff"] = (
            df_mod["total_Baseline_" + str(year_list[1])]
            - df_mod["total_Baseline_" + str(year_list[0])]
        )

        np.random.seed(10)
        df_mod["price_contri"] = 0.35 + (0.9 - 0.35) * np.random.rand(df_mod.shape[0])
        df_mod["price_contri"] = df_mod["price_contri"] * -1
        df_mod["distribution_contri"] = 0.36 + (0.8 - 0.36) * np.random.rand(
            df_mod.shape[0]
        )
        df_mod["com_price_contri"] = 1 - (
            df_mod["price_contri"] + df_mod["distribution_contri"]
        )
        df_mod["Price_Driver"] = df_mod["baseline_diff"] * df_mod["price_contri"]
        df_mod["Distribution"] = df_mod["baseline_diff"] * df_mod["distribution_contri"]
        df_mod["Cannibalization"] = df_mod["baseline_diff"] * df_mod["com_price_contri"]

        df_mod["baseline_total_diff"] = (
            df_mod["Price_Driver"] + df_mod["Distribution"] + df_mod["Cannibalization"]
        )

        Baseline_22 = df_mod["total_Baseline_" + str(year_list[1])].sum()
        Baseline_21 = df_mod["total_Baseline_" + str(year_list[0])].sum()
        Price_Driver = df_mod["Price_Driver"].sum()
        Distribution = df_mod["Distribution"].sum()
        Cannibalization = df_mod["Cannibalization"].sum()

        baseline_diff = ((Baseline_22 / Baseline_21) - 1) * 100
        price_diff = (
            df_mod["price_contri"].mean() * 100 * ((Baseline_22 / Baseline_21) - 1)
        )
        dist_diff = (
            df_mod["distribution_contri"].mean()
            * 100
            * ((Baseline_22 / Baseline_21) - 1)
        )
        com_price_diff = (
            df_mod["com_price_contri"].mean() * 100 * ((Baseline_22 / Baseline_21) - 1)
        )
        percentage_changes = [dist_diff, com_price_diff]
        baseline_ch = [price_diff, baseline_diff]
        cat_baseline = ["Own Price", "Baseline" + " " + str(year_list[1])]
        val_baseline = [Baseline_21, Baseline_22]
        categories = [
            "Baseline" + " " + str(year_list[0]),
            "Own Price",
            "Own Distribution",
            "Competitor Price",
            "Baseline" + " " + str(year_list[1]),
        ]
        values = [Baseline_21, Price_Driver, Distribution, Cannibalization, Baseline_22]
        values2 = [
            Baseline_22,
            -Cannibalization,
            -Distribution,
            -Price_Driver,
            Baseline_21,
        ]
        categories2 = [
            "Baseline" + " " + str(year_list[1]),
            "Competitor Price",
            "Own Distribution",
            "Own Price",
            "Baseline" + " " + str(year_list[0]),
        ]

        return ContributionBreakdown(
            categories=categories,
            values=[float(v) for v in values],
            reverse_categories=categories2,
            reverse_values=[float(v) for v in values2],
            baseline_categories=cat_baseline,
            baseline_values=[float(v) for v in val_baseline],
            baseline_changes=[float(v) for v in baseline_ch],
            percentage_changes=[float(v) for v in percentage_changes],
        )

    def _build_options(self, df: pd.DataFrame) -> ContributionOptions:
        return ContributionOptions(
            categories=(
                sorted(df["category"].dropna().unique().tolist())
                if "category" in df.columns
                else []
            ),
            manufacturers=sorted(df["manufacturer_nm"].dropna().unique().tolist()),
            brands=sorted(df["brand_nm"].dropna().unique().tolist()),
            ppgs=sorted(df["ppg_nm"].dropna().unique().tolist()),
            retailers=sorted(df["retailer_id"].dropna().unique().tolist()),
        )

    def _serialize_elasticity(
        self, title: str, elasticity_df: pd.DataFrame
    ) -> ElasticityPayload:
        bars = [
            ElasticityBar(
                driver=str(row["Drivers"]),
                elasticity=float(row["elasticity"]),
            )
            for _, row in elasticity_df.iterrows()
        ]
        return ElasticityPayload(title=title, bars=bars)

    def build_options(
        self, df: pd.DataFrame, filters: ContributionFilters
    ) -> ContributionOptions:
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

        return ContributionOptions(
            categories=categories,
            manufacturers=manufacturers,
            brands=brands,
            ppgs=ppgs,
            retailers=retailers,
        )

    def compute_contribution(
        self,
        filters: ContributionFilters | Dict[str, Any],
    ) -> ContributionResponse:
        df_all = self.load_and_clean_csv()
        filters_model = (
            filters
            if isinstance(filters, ContributionFilters)
            else ContributionFilters(**(filters or {}))
        )
        df_filtered = self.apply_filters(df_all, filters_model)
        price_e = self._price_elasticity(df_filtered, df_all)
        cross_price_e = self._cross_price_elasticity(df_filtered, df_all)
        distribution_e = self._distribution_elasticity(df_filtered, df_all)
        contri_by_driver = self._contribution_by_drivers(df_filtered)
        logger.info("Contribution Analysis done ")
        return ContributionResponse(
            price_elasticity=price_e,
            cross_price_elasticity=cross_price_e,
            distribution_elasticity=distribution_e,
            contribution_by_driver=contri_by_driver,
        )
