# Install necessary packages if not already installed
if (!require("readxl")) install.packages("readxl")
if (!require("tidyverse")) install.packages("tidyverse")
if (!require("stringr")) install.packages("stringr")

# Load libraries
library(readxl)
library(tidyverse)
library(stringr)

# Function to extract 5-digit zip codes from the "Name:" column
extract_zip_code <- function(address) {
  if (!is.na(address)) {
    # Extract 5-digit sequence
    zip_match <- str_extract(address, "\\b\\d{5}\\b")
    return(zip_match)
  }
  return(NA)
}

# Path to the Excel file - Make sure this path is correct
excel_file_path <- "/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/election25data.xls"

# Check if file exists
if (!file.exists(excel_file_path)) {
  stop("File does not exist at: ", excel_file_path)
}

# Read the Excel file
tryCatch({
  cat("Attempting to read Excel file...\n")
  df <- read_excel(excel_file_path)
  cat("Successfully read the file!\n")
}, error = function(e) {
  cat("Error reading Excel file:", e$message, "\n")
  
  # Try with different sheet index
  tryCatch({
    cat("Trying to read with sheet index 1...\n")
    df <<- read_excel(excel_file_path, sheet = 1)
    cat("Successfully read the file using sheet index 1!\n")
  }, error = function(e2) {
    cat("Error reading with sheet index:", e2$message, "\n")
    
    # Try as CSV
    tryCatch({
      cat("Trying to read as CSV...\n")
      df <<- read.csv(excel_file_path)
      cat("Successfully read as CSV!\n")
    }, error = function(e3) {
      cat("Error reading as CSV:", e3$message, "\n")
      stop("Unable to read the file in any format. Please check if the file exists and is not corrupted.")
    })
  })
})

# Print basic information about the dataframe
cat("Dataframe dimensions:", dim(df)[1], "rows by", dim(df)[2], "columns\n")
cat("Column names:", paste(colnames(df), collapse = ", "), "\n")

# Extract zip codes from the "Name:" column if it exists
if ("Name:" %in% colnames(df)) {
  df <- df %>%
    mutate(ZipCode = lag(sapply(df$`Name:`, extract_zip_code), -2))
  cat("Added ZipCode column\n")
} else {
  cat("Warning: 'Name:' column not found.\n")
  # Try to find similar column names
  similar_cols <- grep("name", tolower(colnames(df)), value = TRUE)
  if (length(similar_cols) > 0) {
    cat("Found similar columns that might contain names:", pa