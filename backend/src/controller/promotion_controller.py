from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from io import StringIO

from src.services.optimal_promotion_service.main import OptimalPromotion as op
from src.services.optimal_promotion_service.performance_analysis import (
    PerformanceAnalysis,
)
from src.services.optimal_promotion_service.past_promotion_analysis import (
    PastPromotionAnalysis,
)
from src.services.optimal_promotion_service.simulator import (
    SimulationAnalysis,
)
from src.model.promotion.performance import (
    PerformanceFilters,
    PerformanceResponse,
    FilterOptions,
)
from src.model.promotion.past_promotion import (
    PastPromotionFilters,
    PastPromotionOptions,
    PastPromotionResponse,
)
from src.model.promotion.simulation import (
    GlobalFilters,
    SimulationEventFilters,
    SimulationOptions,
    SimulationResponse,
)
from src.utility.logger import AppLogger

router = APIRouter(prefix="/api/promotion", tags=["Promotion"])
logger = AppLogger.get_logger(__name__)


@router.post("/performance", response_model=PerformanceResponse)
def performance(
    payload: PerformanceFilters,
    service: PerformanceAnalysis = Depends(op.get_performance_analysis),
) -> PerformanceResponse:
    try:
        result = service.build_performance(filters=payload)
        return result
    except FileNotFoundError as exc:
        logger.error(f"File was not found in Performance:{exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as e:
        logger.error(f"Exception Occurred : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/{table_name}")
def export_table_csv(
    table_name: str,
    filters: PerformanceFilters,
    service: PerformanceAnalysis = Depends(op.get_performance_analysis),
):
    try:
        df = service.load_table(filters, table_name)
    except ValueError as exc:
        logger.error(f"Exception Occurred")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        logger.error(f"File was not found in Performance:{exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    stream = StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    headers = {"Content-Disposition": f'attachment; filename="{table_name}.csv"'}

    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers=headers,
    )


@router.post("/performance/options", response_model=FilterOptions)
def options(
    payload: PerformanceFilters,
    service: PerformanceAnalysis = Depends(op.get_performance_analysis),
) -> FilterOptions:
    try:
        filters = payload
        df = service._load_df()
        response = service.build_options(df=df, filters=filters)
        return response
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ======================= Past Promotion Routes ===========================


@router.post("/past-promotion", response_model=PastPromotionResponse)
def promotion(
    payload: PastPromotionFilters,
    service: PastPromotionAnalysis = Depends(op.get_past_performance_analysis),
) -> PastPromotionResponse:
    try:
        result = service.build_past_performance(filters=payload)
        return result
    except FileNotFoundError as exc:
        logger.error(f"File was not found in past promotion:{exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as e:
        logger.error(f"Exception Occurred : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/past-promotion/options", response_model=PastPromotionOptions)
def promotion_options(
    payload: PastPromotionFilters,
    service: PastPromotionAnalysis = Depends(op.get_past_performance_analysis),
) -> PastPromotionOptions:
    try:
        filters = payload
        df = service._load_and_clean_df()
        response = service.build_options(df=df, filters=filters)
        return response
    except FileNotFoundError as exc:
        logger.error("File was not found in promotion")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ======================= Simulation Routes ===========================


@router.post("/simulation", response_model=SimulationResponse)
def promotion(
    payload: dict,
    service: SimulationAnalysis = Depends(op.get_simulation),
) -> SimulationResponse:
    try:
        global_filters = GlobalFilters(**(payload.get("filters") or {}))
        event_filters_raw = payload.get("event_filters") or []
        event_filters = [SimulationEventFilters(**ev) for ev in event_filters_raw]
        result = service.run_simulation(
            global_filters=global_filters, event_filters=event_filters
        )
        return result
    except FileNotFoundError as exc:
        logger.error(f"File was not found in past promotion:{exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as e:
        logger.error(f"Exception Occurred : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation/options", response_model=SimulationOptions)
def promotion_options(
    payload: GlobalFilters,
    service: SimulationAnalysis = Depends(op.get_simulation),
) -> SimulationOptions:
    try:
        filters = payload
        response = service.build_options(filters=filters)
        return response
    except FileNotFoundError as exc:
        logger.error("File was not found in simulation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
