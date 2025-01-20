import pandas as pd

# Paths to the single CSV and Excel files
csv_file_path = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/campaignfinance_01202024.csv'
excel_file_path = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/campaignfinance_01202024.xlsx'

# Load data
df_csv = pd.read_csv(csv_file_path)
df_excel = pd.read_excel(excel_file_path)

# Convert TransDate col to datetime
df_csv['TransDate:'] = pd.to_datetime(df_csv['TransDate:'], errors='coerce')
df_excel['TransDate:'] = pd.to_datetime(df_excel['TransDate:'], errors='coerce')

# Filter for dates on or after 10/27/2024
filtered_csv = df_csv[df_csv['TransDate:'] >= pd.Timestamp('10/27/24')]
filtered_excel = df_excel[df_excel['TransDate:'] >= pd.Timestamp('10/27/24')]

# Save filtered datasets
filtered_csv.to_csv("campaignfinanceupdatejan25.csv", index=False)
filtered_excel.to_excel("campaignfinanceupdatejan25.xlsx", index=False)


