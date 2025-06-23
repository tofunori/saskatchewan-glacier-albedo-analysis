#!/usr/bin/env Rscript
# =============================================================================
# Saskatchewan Glacier Albedo - Simple R Analysis
# =============================================================================
# 
# Simplified version focusing on essential statistical tests only
# Requires minimal R packages for basic trend analysis

cat("🚀 Saskatchewan Glacier Albedo - Simple R Analysis\n")
cat(paste(rep("=", 50), collapse = ""), "\n\n")

# Essential packages only
essential_packages <- c(
  "DBI",           # Database interface (usually pre-installed)
  "RPostgreSQL"    # PostgreSQL connection
)

# Check if packages are available
missing_packages <- essential_packages[!(essential_packages %in% installed.packages()[,"Package"])]

if(length(missing_packages) > 0) {
  cat("❌ Missing essential packages:", paste(missing_packages, collapse = ", "), "\n")
  cat("💡 Please install manually:\n")
  cat("   install.packages(c('DBI', 'RPostgreSQL'))\n")
  cat("   Or answer 'yes' when prompted\n\n")
  
  # Try to install with user confirmation
  install.packages(missing_packages, repos = "https://cran.rstudio.com/")
}

# Load essential libraries
suppressMessages({
  library(DBI)
  library(RPostgreSQL)
})

cat("✅ Essential packages loaded\n\n")

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
    return(con)
  }, error = function(e) {
    cat("❌ Database connection failed:", e$message, "\n")
    return(NULL)
  })
}

# =============================================================================
# BASIC TREND ANALYSIS (BUILT-IN R FUNCTIONS ONLY)
# =============================================================================

# Simple Mann-Kendall test using base R
simple_mann_kendall <- function(x) {
  n <- length(x)
  if (n < 3) return(list(S = NA, tau = NA, p_value = NA))
  
  # Calculate S statistic
  S <- 0
  for (i in 1:(n-1)) {
    for (j in (i+1):n) {
      S <- S + sign(x[j] - x[i])
    }
  }
  
  # Calculate tau
  tau <- S / (n * (n - 1) / 2)
  
  # Variance of S (simplified, assuming no ties)
  var_S <- n * (n - 1) * (2 * n + 5) / 18
  
  # Z statistic
  if (S > 0) {
    z <- (S - 1) / sqrt(var_S)
  } else if (S < 0) {
    z <- (S + 1) / sqrt(var_S)
  } else {
    z <- 0
  }
  
  # Two-tailed p-value (approximate)
  p_value <- 2 * (1 - pnorm(abs(z)))
  
  return(list(
    S = S,
    tau = tau,
    z_score = z,
    p_value = p_value,
    trend = ifelse(p_value < 0.05, ifelse(S > 0, "Increasing", "Decreasing"), "No Trend")
  ))
}

# Simple Sen's slope using base R
simple_sens_slope <- function(x, time = NULL) {
  n <- length(x)
  if (is.null(time)) time <- 1:n
  
  slopes <- c()
  for (i in 1:(n-1)) {
    for (j in (i+1):n) {
      if (time[j] != time[i]) {
        slope <- (x[j] - x[i]) / (time[j] - time[i])
        slopes <- c(slopes, slope)
      }
    }
  }
  
  return(median(slopes, na.rm = TRUE))
}

# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

