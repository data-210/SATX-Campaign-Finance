import pdfplumber
import re
import pandas as pd
from ace_tools import display_dataframe_to_user

pdf_path = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/Sorensen30dayfiling.pdf'
contrib_records = []
exp_records = []

with pdfplumber.open(pdf_path) as pdf:
    # Extract totals from cover sheet for reference (not used in merged DataFrame)
    cover_text = pdf.pages[1].extract_text() or ""
    nums = re.findall(r'[\d,]+\.\d{2}', cover_text)
    
    # Parse Schedule A1: Monetary Political Contributions
    for page in pdf.pages:
        text = page.extract_text()
        if text and 'MONETARY POLITICAL CONTRIBUTIONS' in text:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                m = re.match(r'^(\d{1,2}/\d{1,2}/\d{4}).*?([\d,]+\.\d{2})$', line.strip())
                if m:
                    date_str, amt_str = m.groups()
                    name = lines[i-1].strip()
                    contrib_records.append({
                        'date': pd.to_datetime(date_str, format='%m/%d/%Y'),
                        'name': name,
                        'amount': float(amt_str.replace(',', '')),
                        'type': 'Contribution'
                    })
    # Parse Schedule F1: Political Expenditures Made From Political Contributions
    in_f1 = False
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        lines = text.split('\n')
        if any(line.strip() == 'F1:' or 'Schedule F1' in line for line in lines):
            in_f1 = True
        if in_f1:
            for i, line in enumerate(lines):
                m1 = re.match(r'^(\d{1,2}/\d{1,2}/\d{4})\s+(.+)$', line.strip())
                if m1:
                    date_str, payee = m1.groups()
                    # Look ahead for amount
                    amount = None
                    for j in range(i+1, min(i+6, len(lines))):
                        m2 = re.match(r'^([\d,]+\.\d{2})\b', lines[j].strip())
                        if m2:
                            amount = float(m2.group(1).replace(',', ''))
                            break
                    if amount is not None:
                        exp_records.append({
                            'date': pd.to_datetime(date_str, format='%m/%d/%Y'),
                            'name': payee.strip(),
                            'amount': amount,
                            'type': 'Expenditure'
                        })

# Create DataFrames
df_contrib = pd.DataFrame(contrib_records)
df_exp = pd.DataFrame(exp_records)

# Merge into one DataFrame
df_merged = pd.concat([df_contrib, df_exp], ignore_index=True)

# Display
display_dataframe_to_user("Combined Schedule A1 and F1 Records", df_merged)
