from fastapi import APIRouter, HTTPException
from src.model.response import DescriptiveRequest, DescriptiveResponse
from src.services.core_service.descriptive_service import compute_descriptive
from typing import Dict

router = APIRouter(prefix="/api/trend", tags=["Trend"])

@router.post("/compute", response_model=DescriptiveResponse)
def compute_descriptive_endpoint(payload: DescriptiveRequest):
    try:
        filters: Dict = payload.dict()
        result = compute_descriptive(filters)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
