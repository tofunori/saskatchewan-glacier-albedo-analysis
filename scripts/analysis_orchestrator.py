"""
Analysis orchestration with improved error handling and separation of concerns.
"""

from typing import Optional, Dict, Any
import logging
from datetime import datetime

from config.settings import config
from utils.exceptions import AnalysisError, ConfigurationError
from scripts.dataset_validator import DatasetValidator

logger = logging.getLogger(__name__)


class AnalysisType:
    """Constants for analysis types."""
    COMPLETE = 1
    TRENDS = 2
    VISUALIZATIONS = 3
    PIXELS_QA = 4
    DAILY_PLOTS = 5


class AnalysisOrchestrator:
    """Orchestrates different types of analyses with proper error handling."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.validator = DatasetValidator()
        self.results: Dict[str, Any] = {}
    
    def run_dataset_analysis(self, dataset_name: str) -> bool:
        """Run complete analysis for a specific dataset.
        
        Args:
            dataset_name: Name of dataset to analyze
            
        Returns:
            bool: True if analysis completed successfully
        """
        try:
            print(f"\n🔍 Starting complete analysis for {dataset_name}")
            print("=" * 60)
            
            # Validate dataset availability
            if not self._validate_dataset(dataset_name):
                return False
            
            # Run all analysis components
            success = True
            success &= self._run_trends_analysis(dataset_name)
            success &= self._run_visualizations(dataset_name)
            success &= self._run_pixel_analysis(dataset_name)
            success &= self._run_daily_plots(dataset_name)
            
            if success:
                print(f"✅ Complete analysis for {dataset_name} finished successfully")
            else:
                print(f"⚠️ Analysis for {dataset_name} completed with some errors")
                
            return success
            
        except Exception as e:
            logger.error(f"Dataset analysis failed for {dataset_name}: {e}")
            print(f"❌ Analysis failed for {dataset_name}: {e}")
            return False
    
    def run_custom_analysis(self, dataset_name: str, analysis_type: int) -> bool:
        """Run specific type of analysis.
        
        Args:
            dataset_name: Name of dataset
            analysis_type: Type of analysis to run
            
        Returns:
            bool: True if analysis completed successfully
        """
        if not self._validate_dataset(dataset_name):
            return False
        
        analysis_map = {
            AnalysisType.COMPLETE: self.run_dataset_analysis,
            AnalysisType.TRENDS: self._run_trends_analysis,
            AnalysisType.VISUALIZATIONS: self._run_visualizations,
            AnalysisType.PIXELS_QA: self._run_pixel_analysis,
            AnalysisType.DAILY_PLOTS: self._run_daily_plots
        }
        
        analysis_func = analysis_map.get(analysis_type)
        if not analysis_func:
            print(f"❌ Unknown analysis type: {analysis_type}")
            return False
        
        try:
            if analysis_type == AnalysisType.COMPLETE:
                return analysis_func(dataset_name)
            else:
                return analysis_func(dataset_name)
        except Exception as e:
            logger.error(f"Custom analysis failed: {e}")
            print(f"❌ Analysis failed: {e}")
            return False
    
    def _validate_dataset(self, dataset_name: str) -> bool:
        """Validate that dataset is available.
        
        Args:
            dataset_name: Name of dataset to validate
            
        Returns:
            bool: True if dataset is valid and available
        """
        dataset_config = config.get_dataset_config(dataset_name)
        if not dataset_config:
            print(f"❌ No configuration found for dataset: {dataset_name}")
            return False
        
        if not self.validator.check_all_datasets():
            print(f"❌ No datasets available")
            return False
        
        if not self.validator.is_dataset_available(dataset_name):
            print(f"❌ Dataset {dataset_name} is not available")
            return False
        
        return True
    
    def _run_trends_analysis(self, dataset_name: str) -> bool:
        """Run trends analysis for dataset."""
        try:
            print(f"\n📈 Running trends analysis for {dataset_name}...")
            
            # Import and run trends analysis
            from analysis.trends import TrendCalculator
            from data.unified_loader import get_albedo_handler
            
            handler = get_albedo_handler(dataset_name)
            handler.load_data()
            
            calculator = TrendCalculator(handler)
            results = calculator.calculate_basic_trends()
            
            self.results[f'{dataset_name}_trends'] = results
            print(f"✅ Trends analysis completed for {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"Trends analysis failed for {dataset_name}: {e}")
            print(f"❌ Trends analysis failed for {dataset_name}: {e}")
            return False
    
    def _run_visualizations(self, dataset_name: str) -> bool:
        """Run visualizations for dataset."""
        try:
            print(f"\n🎨 Generating visualizations for {dataset_name}...")
            
            # Import and run visualizations
            from visualization.charts import ChartGenerator
            from data.unified_loader import get_albedo_handler
            
            handler = get_albedo_handler(dataset_name)
            handler.load_data()
            
            chart_gen = ChartGenerator(handler, dataset_name)
            chart_gen.generate_all_charts()
            
            print(f"✅ Visualizations completed for {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"Visualizations failed for {dataset_name}: {e}")
            print(f"❌ Visualizations failed for {dataset_name}: {e}")
            return False
    
    def _run_pixel_analysis(self, dataset_name: str) -> bool:
        """Run pixel/QA analysis for dataset."""
        try:
            print(f"\n🔍 Running pixel/QA analysis for {dataset_name}...")
            
            # Import and run pixel analysis
            from analysis.pixel_analysis import PixelAnalyzer
            from data.unified_loader import get_albedo_handler
            
            handler = get_albedo_handler(dataset_name)
            handler.load_data()
            
            analyzer = PixelAnalyzer(handler, dataset_name)
            results = analyzer.analyze_quality_distribution()
            
            self.results[f'{dataset_name}_pixels'] = results
            print(f"✅ Pixel/QA analysis completed for {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"Pixel analysis failed for {dataset_name}: {e}")
            print(f"❌ Pixel analysis failed for {dataset_name}: {e}")
            return False
    
    def _run_daily_plots(self, dataset_name: str) -> bool:
        """Run daily plots generation for dataset."""
        try:
            print(f"\n📅 Generating daily plots for {dataset_name}...")
            
            # Import and run daily plots
            from visualization.daily_plots import DailyPlotGenerator
            from data.unified_loader import get_albedo_handler
            
            handler = get_albedo_handler(dataset_name)
            handler.load_data()
            
            plot_gen = DailyPlotGenerator(handler, dataset_name)
            plot_gen.generate_all_years()
            
            print(f"✅ Daily plots completed for {dataset_name}")
            return True
            
        except Exception as e:
            logger.error(f"Daily plots failed for {dataset_name}: {e}")
            print(f"❌ Daily plots failed for {dataset_name}: {e}")
            return False


# Create global orchestrator instance
orchestrator = AnalysisOrchestrator()

# Legacy wrapper functions for backward compatibility
def run_dataset_analysis(dataset_name: str) -> bool:
    """Legacy wrapper for dataset analysis."""
    return orchestrator.run_dataset_analysis(dataset_name)

def run_custom_analysis(dataset_name: str, analysis_type: int) -> bool:
    """Legacy wrapper for custom analysis."""
    return orchestrator.run_custom_analysis(dataset_name, analysis_type)

def run_complete_analysis() -> bool:
    """Legacy wrapper for complete analysis."""
    return orchestrator.run_dataset_analysis(config.default_dataset)

def run_trends_only() -> bool:
    """Legacy wrapper for trends analysis."""
    return orchestrator.run_custom_analysis(config.default_dataset, AnalysisType.TRENDS)

def run_visualizations_only() -> bool:
    """Legacy wrapper for visualizations."""
    return orchestrator.run_custom_analysis(config.default_dataset, AnalysisType.VISUALIZATIONS)

def run_pixels_only() -> bool:
    """Legacy wrapper for pixel analysis."""
    return orchestrator.run_custom_analysis(config.default_dataset, AnalysisType.PIXELS_QA)

def run_daily_only() -> bool:
    """Legacy wrapper for daily plots."""
    return orchestrator.run_custom_analysis(config.default_dataset, AnalysisType.DAILY_PLOTS)