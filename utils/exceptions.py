"""
Custom exceptions for Saskatchewan Glacier Albedo Analysis.
"""

class AlbedoAnalysisError(Exception):
    """Base exception for albedo analysis errors."""
    pass


class DataLoadError(AlbedoAnalysisError):
    """Raised when data loading fails."""
    pass


class ConfigurationError(AlbedoAnalysisError):
    """Raised when configuration is invalid."""
    pass


class AnalysisError(AlbedoAnalysisError):
    """Raised when analysis computation fails."""
    pass


class VisualizationError(AlbedoAnalysisError):
    """Raised when visualization generation fails."""
    pass


class DatabaseConnectionError(AlbedoAnalysisError):
    """Raised when database connection fails."""
    pass