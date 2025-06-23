-- Saskatchewan Glacier Albedo Analysis Database Schema
-- Created for migrating CSV data to PostgreSQL

-- Create schema for organization
CREATE SCHEMA IF NOT EXISTS albedo;

-- Table for MCD43A3 albedo data (general albedo)
CREATE TABLE IF NOT EXISTS albedo.mcd43a3_measurements (
    id SERIAL PRIMARY KEY,
    system_index TEXT,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    decimal_year DOUBLE PRECISION NOT NULL,
    doy INTEGER NOT NULL,
    season VARCHAR(20),
    system_time_start BIGINT,
    min_pixels_threshold INTEGER,
    total_valid_pixels INTEGER,
    
    -- Border fraction (0-25%)
    border_data_quality DOUBLE PRECISION,
    border_mean DOUBLE PRECISION,
    border_median DOUBLE PRECISION,
    border_pixel_count INTEGER,
    
    -- Mixed low fraction (25-50%)
    mixed_low_data_quality DOUBLE PRECISION,
    mixed_low_mean DOUBLE PRECISION,
    mixed_low_median DOUBLE PRECISION,
    mixed_low_pixel_count INTEGER,
    
    -- Mixed high fraction (50-75%)
    mixed_high_data_quality DOUBLE PRECISION,
    mixed_high_mean DOUBLE PRECISION,
    mixed_high_median DOUBLE PRECISION,
    mixed_high_pixel_count INTEGER,
    
    -- Mostly ice fraction (75-90%)
    mostly_ice_data_quality DOUBLE PRECISION,
    mostly_ice_mean DOUBLE PRECISION,
    mostly_ice_median DOUBLE PRECISION,
    mostly_ice_pixel_count INTEGER,
    
    -- Pure ice fraction (90-100%)
    pure_ice_data_quality DOUBLE PRECISION,
    pure_ice_mean DOUBLE PRECISION,
    pure_ice_median DOUBLE PRECISION,
    pure_ice_pixel_count INTEGER,
    
    -- Geometry (JSON)
    geo TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for MOD10A1 snow albedo data
CREATE TABLE IF NOT EXISTS albedo.mod10a1_measurements (
    id SERIAL PRIMARY KEY,
    system_index TEXT,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    decimal_year DOUBLE PRECISION NOT NULL,
    doy INTEGER NOT NULL,
    season VARCHAR(20),
    system_time_start BIGINT,
    min_pixels_threshold INTEGER,
    total_valid_pixels INTEGER,
    
    -- Border fraction (0-25%)
    border_data_quality DOUBLE PRECISION,
    border_mean DOUBLE PRECISION,
    border_median DOUBLE PRECISION,
    border_pixel_count INTEGER,
    
    -- Mixed low fraction (25-50%)
    mixed_low_data_quality DOUBLE PRECISION,
    mixed_low_mean DOUBLE PRECISION,
    mixed_low_median DOUBLE PRECISION,
    mixed_low_pixel_count INTEGER,
    
    -- Mixed high fraction (50-75%)
    mixed_high_data_quality DOUBLE PRECISION,
    mixed_high_mean DOUBLE PRECISION,
    mixed_high_median DOUBLE PRECISION,
    mixed_high_pixel_count INTEGER,
    
    -- Mostly ice fraction (75-90%)
    mostly_ice_data_quality DOUBLE PRECISION,
    mostly_ice_mean DOUBLE PRECISION,
    mostly_ice_median DOUBLE PRECISION,
    mostly_ice_pixel_count INTEGER,
    
    -- Pure ice fraction (90-100%)
    pure_ice_data_quality DOUBLE PRECISION,
    pure_ice_mean DOUBLE PRECISION,
    pure_ice_median DOUBLE PRECISION,
    pure_ice_pixel_count INTEGER,
    
    -- Geometry (JSON)
    geo TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for MCD43A3 quality distribution
CREATE TABLE IF NOT EXISTS albedo.mcd43a3_quality (
    id SERIAL PRIMARY KEY,
    system_index TEXT,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    decimal_year DOUBLE PRECISION NOT NULL,
    doy INTEGER NOT NULL,
    season VARCHAR(20),
    system_time_start BIGINT,
    
    -- Quality levels
    quality_0_best DOUBLE PRECISION,
    quality_1_good DOUBLE PRECISION,
    quality_2_moderate DOUBLE PRECISION,
    quality_3_poor DOUBLE PRECISION,
    
    -- Metadata
    total_pixels INTEGER,
    geo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for MOD10A1 quality distribution
CREATE TABLE IF NOT EXISTS albedo.mod10a1_quality (
    id SERIAL PRIMARY KEY,
    system_index TEXT,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    decimal_year DOUBLE PRECISION NOT NULL,
    doy INTEGER NOT NULL,
    season VARCHAR(20),
    system_time_start BIGINT,
    
    -- Quality levels
    quality_0_best DOUBLE PRECISION,
    quality_1_good DOUBLE PRECISION,
    quality_2_ok DOUBLE PRECISION,
    quality_other_night_ocean DOUBLE PRECISION,
    
    -- Metadata
    total_pixels INTEGER,
    geo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_mcd43a3_date ON albedo.mcd43a3_measurements(date);
CREATE INDEX IF NOT EXISTS idx_mcd43a3_year ON albedo.mcd43a3_measurements(year);
CREATE INDEX IF NOT EXISTS idx_mcd43a3_season ON albedo.mcd43a3_measurements(season);
CREATE INDEX IF NOT EXISTS idx_mcd43a3_decimal_year ON albedo.mcd43a3_measurements(decimal_year);

CREATE INDEX IF NOT EXISTS idx_mod10a1_date ON albedo.mod10a1_measurements(date);
CREATE INDEX IF NOT EXISTS idx_mod10a1_year ON albedo.mod10a1_measurements(year);
CREATE INDEX IF NOT EXISTS idx_mod10a1_season ON albedo.mod10a1_measurements(season);
CREATE INDEX IF NOT EXISTS idx_mod10a1_decimal_year ON albedo.mod10a1_measurements(decimal_year);

CREATE INDEX IF NOT EXISTS idx_mcd43a3_quality_date ON albedo.mcd43a3_quality(date);
CREATE INDEX IF NOT EXISTS idx_mod10a1_quality_date ON albedo.mod10a1_quality(date);

-- Create views for easy access (maintaining compatibility with existing code)
CREATE OR REPLACE VIEW albedo.mcd43a3_view AS 
SELECT 
    date,
    year,
    decimal_year,
    doy,
    season,
    min_pixels_threshold,
    border_mean,
    border_median,
    mixed_low_mean,
    mixed_low_median,
    mixed_high_mean,
    mixed_high_median,
    mostly_ice_mean,
    mostly_ice_median,
    pure_ice_mean,
    pure_ice_median,
    total_valid_pixels
FROM albedo.mcd43a3_measurements
ORDER BY date;

CREATE OR REPLACE VIEW albedo.mod10a1_view AS 
SELECT 
    date,
    year,
    decimal_year,
    doy,
    season,
    min_pixels_threshold,
    border_mean,
    border_median,
    mixed_low_mean,
    mixed_low_median,
    mixed_high_mean,
    mixed_high_median,
    mostly_ice_mean,
    mostly_ice_median,
    pure_ice_mean,
    pure_ice_median,
    total_valid_pixels
FROM albedo.mod10a1_measurements
ORDER BY date;