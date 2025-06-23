#!/usr/bin/env Rscript
# =============================================================================
# Saskatchewan Glacier Albedo Trend Analysis in R
# =============================================================================
# 
# Robust statistical analysis using established R packages for:
# - Mann-Kendall trend tests
# - Sen's slope estimation  
# - Change point detection
# - Cross-dataset correlation
# - Seasonal trend analysis
#
# Author: Saskatchewan Albedo Analysis System
# Date: 2025-01-23

# =============================================================================
# 1. SETUP AND DEPENDENCIES
# =============================================================================

# Install required packages if not already installed
required_packages <- c(
  "RPostgreSQL",    # Database connection
  "DBI",           # Database interface
  "dplyr",         # Data manipulation
  "lubridate",     # Date handling
  "trend",         # Mann-Kendall and Sen's slope
  "Kendall",       # Additional Mann-Kendall tests
  "changepoint",   # Change point detection
  "bcp",           # Bayesian change point
  "ggplot2",       # Visualization
  "corrplot",      # Correlation plots
  "modifiedmk",    # Modified Mann-Kendall for autocorrelation
  "forecast",      # Time series analysis
  "tseries"        # Time series tests
)

# Function to install missing packages
install_if_missing <- function(packages) {
  new_packages <- packages[!(packages %in% installed.packages()[,"Package"])]
  if(length(new_packages)) {
    install.packages(new_packages, dependencies = TRUE)
  }
}

# Install missing packages
cat("Checking and installing required R packages...\n")
install_if_missing(required_packages)

# Load libraries
suppressMessages({
  library(RPostgreSQL)
  library(DBI)
  library(dplyr)
  library(lubridate)
  library(trend)
  library(Kendall)
  library(changepoint)
  library(bcp)
  library(ggplot2)
  library(corrplot)
  library(modifiedmk)
  library(forecast)
  library(tseries)
})

cat("✅ All R packages loaded successfully\n\n")

# =============================================================================
# 2. DATABASE CONNECTION
# =============================================================================

# Database connection parameters
connect_to_database <- function() {
  tryCatch({
    # Connect to PostgreSQL database
    drv <- dbDriver("PostgreSQL")
    con <- dbConnect(drv, 
                     dbname = "saskatchewan_albedo",
                     host = "localhost",
                     port = 5432,
                     user = Sys.getenv("USER"))
    
    cat("✅ Connected to PostgreSQL database\n")
    return(con)
  }, error = function(e) {
    cat("❌ Database connection failed:", e$message, "\n")
    cat("💡 Ensure PostgreSQL is running and accessible\n")
    return(NULL)
  })
}

# Test database connection
con <- connect_to_database()
if (is.null(con)) {
  stop("Cannot proceed without database connection")
}

# =============================================================================
# 3. DATA EXTRACTION FUNCTIONS
# =============================================================================

