from fastapi import APIRouter, Depends, HTTPException, status

from src.services.core_service.summary import (
    SummaryFilters,
    SummaryResponse,
    Summary as SummaryService,
    FilterOptions,
)
from src.services.core_service.simulation_analysis import (
    SimulationAdjustments,
    SimulationFilters,
    SimulationResponse,
    SimulationAnalysisService,
)

router = APIRouter(prefix="/api/pricing", tags=["Pricing"])


def get_summary_service() -> SummaryService:
    return SummaryService()


def get_simulation_service() -> SimulationAnalysisService:
    return SimulationAnalysisService()


@router.post("/summary", response_model=SummaryResponse)
def summary(
    payload: SummaryFilters,
    service: SummaryService = Depends(get_summary_service),
) -> SummaryResponse:
    try:
        return service.build_summary(payload)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/options", response_model=FilterOptions)
def options(service: SummaryService = Depends(get_summary_service)) -> FilterOptions:
    try:
        df = service.load_dataframe()
        return service.build_options(df)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


class SimulationRequest(SimulationAdjustments):
    filters: SimulationFilters | None = None


@router.post("/simulation", response_model=SimulationResponse)
def simulation(
    payload: SimulationRequest,
    service: SimulationAnalysisService = Depends(get_simulation_service),
) -> SimulationResponse:
    try:
        filters = payload.filters or SimulationFilters()
        adjustments = SimulationAdjustments(
            price_change_pct=payload.price_change_pct,
            new_price=payload.new_price,
            competitor_price_change_pct=payload.competitor_price_change_pct,
            new_competitor_price=payload.new_competitor_price,
            new_distribution=payload.new_distribution,
        )
        return service.build_simulation(filters, adjustments)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
