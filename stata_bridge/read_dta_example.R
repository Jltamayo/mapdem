# read_dta_example.R
#
# R-side equivalent of read_dta_example.py, for team members who prefer to
# ingest partner .dta files directly in R via the `haven` package. Either
# path converges on the same canonical CSV output in docs/data/processed/.
#
# Run:
#   Rscript stata_bridge/read_dta_example.R

library(haven)
library(readr)

dta_path <- file.path("data", "raw", "partner_model_output.dta")

if (!file.exists(dta_path)) {
  stop(
    "No .dta file found at ", dta_path,
    ". Run stata_bridge/read_dta_example.py first to generate a synthetic one, ",
    "or drop a real partner file at that path."
  )
}

df <- read_dta(dta_path)
print(df)

out_path <- file.path("docs", "data", "processed", "partner_model_output_from_R.csv")
write_csv(df, out_path)
message("Converted to canonical format: ", out_path)
