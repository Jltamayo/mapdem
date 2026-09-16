# nuts_disaggregation.R
#
# When an indicator only exists at NUTS2, every child NUTS3 region inherits
# its parent's value. Each disaggregated row is tagged `is_duplicated`, so
# the front end can render it with a different visual treatment (hatching /
# lower opacity) instead of presenting it as a genuinely observed NUTS3
# value. See docs/methodology.md for the source and rationale.
#
# Run:
#   Rscript analysis/nuts_disaggregation.R

library(dplyr)

#' @param nuts3_df data.frame with column "nuts3" and indicator columns
#'   (values may be NA where only NUTS2 data exists)
#' @param nuts2_df data.frame with column "nuts2" and the same indicator
#'   columns, at NUTS2 resolution
#' @param crosswalk data.frame with columns "nuts3", "nuts2" mapping child to parent
#' @param indicator_cols character vector of indicator column names to fill
disaggregate_nuts2_to_nuts3 <- function(nuts3_df, nuts2_df, crosswalk, indicator_cols) {
  nuts3_df <- nuts3_df %>% left_join(crosswalk, by = "nuts3")

  for (col in indicator_cols) {
    flag_col <- paste0(col, "_is_duplicated")
    nuts3_df[[flag_col]] <- is.na(nuts3_df[[col]])

    missing_idx <- is.na(nuts3_df[[col]])
    if (any(missing_idx)) {
      parent_values <- nuts2_df[match(nuts3_df$nuts2[missing_idx], nuts2_df$nuts2), col]
      nuts3_df[[col]][missing_idx] <- parent_values
    }
  }
  nuts3_df
}

if (sys.nframe() == 0) {
  crosswalk <- tibble::tribble(
    ~nuts3,   ~nuts2,
    "ES511", "ES51",
    "ES512", "ES51",
    "ES513", "ES51",
    "ES514", "ES51"
  )

  nuts3_df <- tibble::tribble(
    ~nuts3,   ~democratic_trust,
    "ES511",  62.3,
    "ES512",  NA,     # will be filled from ES51
    "ES513",  NA,     # will be filled from ES51
    "ES514",  58.1
  )

  nuts2_df <- tibble::tribble(
    ~nuts2,  ~democratic_trust,
    "ES51",  55.0
  )

  result <- disaggregate_nuts2_to_nuts3(nuts3_df, nuts2_df, crosswalk, "democratic_trust")
  print(result)
}
