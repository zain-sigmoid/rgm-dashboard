from fastapi import APIRouter, Depends, HTTPException, status

from src.utility.logger import AppLogger
from src.services.smart_pricing_service.summary import (
    SummaryFilters,
    SummaryResponse,
    Summary as SummaryService,
    FilterOptions,
)
from src.services.smart_pricing_service.simulation_analysis import (
    SimulationAdjustments,
    SimulationFilters,
    SimulationResponse,
    SimulationAnalysisService,
    SimulationOptions,
)
from src.services.smart_pricing_service.contribution_analysis import (
    ContributionAnalysis,
    ContributionFilters,
    ContributionOptions,
    ContributionResponse,
)

from src.model.response import (
    DescriptiveResponse,
    DescriptiveFilters,
    DescriptiveOptions,
)
from src.services.smart_pricing_service.descriptive_analysis import DescriptiveAnalysis

router = APIRouter(prefix="/api/pricing", tags=["Pricing"])
logger = AppLogger.get_logger(__name__)


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


@router.post("/options", response_model=FilterOptions)
def options(
    payload: SummaryFilters, service: SummaryService = Depends(get_summary_service)
) -> FilterOptions:
    try:
        filters = payload
        df = service.load_dataframe()
        return service.build_options(df, filters)
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


@router.post("/simulation/options", response_model=SimulationOptions)
def options(
    payload: SimulationFilters,
    service: SimulationAnalysisService = Depends(get_simulation_service),
) -> SimulationOptions:
    try:
        filters = payload
        df = service._load_df()
        return service.build_options(df, filters)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ======================== Contribution Tab ===============================
def get_contribution_service() -> ContributionAnalysis:
    return ContributionAnalysis()


@router.post("/contribution", response_model=ContributionResponse)
def contribution_compute(
    payload: ContributionFilters,
    service: ContributionAnalysis = Depends(get_contribution_service),
):
    try:
        filters = payload
        result = service.compute_contribution(filters=filters)
        return result
    except FileNotFoundError as e:
        logger.error("File was not found in contribution analysis")
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        logger.error("Error occurred in computation in contribution analysis")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exception Occurred : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contribution/options", response_model=ContributionOptions)
def options(
    payload: ContributionFilters,
    service: ContributionAnalysis = Depends(get_contribution_service),
) -> ContributionOptions:
    try:
        filters = payload
        df = service.load_and_clean_csv()
        return service.build_options(df, filters)
    except FileNotFoundError as exc:
        logger.error("File Not Found at Contribution Analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ======================== Trend Tab ===============================
def get_descriptive_service() -> DescriptiveAnalysis:
    return DescriptiveAnalysis()


@router.post("/trend", response_model=DescriptiveResponse)
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


@router.post("/trend/options", response_model=DescriptiveOptions)
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
