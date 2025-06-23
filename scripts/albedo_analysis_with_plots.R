#!/usr/bin/env Rscript
# =============================================================================
# Saskatchewan Glacier Albedo Analysis - Simple Version with Plots
# =============================================================================
# 
# Clean, simple analysis with basic visualizations
# Requires: ggplot2, dplyr, DBI, RPostgreSQL

cat("🚀 Saskatchewan Glacier Albedo Analysis with Plots\n")
cat(paste(rep("=", 50), collapse = ""), "\n\n")

# Required packages
required_packages <- c("DBI", "RPostgreSQL", "ggplot2", "dplyr")

# Check for missing packages
missing_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(missing_packages) > 0) {
  cat("❌ Missing packages:", paste(missing_packages, collapse = ", "), "\n")
  cat("💡 Install with: install.packages(c(", paste0("'", missing_packages, "'", collapse = ", "), "))\n")
  stop("Please install missing packages first.")
}

# Load libraries
suppressMessages({
  library(DBI)
  library(RPostgreSQL)
  library(ggplot2)
  library(dplyr)
})

cat("✅ Packages loaded successfully\n\n")

# =============================================================================
# DATABASE CONNECTION
# =============================================================================

connect_to_database <- function() {
  tryCatch({
    drv <- dbDriver("PostgreSQL")
    con <- dbConnect(drv, 
                     dbname = "saskatchewan_albedo",
                     host = "/var/run/postgresql",
                     user = Sys.getenv("USER"))
    
    cat("✅ Connected to PostgreSQL database\n")
    con
  }, error = function(e) {
    cat("❌ Database connection failed:", e$message, "\n")
    NULL
  })
}

# =============================================================================
# DATA EXTRACTION
# =============================================================================

