import json
import csv

# Read and merge JSON files
with open('hilton_hotels.json', 'r') as file1, open('hilton_hotels_others.json', 'r') as file2:
    hilton_hotels = json.load(file1)
    hilton_hotels_others = json.load(file2)

merged_hotels = hilton_hotels + hilton_hotels_others

# Deduplicate
unique_hotels = list({hotel['hotel_code']: hotel for hotel in merged_hotels}.values())

# Add hotel_id starting from 2287
for idx, hotel in enumerate(unique_hotels, start=2287):
    hotel['hotel_id'] = idx

# Write to CSV
csv_columns = [
    'hotel_id', 'hotel_name', 'hotel_brand', 'sub_brand', 'hotel_code', 'image',
    'hotel_address', 'hotel_zipcode', 'hotel_city', 'hotel_province',
    'hotel_country', 'hotel_longitude', 'hotel_latitude', 'hotel_status'
]

with open('merged_hotels.csv', 'w', newline='') as csvfile:
    csvwriter = csv.DictWriter(csvfile, fieldnames=csv_columns)
    csvwriter.writeheader()
    for hotel in unique_hotels:
        csvwriter.writerow(hotel)