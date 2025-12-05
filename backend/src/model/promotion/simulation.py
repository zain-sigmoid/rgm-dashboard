import datetime
import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GlobalFilters(BaseModel):
    """Filters applied to the dataset before simulation logic."""

    categories: Optional[List[str]] = Field(default=None)
    brands: Optional[List[str]] = Field(default=None)
    segment: Optional[List[str]] = Field(default=None)
    ppgs: Optional[List[str]] = Field(default=None)
    retailers: Optional[List[str]] = Field(default=None)


class SimulationEventFilters(BaseModel):
    """Represents one row of user input for a promotion event."""

    promo_tactic: Optional[List[str]] = Field(default=None)
    offer_type: Optional[List[str]] = Field(default=None)
    offer_mechanic: Optional[List[str]] = Field(default=None)
    start_date: Optional[datetime.date] = None
    duration: Optional[int] = None
    discount: Optional[float] = None
    redemption_rate: Optional[float] = None


class SimulationOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)
    segment: List[str] = Field(default=None)
    offer_type: List[str] = Field(default_factory=list)
    promo_tactics: List[str] = Field(default_factory=list)
    offer_mechanic: List[str] = Field(default_factory=list)


class SalesLinePoint(BaseModel):
    label: str
    baseline_sales: float
    promo_sales: float


class DFTable(BaseModel):
    columns: List[str]
    rows: List[Dict[str, str]]


class PieSegment(BaseModel):
    name: str  # "Baseline" or "Incremental"
    value: float  # sales


class PieChart(BaseModel):
    label: str
    total_sales: float
    segments: List[PieSegment]


class EventROI(BaseModel):
    promo_index: int
    roi: float


class SimulationResponse(BaseModel):
    baseline_vs_promo: List[SalesLinePoint]
    pie_chart: PieChart
    df_table: DFTable
    events: List[EventROI]