# Extract albedo time series from database
extract_albedo_data <- function(con, dataset_name) {
  query <- paste0("
    SELECT 
      date,
      decimal_year,
      year,
      season,
      pure_ice_mean,
      pure_ice_pixel_count,
      mostly_ice_mean,
      mixed_high_mean,
      mixed_low_mean,
      border_mean,
      total_valid_pixels
    FROM albedo.", dataset_name, "_measurements
    WHERE pure_ice_mean IS NOT NULL
    ORDER BY date
  ")
  
  data <- dbGetQuery(con, query)
  data$date <- as.Date(data$date)
  
  cat("📊 Extracted", nrow(data), "observations from", dataset_name, "\n")
  return(data)
}

# Extract matched dataset for correlation analysis
extract_matched_data <- function(con) {
  query <- "
    SELECT 
      m1.date,
      m1.decimal_year,
      m1.season,
      m1.pure_ice_mean as mcd43a3_albedo,
      m2.pure_ice_mean as mod10a1_albedo,
      m1.pure_ice_pixel_count as mcd43a3_pixels,
      m2.pure_ice_pixel_count as mod10a1_pixels
    FROM albedo.mcd43a3_measurements m1
    INNER JOIN albedo.mod10a1_measurements m2 
      ON m1.date = m2.date
    WHERE m1.pure_ice_mean IS NOT NULL 
      AND m2.pure_ice_mean IS NOT NULL
    ORDER BY m1.date
  "
  
  data <- dbGetQuery(con, query)
  data$date <- as.Date(data$date)
  
  cat("📊 Extracted", nrow(data), "matched observations for correlation analysis\n")
  return(data)
}

# =============================================================================
# 4. TREND ANALYSIS FUNCTIONS
# =============================================================================

# Comprehensive Mann-Kendall and Sen's slope analysis
perform_trend_analysis <- function(data, dataset_name, variable = "pure_ice_mean") {
  cat("\n=== TREND ANALYSIS FOR", toupper(dataset_name), "===\n")
  
  # Extract time series
  ts_data <- data[[variable]]
  time_vector <- data$decimal_year
  
  # 1. Basic Mann-Kendall test
  mk_result <- mk.test(ts_data)
  
  # 2. Sen's slope estimation
  sens_result <- sens.slope(ts_data)
  
  # 3. Modified Mann-Kendall (accounts for autocorrelation)
  # Check for autocorrelation first
  acf_result <- acf(ts_data, plot = FALSE, lag.max = 10)
  significant_autocorr <- any(abs(acf_result$acf[-1]) > 0.2)
  
  if (significant_autocorr) {
    cat("⚠️  Autocorrelation detected, using modified Mann-Kendall\n")
    mod_mk_result <- modifiedmk::mmkh(ts_data)
  } else {
    mod_mk_result <- NULL
  }
  
  # 4. Seasonal Mann-Kendall (if seasonal data available)
  seasonal_mk <- NULL
  if ("season" %in% names(data)) {
    # Create seasonal time series
    seasons <- factor(data$season, levels = c("early_summer", "mid_summer", "late_summer"))
    seasonal_mk <- list()
    
    for (season in levels(seasons)) {
      season_data <- data[data$season == season, variable]
      if (length(season_data) > 10) {  # Minimum data points
        seasonal_mk[[season]] <- list(
          mk_test = mk.test(season_data),
          sens_slope = sens.slope(season_data),
          n_obs = length(season_data)
        )
      }
    }
  }
  
  # Compile results
  results <- list(
    dataset = dataset_name,
    variable = variable,
    n_observations = length(ts_data),
    time_span = range(time_vector),
    
    # Basic tests
    mk_test = mk_result,
    sens_slope = sens_result,
    
    # Modified test
    modified_mk = mod_mk_result,
    autocorrelation_detected = significant_autocorr,
    
    # Seasonal analysis
    seasonal_analysis = seasonal_mk,
    
    # Summary statistics
    mean_value = mean(ts_data, na.rm = TRUE),
    sd_value = sd(ts_data, na.rm = TRUE),
    trend_magnitude = sens_result$estimates * (max(time_vector) - min(time_vector))
  )
  
  # Print summary
  cat("📈 Mann-Kendall Trend:", mk_result$statistic, "\n")
  cat("📊 p-value:", format(mk_result$p.value, scientific = TRUE), "\n")
  cat("📉 Sen's Slope:", format(sens_result$estimates, digits = 6), "units/year\n")
  cat("📏 Total Change:", format(results$trend_magnitude, digits = 4), "units over", 
      format(max(time_vector) - min(time_vector), digits = 1), "years\n")
  
  if (mk_result$p.value < 0.001) {
    cat("✅ Highly significant trend (p < 0.001)\n")
  } else if (mk_result$p.value < 0.05) {
    cat("✅ Significant trend (p < 0.05)\n")
  } else if (mk_result$p.value < 0.10) {
    cat("⚠️  Marginally significant trend (p < 0.10)\n")
  } else {
    cat("❌ No significant trend detected\n")
  }
  
  return(results)
}

# =============================================================================
# 5. CHANGE POINT DETECTION FUNCTIONS
# =============================================================================

# Comprehensive change point analysis
perform_changepoint_analysis <- function(data, dataset_name, variable = "pure_ice_mean") {
  cat("\n=== CHANGE POINT ANALYSIS FOR", toupper(dataset_name), "===\n")
  
  ts_data <- data[[variable]]
  time_vector <- data$decimal_year
  
  # 1. PELT (Pruned Exact Linear Time) - Most robust
  tryCatch({
    cpt_pelt <- cpt.mean(ts_data, method = "PELT", minseglen = 30)
    pelt_cpts <- cpts(cpt_pelt)
    
    cat("🔍 PELT Change Points detected at positions:", pelt_cpts, "\n")
    if (length(pelt_cpts) > 0) {
      pelt_years <- time_vector[pelt_cpts]
      cat("📅 PELT Change Point Years:", paste(round(pelt_years, 2), collapse = ", "), "\n")
    }
  }, error = function(e) {
    cat("❌ PELT analysis failed:", e$message, "\n")
    pelt_cpts <- integer(0)
    pelt_years <- numeric(0)
  })
  
  # 2. Binary Segmentation
  tryCatch({
    cpt_binseg <- cpt.mean(ts_data, method = "BinSeg", Q = 3)
    binseg_cpts <- cpts(cpt_binseg)
    
    cat("🔍 BinSeg Change Points detected at positions:", binseg_cpts, "\n")
    if (length(binseg_cpts) > 0) {
      binseg_years <- time_vector[binseg_cpts]
      cat("📅 BinSeg Change Point Years:", paste(round(binseg_years, 2), collapse = ", "), "\n")
    }
  }, error = function(e) {
    cat("❌ BinSeg analysis failed:", e$message, "\n")
    binseg_cpts <- integer(0)
    binseg_years <- numeric(0)
  })
  
  # 3. Bayesian Change Point (if data not too large)
  if (length(ts_data) <= 500) {
    tryCatch({
      bcp_result <- bcp(ts_data, mcmc = 1000, burnin = 100)
      bcp_probs <- bcp_result$posterior.prob
      
      # Find positions with high change point probability (>0.5)
      bcp_cpts <- which(bcp_probs > 0.5)
      
      cat("🔍 Bayesian Change Points (prob > 0.5) at positions:", bcp_cpts, "\n")
      if (length(bcp_cpts) > 0) {
        bcp_years <- time_vector[bcp_cpts]
        cat("📅 Bayesian Change Point Years:", paste(round(bcp_years, 2), collapse = ", "), "\n")
      }
    }, error = function(e) {
      cat("❌ Bayesian analysis failed:", e$message, "\n")
      bcp_cpts <- integer(0)
      bcp_years <- numeric(0)
    })
  } else {
    cat("⏭️  Skipping Bayesian analysis (dataset too large)\n")
    bcp_cpts <- integer(0)
    bcp_years <- numeric(0)
  }
  
  # Calculate before/after statistics for most significant change point
  main_changepoint <- NULL
  if (length(pelt_cpts) > 0) {
    # Use the first PELT change point as primary
    cp_pos <- pelt_cpts[1]
    cp_year <- time_vector[cp_pos]
    
    before_data <- ts_data[1:(cp_pos-1)]
    after_data <- ts_data[cp_pos:length(ts_data)]
    
    main_changepoint <- list(
      position = cp_pos,
      year = cp_year,
      mean_before = mean(before_data, na.rm = TRUE),
      mean_after = mean(after_data, na.rm = TRUE),
      n_before = length(before_data),
      n_after = length(after_data),
      magnitude_change = mean(after_data, na.rm = TRUE) - mean(before_data, na.rm = TRUE)
    )
    
    cat("📊 Primary Change Point at", round(cp_year, 2), "\n")
    cat("   Before:", round(main_changepoint$mean_before, 6), 
        "(n =", main_changepoint$n_before, ")\n")
    cat("   After: ", round(main_changepoint$mean_after, 6), 
        "(n =", main_changepoint$n_after, ")\n")
    cat("   Change:", round(main_changepoint$magnitude_change, 6), "\n")
  }
  
  return(list(
    dataset = dataset_name,
    variable = variable,
    pelt_changepoints = if(exists("pelt_years")) pelt_years else numeric(0),
    binseg_changepoints = if(exists("binseg_years")) binseg_years else numeric(0),
    bayesian_changepoints = if(exists("bcp_years")) bcp_years else numeric(0),
    primary_changepoint = main_changepoint
  ))
}

# =============================================================================
# 6. CORRELATION ANALYSIS FUNCTIONS
# =============================================================================

# Cross-dataset correlation analysis
perform_correlation_analysis <- function(matched_data) {
  cat("\n=== CROSS-DATASET CORRELATION ANALYSIS ===\n")
  
  # Overall correlation
  overall_corr <- cor.test(matched_data$mcd43a3_albedo, matched_data$mod10a1_albedo, 
                          method = "pearson")
  
  cat("📊 Overall Pearson Correlation:", round(overall_corr$estimate, 4), "\n")
  cat("📈 p-value:", format(overall_corr$p.value, scientific = TRUE), "\n")
  cat("📏 95% CI: [", round(overall_corr$conf.int[1], 4), ", ", 
      round(overall_corr$conf.int[2], 4), "]\n")
  
  # Seasonal correlations
  seasonal_corr <- matched_data %>%
    group_by(season) %>%
    summarise(
      n_obs = n(),
      correlation = cor(mcd43a3_albedo, mod10a1_albedo, use = "complete.obs"),
      mean_diff = mean(mod10a1_albedo - mcd43a3_albedo, na.rm = TRUE),
      rmse = sqrt(mean((mod10a1_albedo - mcd43a3_albedo)^2, na.rm = TRUE)),
      .groups = 'drop'
    )
  
  cat("\n📅 Seasonal Correlations:\n")
  print(seasonal_corr)
  
  # Test for significant differences in correlations
  seasons <- unique(matched_data$season)
  if (length(seasons) >= 2) {
    cat("\n🔍 Testing correlation differences between seasons:\n")
    for (i in 1:(length(seasons)-1)) {
      for (j in (i+1):length(seasons)) {
        s1_data <- matched_data[matched_data$season == seasons[i], ]
        s2_data <- matched_data[matched_data$season == seasons[j], ]
        
        if (nrow(s1_data) > 10 && nrow(s2_data) > 10) {
          # Fisher's z-transformation for correlation comparison
          r1 <- cor(s1_data$mcd43a3_albedo, s1_data$mod10a1_albedo, use = "complete.obs")
          r2 <- cor(s2_data$mcd43a3_albedo, s2_data$mod10a1_albedo, use = "complete.obs")
          
          z1 <- 0.5 * log((1 + r1) / (1 - r1))
          z2 <- 0.5 * log((1 + r2) / (1 - r2))
          
          se_diff <- sqrt(1/(nrow(s1_data)-3) + 1/(nrow(s2_data)-3))
          z_stat <- (z1 - z2) / se_diff
          p_value <- 2 * (1 - pnorm(abs(z_stat)))
          
          cat("   ", seasons[i], "vs", seasons[j], ": z =", round(z_stat, 3), 
              ", p =", format(p_value, digits = 3), "\n")
        }
      }
    }
  }
  
  return(list(
    overall_correlation = overall_corr,
    seasonal_correlations = seasonal_corr,
    n_observations = nrow(matched_data)
  ))
}

# =============================================================================
# 7. MAIN ANALYSIS EXECUTION
# =============================================================================

# Main analysis function
run_comprehensive_analysis <- function() {
  cat("🚀 Starting Comprehensive Saskatchewan Glacier Albedo Analysis\n")
  cat("=" %R% 70 %R% "\n\n")
  
  # Extract data
  cat("📊 EXTRACTING DATA FROM DATABASE\n")
  mcd43a3_data <- extract_albedo_data(con, "mcd43a3")
  mod10a1_data <- extract_albedo_data(con, "mod10a1")
  matched_data <- extract_matched_data(con)
  
  # Initialize results storage
  results <- list()
  
  # 1. Trend Analysis
  cat("\n🔍 PERFORMING TREND ANALYSIS\n")
  results$mcd43a3_trends <- perform_trend_analysis(mcd43a3_data, "MCD43A3")
  results$mod10a1_trends <- perform_trend_analysis(mod10a1_data, "MOD10A1")
  
  # 2. Change Point Detection
  cat("\n📍 PERFORMING CHANGE POINT DETECTION\n")
  results$mcd43a3_changepoints <- perform_changepoint_analysis(mcd43a3_data, "MCD43A3")
  results$mod10a1_changepoints <- perform_changepoint_analysis(mod10a1_data, "MOD10A1")
  
  # 3. Correlation Analysis
  cat("\n🔗 PERFORMING CORRELATION ANALYSIS\n")
  results$correlation_analysis <- perform_correlation_analysis(matched_data)
  
  # 4. Summary Report
  cat("\n📋 ANALYSIS SUMMARY\n")
  cat("=" %R% 50 %R% "\n")
  
  cat("\n📈 TREND RESULTS:\n")
  cat("MCD43A3 Sen's Slope:", format(results$mcd43a3_trends$sens_slope$estimates, digits = 6), "units/year\n")
  cat("MOD10A1 Sen's Slope:", format(results$mod10a1_trends$sens_slope$estimates, digits = 6), "units/year\n")
  
  cat("\n📍 CHANGE POINTS:\n")
  if (length(results$mcd43a3_changepoints$pelt_changepoints) > 0) {
    cat("MCD43A3 Primary Change Point:", round(results$mcd43a3_changepoints$pelt_changepoints[1], 2), "\n")
  }
  if (length(results$mod10a1_changepoints$pelt_changepoints) > 0) {
    cat("MOD10A1 Primary Change Point:", round(results$mod10a1_changepoints$pelt_changepoints[1], 2), "\n")
  }
  
  cat("\n🔗 CORRELATION:\n")
  cat("Overall Dataset Correlation:", round(results$correlation_analysis$overall_correlation$estimate, 4), "\n")
  
  # Save results
  timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
  save(results, file = paste0("saskatcheawan_albedo_R_analysis_", timestamp, ".RData"))
  cat("\n💾 Results saved to: saskatcheawan_albedo_R_analysis_", timestamp, ".RData\n")
  
  return(results)
}

# =============================================================================
# 8. EXECUTION
# =============================================================================

# Run the analysis
if (interactive()) {
  cat("🔬 Running in interactive mode. Execute run_comprehensive_analysis() to start.\n")
} else {
  # Run automatically if script is executed
  tryCatch({
    results <- run_comprehensive_analysis()
    cat("\n✅ Analysis completed successfully!\n")
  }, error = function(e) {
    cat("\n❌ Analysis failed:", e$message, "\n")
  }, finally = {
    # Close database connection
    if (exists("con") && !is.null(con)) {
      dbDisconnect(con)
      cat("🔌 Database connection closed\n")
    }
  })
}

# =============================================================================
# END OF SCRIPT
# =============================================================================