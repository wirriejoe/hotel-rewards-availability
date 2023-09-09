import pandas as pd

# Read the CSV file into a pandas DataFrame
df = pd.read_csv("ihg_hotels_metadata.csv")

# Separate the DataFrame into two parts: one with 'hotel_code' values and another without
df_with_code = df[df['Hotel Code'].notna()]
df_without_code = df[df['Hotel Code'].isna()]

# Deduplicate the DataFrame that has 'hotel_code' values
df_with_code_deduplicated = df_with_code.drop_duplicates(subset=["Hotel Code"])

# Combine the deduplicated DataFrame with the one that had NaN 'hotel_code' values
df_final = pd.concat([df_with_code_deduplicated, df_without_code])

# Save the final DataFrame back to a CSV file
df_final.to_csv("ihg_hotels_metadata_deduplicated.csv", index=False)
