#!/bin/bash
# =============================================================================
# Saskatchewan Glacier Albedo Analysis - R Script Runner
# =============================================================================

echo "🚀 Starting Saskatchewan Glacier Albedo Analysis in R"
echo "======================================================"

# Check if R is installed
if ! command -v R &> /dev/null; then
    echo "❌ R is not installed. Please install R first:"
    echo "   Ubuntu/Debian: sudo apt install r-base r-base-dev"
    echo "   CentOS/RHEL: sudo yum install R"
    echo "   macOS: brew install r"
    exit 1
fi

echo "✅ R is installed"

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

echo "✅ PostgreSQL is running"

# Run the R script
echo "🔬 Executing R analysis script..."
echo ""

Rscript scripts/albedo_trend_analysis.R

echo ""
echo "📊 R Analysis completed!"
echo "💾 Check for generated .RData files with results"