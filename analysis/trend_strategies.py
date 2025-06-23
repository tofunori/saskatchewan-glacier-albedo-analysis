"""
Strategy pattern for trend analysis calculations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
import logging

from utils.exceptions import AnalysisError
from utils.helpers import perform_mann_kendall_test, calculate_sen_slope

logger = logging.getLogger(__name__)


@dataclass
class TrendResult:
    """Result of a trend analysis."""
    test_name: str
    statistic: float
    p_value: float
    slope: Optional[float] = None
    trend_direction: Optional[str] = None
    significance: Optional[str] = None
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if trend is statistically significant."""
        return self.p_value < alpha


class TrendStrategy(ABC):
    """Abstract base class for trend calculation strategies."""
    
    @abstractmethod
    def calculate(self, data: pd.Series) -> TrendResult:
        """Calculate trend for given data series.
        
        Args:
            data: Time series data
            
        Returns:
            TrendResult object with analysis results
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass


class MannKendallStrategy(TrendStrategy):
    """Mann-Kendall trend test strategy."""
    
    def __init__(self, alpha: float = 0.05):
        """Initialize with significance level."""
        self.alpha = alpha
    
    def calculate(self, data: pd.Series) -> TrendResult:
        """Calculate Mann-Kendall trend test."""
        try:
            # Clean data - remove NaN values
            clean_data = data.dropna()
            
            if len(clean_data) < 3:
                raise AnalysisError(f"Insufficient data for Mann-Kendall test: {len(clean_data)} points")
            
            # Perform Mann-Kendall test
            tau, p_value = perform_mann_kendall_test(clean_data.values)
            
            # Determine trend direction
            if p_value < self.alpha:
                direction = "increasing" if tau > 0 else "decreasing"
                significance = "significant"
            else:
                direction = "no_trend"
                significance = "not_significant"
            
            return TrendResult(
                test_name="Mann-Kendall",
                statistic=tau,
                p_value=p_value,
                trend_direction=direction,
                significance=significance
            )
            
        except Exception as e:
            logger.error(f"Mann-Kendall calculation failed: {e}")
            raise AnalysisError(f"Mann-Kendall test failed: {e}")
    
    def get_name(self) -> str:
        return "Mann-Kendall"


class SenSlopeStrategy(TrendStrategy):
    """Sen's slope trend estimation strategy."""
    
    def calculate(self, data: pd.Series) -> TrendResult:
        """Calculate Sen's slope."""
        try:
            # Clean data
            clean_data = data.dropna()
            
            if len(clean_data) < 3:
                raise AnalysisError(f"Insufficient data for Sen's slope: {len(clean_data)} points")
            
            # Calculate Sen's slope
            slope = calculate_sen_slope(clean_data.values)
            
            # Determine trend direction from slope
            if abs(slope) < 1e-10:  # Near zero
                direction = "no_trend"
            else:
                direction = "increasing" if slope > 0 else "decreasing"
            
            return TrendResult(
                test_name="Sen's Slope",
                statistic=slope,
                p_value=np.nan,  # Sen's slope doesn't provide p-value
                slope=slope,
                trend_direction=direction
            )
            
        except Exception as e:
            logger.error(f"Sen's slope calculation failed: {e}")
            raise AnalysisError(f"Sen's slope calculation failed: {e}")
    
    def get_name(self) -> str:
        return "Sen's Slope"


class LinearRegressionStrategy(TrendStrategy):
    """Linear regression trend strategy."""
    
    def __init__(self, alpha: float = 0.05):
        """Initialize with significance level."""
        self.alpha = alpha
    
    def calculate(self, data: pd.Series) -> TrendResult:
        """Calculate linear regression trend."""
        try:
            from scipy import stats
            
            # Clean data
            clean_data = data.dropna()
            
            if len(clean_data) < 3:
                raise AnalysisError(f"Insufficient data for linear regression: {len(clean_data)} points")
            
            # Create time index
            x = np.arange(len(clean_data))
            y = clean_data.values
            
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Determine trend direction
            if p_value < self.alpha:
                direction = "increasing" if slope > 0 else "decreasing"
                significance = "significant"
            else:
                direction = "no_trend"
                significance = "not_significant"
            
            return TrendResult(
                test_name="Linear Regression",
                statistic=r_value**2,  # R-squared
                p_value=p_value,
                slope=slope,
                trend_direction=direction,
                significance=significance
            )
            
        except Exception as e:
            logger.error(f"Linear regression calculation failed: {e}")
            raise AnalysisError(f"Linear regression failed: {e}")
    
    def get_name(self) -> str:
        return "Linear Regression"


class TrendAnalyzer:
    """Analyzes trends using multiple strategies."""
    
    def __init__(self, strategies: Optional[list] = None, alpha: float = 0.05):
        """Initialize with trend strategies.
        
        Args:
            strategies: List of TrendStrategy objects
            alpha: Significance level for tests
        """
        if strategies is None:
            strategies = [
                MannKendallStrategy(alpha),
                SenSlopeStrategy(),
                LinearRegressionStrategy(alpha)
            ]
        
        self.strategies = strategies
        self.alpha = alpha
    
    def analyze_series(self, data: pd.Series, series_name: str = "") -> Dict[str, TrendResult]:
        """Analyze trends in a data series using all strategies.
        
        Args:
            data: Time series data
            series_name: Name of the series for logging
            
        Returns:
            Dictionary of results keyed by strategy name
        """
        results = {}
        
        for strategy in self.strategies:
            try:
                result = strategy.calculate(data)
                results[strategy.get_name()] = result
                
                logger.info(f"{strategy.get_name()} for {series_name}: "
                           f"statistic={result.statistic:.4f}, p={result.p_value:.4f}")
                
            except AnalysisError as e:
                logger.error(f"{strategy.get_name()} failed for {series_name}: {e}")
                # Continue with other strategies
                continue
        
        return results
    
    def get_consensus_trend(self, results: Dict[str, TrendResult]) -> str:
        """Get consensus trend direction from multiple analyses.
        
        Args:
            results: Dictionary of trend results
            
        Returns:
            Consensus trend direction
        """
        if not results:
            return "unknown"
        
        # Count trend directions from significant results
        directions = []
        for result in results.values():
            if hasattr(result, 'significance') and result.significance == "significant":
                directions.append(result.trend_direction)
        
        if not directions:
            return "no_significant_trend"
        
        # Return most common direction
        from collections import Counter
        direction_counts = Counter(directions)
        most_common = direction_counts.most_common(1)[0]
        
        return most_common[0] if most_common[1] > len(directions) / 2 else "mixed_signals"