#!/usr/bin/env python3
"""
Quick Statistics Report Generator
================================

Extracts basic statistics from PostgreSQL database using MCP and exports
them to a Word document using MCP office-word tools.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_stats_report():
    """Generate a Word document with basic database statistics"""
    print("🚀 Starting Quick Statistics Report Generation...")
    
    # Import MCP tools (these will be called via the MCP interface)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_filename = f"saskatchewan_albedo_stats_{timestamp}.docx"
    
    print(f"📊 Generating statistics report: {doc_filename}")
    
    # This script serves as a template - the actual MCP calls will be made
    # through the Claude interface when this script is run
    
    queries = {
        "dataset_overview": """
        SELECT 
            'MCD43A3 Measurements' as dataset,
            COUNT(*) as total_records,
            MIN(date) as start_date,
            MAX(date) as end_date,
            COUNT(DISTINCT year) as years_covered
        FROM albedo.mcd43a3_measurements
        UNION ALL
        SELECT 
            'MOD10A1 Measurements' as dataset,
            COUNT(*) as total_records,
            MIN(date) as start_date,
            MAX(date) as end_date,
            COUNT(DISTINCT year) as years_covered
        FROM albedo.mod10a1_measurements
        """,
        
        "mcd43a3_albedo_stats": """
        SELECT 
            ROUND(AVG(border_mean)::numeric, 4) as avg_border,
            ROUND(AVG(mixed_low_mean)::numeric, 4) as avg_mixed_low,
            ROUND(AVG(mixed_high_mean)::numeric, 4) as avg_mixed_high,
            ROUND(AVG(mostly_ice_mean)::numeric, 4) as avg_mostly_ice,
            ROUND(AVG(pure_ice_mean)::numeric, 4) as avg_pure_ice
        FROM albedo.mcd43a3_measurements
        WHERE border_mean IS NOT NULL
        """,
        
        "mod10a1_albedo_stats": """
        SELECT 
            ROUND(AVG(border_mean)::numeric, 4) as avg_border,
            ROUND(AVG(mixed_low_mean)::numeric, 4) as avg_mixed_low,
            ROUND(AVG(mixed_high_mean)::numeric, 4) as avg_mixed_high,
            ROUND(AVG(mostly_ice_mean)::numeric, 4) as avg_mostly_ice,
            ROUND(AVG(pure_ice_mean)::numeric, 4) as avg_pure_ice
        FROM albedo.mod10a1_measurements
        WHERE border_mean IS NOT NULL
        """,
        
        "seasonal_distribution": """
        SELECT 
            season,
            COUNT(*) as observations
        FROM (
            SELECT season FROM albedo.mcd43a3_measurements
            UNION ALL
            SELECT season FROM albedo.mod10a1_measurements
        ) combined
        WHERE season IS NOT NULL
        GROUP BY season
        ORDER BY 
            CASE season
                WHEN 'early_summer' THEN 1
                WHEN 'mid_summer' THEN 2
                WHEN 'late_summer' THEN 3
                ELSE 4
            END
        """,
        
        "data_quality_mcd43a3": """
        SELECT 
            ROUND(AVG(quality_0_best)::numeric, 2) as avg_best_quality,
            ROUND(AVG(quality_1_good)::numeric, 2) as avg_good_quality,
            ROUND(AVG(quality_2_moderate)::numeric, 2) as avg_moderate_quality,
            ROUND(AVG(quality_3_poor)::numeric, 2) as avg_poor_quality
        FROM albedo.mcd43a3_quality
        """,
        
        "pixel_coverage": """
        SELECT 
            'MCD43A3' as dataset,
            ROUND(AVG(total_valid_pixels)::numeric, 0) as avg_valid_pixels,
            MIN(total_valid_pixels) as min_pixels,
            MAX(total_valid_pixels) as max_pixels
        FROM albedo.mcd43a3_measurements
        WHERE total_valid_pixels IS NOT NULL
        UNION ALL
        SELECT 
            'MOD10A1' as dataset,
            ROUND(AVG(total_valid_pixels)::numeric, 0) as avg_valid_pixels,
            MIN(total_valid_pixels) as min_pixels,
            MAX(total_valid_pixels) as max_pixels
        FROM albedo.mod10a1_measurements
        WHERE total_valid_pixels IS NOT NULL
        """
    }
    
    print("📋 Prepared the following statistical queries:")
    for query_name in queries.keys():
        print(f"  • {query_name}")
    
    print(f"\n📄 Ready to generate Word document: {doc_filename}")
    print("\n🔧 This script will be executed through Claude's MCP interface to:")
    print("  1. Run PostgreSQL queries using mcp__postgres__query")
    print("  2. Create Word document using mcp__office-word__create_document")
    print("  3. Add structured content using mcp__office-word__add_heading and add_paragraph")
    
    return {
        "filename": doc_filename,
        "queries": queries,
        "timestamp": timestamp
    }

if __name__ == "__main__":
    result = generate_stats_report()
    print(f"\n✅ Script prepared. Document filename: {result['filename']}")
    print("🚀 Run this script through Claude to execute MCP calls!")