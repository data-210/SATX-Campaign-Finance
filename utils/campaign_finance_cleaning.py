import pandas as pd
import openpyxl
import re

# Function to extract hyperlinks from Excel
def extract_hyperlinks(excel_file_path):
    wb = openpyxl.load_workbook(excel_file_path)
    sheet = wb.active
    hyperlinks = []

    # Loop through the rows in the first column to find hyperlinks
    for row in sheet.iter_rows(min_row=1, max_col=1, values_only=False):
        cell = row[0]
        if cell.hyperlink:
            hyperlinks.append(cell.hyperlink.target)
        else:
            hyperlinks.append(None)
    
    return hyperlinks

# Function to extract 5-digit zip codes from the "Name:" column
def extract_zip_code(address):
    if pd.notna(address):
        match = re.search(r'\b\d{5}\b', address)
        if match:
            return match.group(0)
    return None

# Paths to the single CSV and Excel files
csv_file_path = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/election25.csv'
excel_file_path = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/election25.xlsx'

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Extract zip codes from the "Name:" column (adjust column name if different)
df['ZipCode'] = df['Name:'].apply(extract_zip_code).shift(-2)

# Clean the data by retaining only the first row in each block (where 'Report Id:' is not NaN)
clean_df = df[df['Report Id:'].notna()].copy()

# Extract hyperlinks from the Excel file and add to DataFrame
hyperlinks = extract_hyperlinks(excel_file_path)

# Add hyperlinks to the cleaned DataFrame
clean_hyperlinks = []
link_idx = 0
for i in range(len(clean_df)):
    while link_idx < len(hyperlinks) and hyperlinks[link_idx] is None:
        link_idx += 1
    if link_idx < len(hyperlinks):
        clean_hyperlinks.append(hyperlinks[link_idx])
        link_idx += 1
    else:
        clean_hyperlinks.append(None)

clean_df['ReportLink'] = clean_hyperlinks

# Save the final cleaned DataFrame with hyperlinks and zip codes as a new CSV
clean_df.to_csv('election25update.csv', index=False)