extract_dataset <- function(con, dataset_name) {
  query <- paste0("
    SELECT 
      date,
      decimal_year,
      season,
      pure_ice_mean as albedo,
      pure_ice_pixel_count as pixel_count
    FROM albedo.", dataset_name, "_measurements
    WHERE pure_ice_mean IS NOT NULL
    ORDER BY date
  ")
  
  data <- dbGetQuery(con, query)
  data$date <- as.Date(data$date)
  data$dataset <- toupper(dataset_name)
  
  cat("📊 Extracted", nrow(data), "observations for", toupper(dataset_name), "\n")
  data
}

extract_matched_data <- function(con) {
  query <- "
    SELECT 
      m1.date,
      m1.decimal_year,
      m1.pure_ice_mean as mcd43a3_albedo,
      m2.pure_ice_mean as mod10a1_albedo
    FROM albedo.mcd43a3_measurements m1
    INNER JOIN albedo.mod10a1_measurements m2 
      ON m1.date = m2.date
    WHERE m1.pure_ice_mean IS NOT NULL 
      AND m2.pure_ice_mean IS NOT NULL
    ORDER BY m1.date
  "
  
  data <- dbGetQuery(con, query)
  data$date <- as.Date(data$date)
  
  cat("📊 Extracted", nrow(data), "matched observations\n")
  data
}

# =============================================================================
# STATISTICAL ANALYSIS
# =============================================================================

analyze_trends <- function(data) {
  results <- list()
  
  for(dataset in unique(data$dataset)) {
    subset_data <- data[data$dataset == dataset, ]
    
    # Basic statistics
    results[[dataset]] <- list(
      n_obs = nrow(subset_data),
      mean_albedo = mean(subset_data$albedo, na.rm = TRUE),
      min_albedo = min(subset_data$albedo, na.rm = TRUE),
      max_albedo = max(subset_data$albedo, na.rm = TRUE),
      time_span = max(subset_data$decimal_year) - min(subset_data$decimal_year)
    )
    
    # Simple linear trend
    lm_model <- lm(albedo ~ decimal_year, data = subset_data)
    results[[dataset]]$slope <- coef(lm_model)[2]
    results[[dataset]]$p_value <- summary(lm_model)$coefficients[2, 4]
    results[[dataset]]$r_squared <- summary(lm_model)$r.squared
    
    # Total change over time period
    results[[dataset]]$total_change <- results[[dataset]]$slope * results[[dataset]]$time_span
    
    cat("\n=== ", dataset, " ANALYSIS ===\n")
    cat("📊 Observations:", results[[dataset]]$n_obs, "\n")
    cat("📈 Mean albedo:", round(results[[dataset]]$mean_albedo, 4), "\n")
    cat("📉 Range:", round(results[[dataset]]$min_albedo, 4), "-", round(results[[dataset]]$max_albedo, 4), "\n")
    cat("📈 Trend slope:", format(results[[dataset]]$slope, digits = 6), "albedo/year\n")
    cat("📊 P-value:", format(results[[dataset]]$p_value, scientific = TRUE), "\n")
    cat("📏 Total change:", format(results[[dataset]]$total_change, digits = 4), "albedo units\n")
  }
  
  results
}

analyze_correlation <- function(matched_data) {
  corr_test <- cor.test(matched_data$mcd43a3_albedo, matched_data$mod10a1_albedo)
  
  cat("\n=== CORRELATION ANALYSIS ===\n")
  cat("📊 Matched observations:", nrow(matched_data), "\n")
  cat("🔗 Correlation:", round(corr_test$estimate, 4), "\n")
  cat("📈 P-value:", format(corr_test$p.value, scientific = TRUE), "\n")
  
  list(
    correlation = corr_test$estimate,
    p_value = corr_test$p.value,
    n_matched = nrow(matched_data)
  )
}

# =============================================================================
# VISUALIZATION
# =============================================================================

create_time_series_plot <- function(data) {
  p <- ggplot(data, aes(x = date, y = albedo, color = dataset)) +
    geom_point(alpha = 0.6, size = 0.8) +
    geom_smooth(method = "lm", se = TRUE, alpha = 0.3) +
    labs(
      title = "Saskatchewan Glacier Albedo Time Series (2010-2024)",
      x = "Date",
      y = "Albedo",
      color = "Dataset"
    ) +
    theme_minimal() +
    theme(legend.position = "bottom")
  
  ggsave("results/albedo_time_series.png", p, width = 12, height = 6, dpi = 300)
  cat("💾 Saved: results/albedo_time_series.png\n")
}

create_correlation_plot <- function(matched_data) {
  corr_coef <- round(cor(matched_data$mcd43a3_albedo, matched_data$mod10a1_albedo), 3)
  
  p <- ggplot(matched_data, aes(x = mcd43a3_albedo, y = mod10a1_albedo)) +
    geom_point(alpha = 0.6, color = "steelblue") +
    geom_smooth(method = "lm", se = TRUE, color = "red", alpha = 0.3) +
    labs(
      title = paste0("Dataset Correlation (r = ", corr_coef, ")"),
      x = "MCD43A3 Albedo",
      y = "MOD10A1 Albedo"
    ) +
    theme_minimal()
  
  ggsave("results/albedo_correlation.png", p, width = 8, height = 6, dpi = 300)
  cat("💾 Saved: results/albedo_correlation.png\n")
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

run_analysis <- function() {
  # Connect to database
  con <- connect_to_database()
  if (is.null(con)) {
    stop("Cannot proceed without database connection")
  }
  
  # Create results directory
  if (!dir.exists("results")) {
    dir.create("results")
  }
  
  # Extract data
  mcd43a3_data <- extract_dataset(con, "mcd43a3")
  mod10a1_data <- extract_dataset(con, "mod10a1")
  matched_data <- extract_matched_data(con)
  
  # Combine datasets for plotting
  all_data <- rbind(mcd43a3_data[, c("date", "decimal_year", "albedo", "dataset")],
                    mod10a1_data[, c("date", "decimal_year", "albedo", "dataset")])
  
  # Statistical analysis
  trend_results <- analyze_trends(all_data)
  corr_results <- analyze_correlation(matched_data)
  
  # Create visualizations
  create_time_series_plot(all_data)
  create_correlation_plot(matched_data)
  
  # Close database connection
  dbDisconnect(con)
  cat("\n🔌 Database connection closed\n")
  
  # Save results
  results <- list(
    trends = trend_results,
    correlation = corr_results,
    timestamp = Sys.time()
  )
  
  timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
  save(results, file = paste0("results/albedo_analysis_", timestamp, ".RData"))
  cat("💾 Results saved to: results/albedo_analysis_", timestamp, ".RData\n")
  
  cat("\n✅ Analysis completed successfully!\n")
  cat("📊 Check the 'results/' directory for plots and data\n")
  
  results
}

# Run the analysis
if (interactive()) {
  cat("🔬 Interactive mode. Run: run_analysis()\n")
} else {
  tryCatch({
    results <- run_analysis()
  }, error = function(e) {
    cat("❌ Analysis failed:", e$message, "\n")
  })
}