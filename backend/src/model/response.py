"""
This file contains models used across backend
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict


class Response(BaseModel):
    # to be implemented
    pass


class DescriptiveFilters(BaseModel):
    categories: Optional[List[str]] = None
    manufacturers: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    ppgs: Optional[List[str]] = None
    retailers: Optional[List[str]] = None
    years: Optional[List[str]] = None
    months: Optional[List[int]] = None
    date_freq: Optional[str] = "M"
    include_competitor: bool = True
    competitor_manufacturers: Optional[List[str]] = None
    competitor_brands: Optional[List[str]] = None
    competitor_ppgs: Optional[List[str]] = None
    competitor_retailers: Optional[List[str]] = None


class DescriptiveRequest(BaseModel):
    filters: DescriptiveFilters | None = None


class TimeSeriesPoint(BaseModel):
    date: str
    volume: float
    revenue: Optional[float] = None
    price: Optional[float] = None
    distribution: Optional[float] = None
    competitor_price: Optional[float] = None
    competitor_distribution: Optional[float] = None


class TopTableEntry(BaseModel):
    sku: Optional[str] = None
    ppg_nm: Optional[str] = None
    volume: float
    revenue: float


class DescriptiveResponse(BaseModel):
    volume_vs_revenue: List[TimeSeriesPoint]
    volume_vs_price: List[TimeSeriesPoint]
    volume_vs_distribution: List[TimeSeriesPoint]
    competitor_price: List[TimeSeriesPoint]
    competitor_distribution: List[TimeSeriesPoint]
    # top_table: List[TopTableEntry]
    row_count: int


class DescriptiveOptions(BaseModel):
    categories: List[str] = Field(default_factory=list)
    manufacturers: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)
    ppgs: List[str] = Field(default_factory=list)
    retailers: List[str] = Field(default_factory=list)
    years: List[str] = Field(default_factory=list)
    competitor_manufacturers: List[str] = Field(default_factory=list)
    competitor_brands: List[str] = Field(default_factory=list)
    competitor_ppgs: List[str] = Field(default_factory=list)
    competitor_retailers: List[str] = Field(default_factory=list)
    date_freq: str = "M"
