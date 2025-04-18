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

# Path to the Excel file
excel_file_path = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/election25data.xls'

# Try to determine file extension
file_extension = excel_file_path.split('.')[-1].lower()

# Select the appropriate engine based on the file extension
if file_extension == 'xls':
    engine = 'xlrd'
    print("Using xlrd engine for .xls file")
elif file_extension == 'xlsx':
    engine = 'openpyxl'
    print("Using openpyxl engine for .xlsx file")
else:
    # Try both engines
    print(f"Unknown extension: {file_extension}. Trying xlrd first...")
    engine = 'xlrd'

try:
    # Load the Excel file into a DataFrame with specified engine
    df = pd.read_excel(excel_file_path, engine=engine)
except Exception as e:
    if engine == 'xlrd':
        print(f"Failed with xlrd: {e}. Trying openpyxl...")
        engine = 'openpyxl'
        try:
            df = pd.read_excel(excel_file_path, engine=engine)
        except Exception as e2:
            print(f"Failed with openpyxl as well: {e2}")
            raise
    else:
        print(f"Failed with {engine}: {e}")
        raise

print(f"Successfully loaded Excel file using {engine} engine")

# Load the Excel file into a DataFrame
df = pd.read_excel(excel_file_path)

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

# Save the final cleaned DataFrame without the report links
# Filter out the ReportLink column before saving
final_df = clean_df.drop(columns=['ReportLink'])

# Save the final cleaned DataFrame as a new CSV
final_df.to_csv('election2025.csv', index=False)

print("Processing complete. File saved as 'election2025.csv'")