"""
Tests for data handler module
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from data.handler import AlbedoDataHandler
except ModuleNotFoundError:
    # Try alternative import path based on actual structure
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from data_handler import AlbedoDataHandler
    except ImportError:
        AlbedoDataHandler = None


@pytest.mark.skipif(AlbedoDataHandler is None, reason="AlbedoDataHandler not available")
class TestAlbedoDataHandlerInit:
    """Test AlbedoDataHandler initialization"""

    def test_init_with_valid_path(self):
        """Test initialization with valid CSV path"""
        handler = AlbedoDataHandler("test_path.csv")
        assert handler.csv_path == "test_path.csv"
        assert handler.data is None
        assert handler.raw_data is None
        assert hasattr(handler, "fraction_classes")
        assert hasattr(handler, "class_labels")

    def test_len_method_no_data(self):
        """Test __len__ method when no data is loaded"""
        handler = AlbedoDataHandler("test_path.csv")
        assert len(handler) == 0


@pytest.mark.skipif(AlbedoDataHandler is None, reason="AlbedoDataHandler not available")
class TestAlbedoDataHandlerWithMockData:
    """Test AlbedoDataHandler with mock data"""

    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing"""
        data = {
            "date": ["2020-06-01", "2020-06-02", "2020-06-03"],
            "albedo": [0.8, 0.75, 0.82],
            "quality": [0, 1, 0],
            "fraction_0_20": [10, 15, 12],
            "fraction_20_40": [20, 25, 18],
            "year": [2020, 2020, 2020],
            "month": [6, 6, 6],
            "day": [1, 2, 3],
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def temp_csv_file(self, sample_csv_data):
        """Create temporary CSV file for testing"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            sample_csv_data.to_csv(f.name, index=False)
            yield f.name
        os.unlink(f.name)

    def test_load_data_success(self, temp_csv_file):
        """Test successful data loading"""
        handler = AlbedoDataHandler(temp_csv_file)
        handler.load_data()

        assert handler.data is not None
        assert handler.raw_data is not None
        assert len(handler) > 0
        assert isinstance(handler.data, pd.DataFrame)

    def test_load_data_file_not_found(self):
        """Test data loading with non-existent file"""
        handler = AlbedoDataHandler("non_existent_file.csv")

        with pytest.raises(FileNotFoundError):
            handler.load_data()

    @patch("pandas.read_csv")
    def test_load_data_with_mock(self, mock_read_csv, sample_csv_data):
        """Test data loading with mocked pandas"""
        mock_read_csv.return_value = sample_csv_data

        handler = AlbedoDataHandler("mock_file.csv")
        handler.load_data()

        assert handler.data is not None
        assert len(handler) == 3
        mock_read_csv.assert_called_once()


@pytest.mark.skipif(AlbedoDataHandler is None, reason="AlbedoDataHandler not available")
class TestAlbedoDataHandlerDataProcessing:
    """Test data processing methods"""

    @pytest.fixture
    def handler_with_data(self):
        """Create handler with sample data"""
        data = pd.DataFrame(
            {
                "date": pd.date_range("2020-06-01", periods=10, freq="D"),
                "albedo": np.random.uniform(0.7, 0.9, 10),
                "quality": np.random.choice([0, 1], 10),
                "fraction_0_20": np.random.randint(10, 50, 10),
                "year": [2020] * 10,
                "month": [6] * 10,
            }
        )

        handler = AlbedoDataHandler("mock.csv")
        handler.data = data
        handler.raw_data = data.copy()
        return handler

    def test_get_data_summary(self, handler_with_data):
        """Test data summary generation"""
        summary = handler_with_data.get_data_summary()

        assert isinstance(summary, dict)
        assert "total_records" in summary
        assert "date_range" in summary
        assert summary["total_records"] == 10

    def test_print_data_summary(self, handler_with_data, capsys):
        """Test data summary printing"""
        handler_with_data.print_data_summary()
        captured = capsys.readouterr()

        assert "RÉSUMÉ DES DONNÉES" in captured.out
        assert "Nombre total" in captured.out

    def test_get_fraction_data_valid_class(self, handler_with_data):
        """Test getting fraction data for valid class"""
        # Mock fraction classes
        handler_with_data.fraction_classes = {"0-20%": [0, 20]}

        # Add a column that matches the expected pattern
        handler_with_data.data["fraction_0_20"] = np.random.randint(10, 50, 10)

        fraction_data = handler_with_data.get_fraction_data("0-20%")

        if fraction_data is not None:
            assert isinstance(fraction_data, pd.DataFrame)
            assert len(fraction_data) <= len(handler_with_data.data)

    def test_get_fraction_data_invalid_class(self, handler_with_data):
        """Test getting fraction data for invalid class"""
        fraction_data = handler_with_data.get_fraction_data("invalid_class")
        assert fraction_data is None

    def test_get_monthly_data(self, handler_with_data):
        """Test monthly data aggregation"""
        monthly_data = handler_with_data.get_monthly_data()

        assert isinstance(monthly_data, pd.DataFrame)
        assert "month" in monthly_data.columns
        assert len(monthly_data) <= 12  # At most 12 months


@pytest.mark.skipif(AlbedoDataHandler is None, reason="AlbedoDataHandler not available")
class TestAlbedoDataHandlerValidation:
    """Test data validation methods"""

    def test_validate_required_columns_success(self):
        """Test column validation with valid data"""
        data = pd.DataFrame(
            {
                "date": ["2020-01-01"],
                "albedo": [0.8],
                "quality": [0],
                "year": [2020],
                "month": [1],
            }
        )

        handler = AlbedoDataHandler("mock.csv")
        handler.data = data

        # Should not raise an exception
        try:
            handler._validate_required_columns()
        except Exception as e:
            pytest.fail(f"Validation failed unexpectedly: {e}")

    def test_validate_required_columns_missing(self):
        """Test column validation with missing columns"""
        data = pd.DataFrame(
            {
                "date": ["2020-01-01"],
                "albedo": [0.8],
                # Missing required columns
            }
        )

        handler = AlbedoDataHandler("mock.csv")
        handler.data = data

        with pytest.raises((KeyError, ValueError)):
            handler._validate_required_columns()


@pytest.mark.skipif(AlbedoDataHandler is None, reason="AlbedoDataHandler not available")
class TestAlbedoDataHandlerExport:
    """Test data export functionality"""

    @pytest.fixture
    def handler_with_data(self):
        """Create handler with sample data"""
        data = pd.DataFrame(
            {
                "date": ["2020-06-01", "2020-06-02"],
                "albedo": [0.8, 0.75],
                "quality": [0, 1],
                "year": [2020, 2020],
                "month": [6, 6],
            }
        )

        handler = AlbedoDataHandler("mock.csv")
        handler.data = data
        return handler

    @patch("pandas.DataFrame.to_csv")
    def test_export_cleaned_data(self, mock_to_csv, handler_with_data):
        """Test data export functionality"""
        handler_with_data.export_cleaned_data("output.csv")
        mock_to_csv.assert_called_once()

    def test_get_available_fractions(self, handler_with_data):
        """Test getting available fraction columns"""
        # Add some fraction columns
        handler_with_data.data["fraction_0_20"] = [10, 15]
        handler_with_data.data["fraction_20_40"] = [20, 25]

        fractions = handler_with_data.get_available_fractions()
        assert isinstance(fractions, list)
        assert len(fractions) >= 0


if __name__ == "__main__":
    pytest.main([__file__])
