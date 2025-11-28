# backend/src/controller/contribution_controller.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.services.core_service.contribution_service import load_and_clean_csv, apply_filters, compute_contribution

router = APIRouter(prefix="/api/contribution", tags=["Contribution"])

class ContributionRequest(BaseModel):
    ppg: Optional[List[str]] = None
    retailer: Optional[List[str]] = None
    year: Optional[List[str]] = None
    month: Optional[List[str]] = None
    sku: Optional[List[str]] = None
    group_by: Optional[str] = "ppg_nm"   # could be 'sku', 'ppg_nm', 'retailer_id', etc.
    metric: Optional[str] = "revenue"    # metric to use for contribution
    top_n: Optional[int] = 10
    include_other: Optional[bool] = True

@router.post("/compute")
def contribution_compute(payload: ContributionRequest):
    try:
        df = load_and_clean_csv()
        df_fil = apply_filters(df, payload.dict())
        if df_fil.shape[0] == 0:
            return {"table": [], "fig": None, "by_time": [], "row_count": 0}
        result = compute_contribution(df_fil,
                                      group_by=payload.group_by,
                                      metric=payload.metric,
                                      top_n=payload.top_n,
                                      include_other=payload.include_other)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
