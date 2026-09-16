# composite_index.R
#
# Rank-based composite index method: rank each region on each indicator
# (reversed for undesirable indicators), normalise by the number of regions
# with valid data for that indicator, average within a domain, then average
# across domains. Chosen because it only needs one valid indicator per
# region/domain, which tolerates the "highly inhomogeneous" missingness
# expected across many countries and national statistical systems.
# See docs/methodology.md for the full rationale and source.
#
# Run:
#   Rscript analysis/composite_index.R

library(dplyr)
library(tidyr)
library(readr)

DATA_DIR <- file.path("docs", "data", "processed")

#' Convert a single indicator column into normalised rank fractions.
#' @param x numeric vector, may contain NA
#' @param direction "high_is_good" or "low_is_good"
rank_fraction <- function(x, direction = c("high_is_good", "low_is_good")) {
  direction <- match.arg(direction)
  n_valid <- sum(!is.na(x))
  if (n_valid <= 1) return(rep(NA_real_, length(x)))

  r <- rank(if (direction == "high_is_good") -x else x,
            na.last = "keep", ties.method = "average")
  (n_valid - r) / (n_valid - 1)
}

#' Build one domain index from several indicator columns, averaging across
#' regions with at least one valid indicator.
#' @param df data.frame with a region id column plus indicator columns
#' @param id_col name of the region identifier column
#' @param indicators named list: indicator column -> direction
build_domain_index <- function(df, id_col, indicators) {
  fractions <- lapply(names(indicators), function(col) {
    rank_fraction(df[[col]], indicators[[col]])
  })
  names(fractions) <- names(indicators)
  frac_df <- as_tibble(fractions)

  tibble(
    !!id_col := df[[id_col]],
    domain_index = rowMeans(frac_df, na.rm = TRUE),
    n_indicators_used = rowSums(!is.na(frac_df))
  )
}

if (sys.nframe() == 0) {
  df <- read_csv(file.path(DATA_DIR, "synthetic_indicators.csv"), show_col_types = FALSE)

  indicators <- list(
    objective_inequality_index = "low_is_good",
    perceived_injustice        = "low_is_good",
    civic_participation        = "high_is_good",
    democratic_trust           = "high_is_good",
    media_access_index         = "high_is_good"
  )

  result <- build_domain_index(df, "nuts3", indicators)
  print(result)

  out_path <- file.path(DATA_DIR, "composite_index.csv")
  write_csv(result, out_path)
  message("Wrote ", out_path,
          " — once validated, point docs/index.html at this file for the drill-down view.")
}
