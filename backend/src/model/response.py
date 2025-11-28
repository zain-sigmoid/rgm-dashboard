"""
This file contains models used across backend
"""

from pydantic import BaseModel
from typing import Optional, Any, List, Dict


class Response(BaseModel):
    # to be implemented
    pass

class DescriptiveRequest(BaseModel):
    ppg: Optional[List[str]] = None
    retailer: Optional[List[str]] = None
    year: Optional[List[str]] = None
    month: Optional[List[str]] = None
    date_freq: Optional[str] = "M"
    top_n: Optional[int] = 10

class DescriptiveResponse(BaseModel):
    timeseries: List[Dict[str, Any]]
    top_table: List[Dict[str, Any]]
    fig: Optional[Dict[str, Any]]
    row_count: int
