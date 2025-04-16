### Campaign Finance Election 2025 ###
# Load required libraries
library(shiny)
library(dplyr)
library(ggplot2)
library(DT)
library(lubridate)  # Helpful for date operations
library(shinydashboard)
library(ggthemes)
library(scales)

# --- Data Preparation ---
# Read the CSV file. (Place "election25update.csv" in your working directory or update the path accordingly.)
election_data <- read.csv("election25update.csv", stringsAsFactors = FALSE)
#View(election_data)

# Convert election_date to Date type. Adjust the format if necessary.
election_data$Election.Date. <- as.Date(election_data$Election.Date., 
                                        format = "%m/%d/%Y")

# Filter for May 3, 2025
filtered_data <- election_data %>%
  filter(Election.Date. == as.Date("2025-05-03"))
View(filtered_data)

# Filter for specific candidates
candidates <- c("CLAYTON PERRY", "Alberto Altamirano", "Adriana Garcia", 
                "Adriana Rocha Garcia", "Gina Jones", "Gina Ortiz Jones",
                "John Courage", "Manny Pelaez Pelaez", "Manny Pelaez",
                "Rolando Pablos", "Melissa Cabello Havrda")
filtered_data <- filtered_data %>%
  filter(Cand.Committee. %in% candidates)
unique(filtered_data$Cand.Committee.)
filtered_data <- filtered_data %>%
  mutate(Cand.Committee. = case_when(
    # Title case Clayton Perry
    toupper(Cand.Committee.) == "CLAYTON PERRY" ~ "Clayton Perry",
    # Merge AGR variants
    Cand.Committee. %in% c("Adriana Garcia", "Adriana Rocha Garcia", "Adriana Garcia Rocha") ~ "Adriana Rocha Garcia",
    # Merge GOJ variants
    Cand.Committee. %in% c("Gina Jones", "Gina Ortiz Jones") ~ "Gina Ortiz Jones",
    TRUE ~ Cand.Committee.
  ))

# Fix Amount column
filtered_data <- filtered_data %>%
  mutate(
    `Amount.` = dollar(`Amount.`, prefix = "$", big.mark = ",", accuracy = 1)
  )
# Add Amount_num column
filtered_data <- filtered_data %>%
  mutate(Amount_num = parse_number(`Amount.`))

# Change strVal col name
filtered_data <- filtered_data %>% rename(CF_Type = strVal)

# Write to csv
write.csv(filtered_data, "top8_mayoral.csv", row.names = FALSE)