analyze_dataset <- function(con, dataset_name) {
  cat("\n=== ANALYZING", toupper(dataset_name), "===\n")
  
  # Extract data
  query <- paste0("
    SELECT 
      decimal_year,
      pure_ice_mean
    FROM albedo.", dataset_name, "_measurements
    WHERE pure_ice_mean IS NOT NULL
    ORDER BY decimal_year
  ")
  
  data <- dbGetQuery(con, query)
  
  if (nrow(data) == 0) {
    cat("❌ No data found for", dataset_name, "\n")
    return(NULL)
  }
  
  cat("📊 Extracted", nrow(data), "observations\n")
  
  # Basic statistics
  albedo_values <- data$pure_ice_mean
  time_values <- data$decimal_year
  
  cat("📈 Mean albedo:", round(mean(albedo_values, na.rm = TRUE), 4), "\n")
  cat("📉 Min-Max albedo:", round(min(albedo_values, na.rm = TRUE), 4), "-", 
      round(max(albedo_values, na.rm = TRUE), 4), "\n")
  
  # Trend analysis
  mk_result <- simple_mann_kendall(albedo_values)
  sens_slope <- simple_sens_slope(albedo_values, time_values)
  
  cat("🔍 Mann-Kendall S:", mk_result$S, "\n")
  cat("📊 Kendall's tau:", round(mk_result$tau, 4), "\n")
  cat("📈 p-value:", format(mk_result$p_value, scientific = TRUE), "\n")
  cat("📉 Sen's slope:", format(sens_slope, digits = 6), "albedo/year\n")
  cat("🎯 Trend:", mk_result$trend, "\n")
  
  # Calculate total change over time period
  time_span <- max(time_values) - min(time_values)
  total_change <- sens_slope * time_span
  cat("📏 Total change over", round(time_span, 1), "years:", 
      format(total_change, digits = 4), "albedo units\n")
  
  return(list(
    dataset = dataset_name,
    n_obs = nrow(data),
    mean_albedo = mean(albedo_values, na.rm = TRUE),
    time_span = time_span,
    mk_result = mk_result,
    sens_slope = sens_slope,
    total_change = total_change
  ))
}

# =============================================================================
# CORRELATION ANALYSIS
# =============================================================================

analyze_correlation <- function(con) {
  cat("\n=== CROSS-DATASET CORRELATION ===\n")
  
  query <- "
    SELECT 
      m1.decimal_year,
      m1.pure_ice_mean as mcd43a3_albedo,
      m2.pure_ice_mean as mod10a1_albedo
    FROM albedo.mcd43a3_measurements m1
    INNER JOIN albedo.mod10a1_measurements m2 
      ON m1.date = m2.date
    WHERE m1.pure_ice_mean IS NOT NULL 
      AND m2.pure_ice_mean IS NOT NULL
    ORDER BY m1.decimal_year
  "
  
  matched_data <- dbGetQuery(con, query)
  
  if (nrow(matched_data) == 0) {
    cat("❌ No matched data found\n")
    return(NULL)
  }
  
  cat("📊 Matched observations:", nrow(matched_data), "\n")
  
  # Correlation analysis
  corr_result <- cor.test(matched_data$mcd43a3_albedo, matched_data$mod10a1_albedo)
  
  cat("🔗 Pearson correlation:", round(corr_result$estimate, 4), "\n")
  cat("📈 p-value:", format(corr_result$p.value, scientific = TRUE), "\n")
  cat("📊 95% CI: [", round(corr_result$conf.int[1], 4), ", ", 
      round(corr_result$conf.int[2], 4), "]\n")
  
  # Mean difference
  mean_diff <- mean(matched_data$mod10a1_albedo - matched_data$mcd43a3_albedo, na.rm = TRUE)
  cat("📏 Mean difference (MOD10A1 - MCD43A3):", round(mean_diff, 6), "\n")
  
  return(list(
    n_matched = nrow(matched_data),
    correlation = corr_result$estimate,
    p_value = corr_result$p.value,
    conf_int = corr_result$conf.int,
    mean_difference = mean_diff
  ))
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

run_simple_analysis <- function() {
  # Connect to database
  con <- connect_to_database()
  if (is.null(con)) {
    stop("Cannot proceed without database connection")
  }
  
  # Initialize results
  results <- list()
  
  # Analyze both datasets
  results$mcd43a3 <- analyze_dataset(con, "mcd43a3")
  results$mod10a1 <- analyze_dataset(con, "mod10a1")
  
  # Correlation analysis
  results$correlation <- analyze_correlation(con)
  
  # Summary comparison
  cat("\n📋 SUMMARY COMPARISON\n")
  cat(paste(rep("=", 30), collapse = ""), "\n")
  
  if (!is.null(results$mcd43a3) && !is.null(results$mod10a1)) {
    cat("Sen's Slope Comparison:\n")
    cat("  MCD43A3:", format(results$mcd43a3$sens_slope, digits = 6), "albedo/year\n")
    cat("  MOD10A1:", format(results$mod10a1$sens_slope, digits = 6), "albedo/year\n")
    
    ratio <- results$mod10a1$sens_slope / results$mcd43a3$sens_slope
    cat("  Ratio (MOD10A1/MCD43A3):", round(ratio, 2), "x\n")
    
    cat("\nTrend Significance:\n")
    cat("  MCD43A3:", results$mcd43a3$mk_result$trend, 
        "(p =", format(results$mcd43a3$mk_result$p_value, digits = 3), ")\n")
    cat("  MOD10A1:", results$mod10a1$mk_result$trend, 
        "(p =", format(results$mod10a1$mk_result$p_value, digits = 3), ")\n")
  }
  
  # Close database connection
  dbDisconnect(con)
  cat("\n🔌 Database connection closed\n")
  
  # Save results
  timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
  save(results, file = paste0("simple_albedo_analysis_", timestamp, ".RData"))
  cat("💾 Results saved to: simple_albedo_analysis_", timestamp, ".RData\n")
  
  cat("\n✅ Simple analysis completed successfully!\n")
  return(results)
}

# Run the analysis
if (interactive()) {
  cat("🔬 Interactive mode. Run: run_simple_analysis()\n")
} else {
  tryCatch({
    results <- run_simple_analysis()
  }, error = function(e) {
    cat("❌ Analysis failed:", e$message, "\n")
  })
}

# =============================================================================
# END OF SIMPLE SCRIPT
# =============================================================================