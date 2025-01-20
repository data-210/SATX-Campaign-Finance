import pandas as pd

# File paths
file_1 = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/campaign_finance20241031.csv'
file_2 = '/Users/jackturek/Documents/Repos/SATX-Campaign-Finance/data/campaignfinancedata01202025.csv'

df1 = pd.read_csv(file_1)
df2 = pd.read_csv(file_2)

# Merge
campaign_finance_df = pd.concat([df1, df2], ignore_index = True)

campaign_finance_df.to_csv('campaign_finance.csv', index=False)