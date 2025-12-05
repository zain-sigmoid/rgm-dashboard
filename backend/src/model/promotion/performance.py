from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class PerformanceFilters(BaseModel):
    categories: Optional[List[str]] = Field(default=None)
    brands: Optional[List[str]] = Field(default=None)
    ppgs: Optional[List[str]] = Field(default=None)
    retailers: Optional[List[str]] = Field(default=None)
    segment: Optional[List[str]] = Field(default=None)
    offer_type: Optional[List[str]] = Field(default=None)
    promo_tactics: Optional[List[str]] = Field(default=None)
    year: Optional[List[int]] = Field(
        default=None,
    )
    month: Optional[List[int]] = Field(default=None)


class FilterOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)
    segment: List[str] = Field(default=None)
    offer_type: List[str] = Field(default_factory=list)
    promo_tactics: List[str] = Field(default_factory=list)
    year: List[int] = Field(default_factory=list)
    month: List[int] = Field(default_factory=list)


class KPI(BaseModel):
    label: str
    value: int | float | str


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
    metrics: List[KPI]
    mechanics: DFTable
    ppg: DFTable
    subsegment: DFTable
    retailer: DFTable
