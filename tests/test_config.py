"""
Tests for configuration module
"""

import pytest
import os
from unittest.mock import patch
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class TestConfigBasics:
    """Test basic configuration functionality"""

    def test_config_constants_exist(self):
        """Test that basic configuration constants are defined"""
        assert hasattr(config, "CSV_PATH")
        assert hasattr(config, "OUTPUT_DIR")
        assert hasattr(config, "ANALYSIS_VARIABLE")
        assert hasattr(config, "FRACTION_CLASSES")

    def test_fraction_classes_structure(self):
        """Test that fraction classes are properly structured"""
        assert isinstance(config.FRACTION_CLASSES, list)
        assert len(config.FRACTION_CLASSES) > 0

        for class_name in config.FRACTION_CLASSES:
            assert isinstance(class_name, str)
            assert len(class_name) > 0

    def test_class_labels_match_fractions(self):
        """Test that class labels match fraction classes"""
        assert len(config.CLASS_LABELS) == len(config.FRACTION_CLASSES)

    def test_output_structure_defined(self):
        """Test that output structure is properly defined"""
        assert hasattr(config, "OUTPUT_STRUCTURE")
        assert isinstance(config.OUTPUT_STRUCTURE, dict)
        assert "products" in config.OUTPUT_STRUCTURE


class TestConfigFunctions:
    """Test configuration utility functions"""

    def test_get_significance_marker(self):
        """Test significance marker function"""
        # Test different p-value ranges (based on actual implementation)
        result_high_sig = config.get_significance_marker(0.001)
        result_mod_sig = config.get_significance_marker(0.005)
        result_low_sig = config.get_significance_marker(0.03)
        result_no_sig = config.get_significance_marker(0.08)

        # Verify that we get string results
        assert isinstance(result_high_sig, str)
        assert isinstance(result_mod_sig, str)
        assert isinstance(result_low_sig, str)
        assert isinstance(result_no_sig, str)

        # Verify that higher significance gives different markers
        assert result_high_sig != result_no_sig

    def test_get_autocorr_status(self):
        """Test autocorrelation status function"""
        # Test different autocorrelation levels
        strong_autocorr = config.get_autocorr_status(0.8)
        weak_autocorr = config.get_autocorr_status(0.1)

        assert "Très forte" in strong_autocorr or "Forte" in strong_autocorr
        assert "Faible" in weak_autocorr

    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_get_output_path(self, mock_exists, mock_makedirs):
        """Test output path generation"""
        mock_exists.return_value = False

        # Test basic path generation
        path = config.get_output_path("MCD43A3_albedo", "reports", create_dir=True)
        assert isinstance(path, str)
        assert "MCD43A3_albedo" in path
        assert "reports" in path

        # Verify directory creation was called
        mock_makedirs.assert_called()

    def test_print_config_summary(self, capsys):
        """Test configuration summary printing"""
        config.print_config_summary()
        captured = capsys.readouterr()

        # Check that output contains expected elements
        assert "CONFIGURATION" in captured.out
        assert "CSV" in captured.out
        assert "Répertoire" in captured.out


class TestConfigValidation:
    """Test configuration validation and edge cases"""

    def test_analysis_config_structure(self):
        """Test that analysis config has required fields"""
        assert hasattr(config, "ANALYSIS_CONFIG")
        analysis_config = config.ANALYSIS_CONFIG

        required_fields = ["significance_levels", "autocorr_thresholds"]
        for field in required_fields:
            assert field in analysis_config

    def test_plot_styles_defined(self):
        """Test that plot styles are properly defined"""
        assert hasattr(config, "PLOT_STYLES")
        assert isinstance(config.PLOT_STYLES, dict)

        # Check for common plot style keys
        expected_keys = ["trend_line", "scatter"]
        for key in expected_keys:
            if key in config.PLOT_STYLES:
                assert isinstance(config.PLOT_STYLES[key], dict)

    def test_month_names_complete(self):
        """Test that month names are defined"""
        if hasattr(config, "MONTH_NAMES"):
            assert isinstance(config.MONTH_NAMES, dict)
            assert len(config.MONTH_NAMES) > 0
            # Check that values are strings
            for month_name in config.MONTH_NAMES.values():
                assert isinstance(month_name, str)


if __name__ == "__main__":
    pytest.main([__file__])
