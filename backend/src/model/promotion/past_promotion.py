from pydantic import BaseModel, Field
from typing import List, Optional, Union


class PastPromotionFilters(BaseModel):
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


class PastPromotionOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)
    segment: List[str] = Field(default=None)
    offer_type: List[str] = Field(default_factory=list)
    promo_tactics: List[str] = Field(default_factory=list)
    year: List[int] = Field(default_factory=list)
    month: List[int] = Field(default_factory=list)


class DualLine(BaseModel):
    x: Union[str, float, int]
    avg_baseline: float
    avg_total_volume: float


class ComboChart(BaseModel):
    uplift: float
    avg_roi: float
    promo_depth: Optional[str] = None
    offer_mechanic: Optional[str] = None
    promo_tactic: Optional[str] = None


class KPI(BaseModel):
    label: str
    value: int | float | str


class PastPromotionResponse(BaseModel):
    metrics: List[KPI]
    volume_vs_baseline: List[DualLine]
    uplift_vs_discount: List[ComboChart]
    uplift_vs_offer: List[ComboChart]
    uplift_vs_promo: List[ComboChart]
