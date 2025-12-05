from src.services.optimal_promotion_service.performance_analysis import (
    PerformanceAnalysis,
)
from src.services.optimal_promotion_service.past_promotion_analysis import (
    PastPromotionAnalysis,
)
from src.services.optimal_promotion_service.simulator import (
    SimulationAnalysis,
)


class OptimalPromotion:
    @staticmethod
    def get_performance_analysis() -> PerformanceAnalysis:
        return PerformanceAnalysis()

    @staticmethod
    def get_past_performance_analysis() -> PastPromotionAnalysis:
        return PastPromotionAnalysis()

    @staticmethod
    def get_simulation() -> SimulationAnalysis:
        return SimulationAnalysis()
