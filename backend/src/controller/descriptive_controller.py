from fastapi import APIRouter, HTTPException, Depends, status
from src.model.response import (
    DescriptiveResponse,
    DescriptiveFilters,
    DescriptiveOptions,
)
from src.services.core_service.descriptive_service import DescriptiveAnalysis
from src.utility.logger import AppLogger

router = APIRouter(prefix="/api/trend", tags=["Trend"])
logger = AppLogger.get_logger(__name__)


def get_descriptive_service() -> DescriptiveAnalysis:
    return DescriptiveAnalysis()


@router.post("/compute", response_model=DescriptiveResponse)
def compute_descriptive_endpoint(payload: DescriptiveFilters):
    try:
        filters = payload
        service = get_descriptive_service()
        result = service.compute_descriptive(filters)
        return result
    except FileNotFoundError as e:
        logger.error(f"Some error occurred in file not found :{e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Exception:{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/options", response_model=DescriptiveOptions)
def options(
    payload: DescriptiveFilters,
    service: DescriptiveAnalysis = Depends(get_descriptive_service),
) -> DescriptiveFilters:
    try:
        filters = payload
        df = service.load_and_clean_csv()
        options = service.build_options(df, filters)
        return options
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
