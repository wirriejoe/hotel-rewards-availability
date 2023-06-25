import os
from dotenv import load_dotenv
import json
import requests
from airtable import Airtable

# Go here to download JSON https://www.hyatt.com/development/explore-hotels/api/hotels

load_dotenv()

airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_name = os.getenv('AIRTABLE_BASE')
airtable = Airtable(base_name, 'Hotels', airtable_api_key)

# Load JSON file
with open('sources/hyatt.com_development_explore-hotels_api_hotels.txt') as f:
    data = json.load(f)

# Record the total number of hotels
print(f"Total number of hotels: {len(data)}")

# Iterate over each hotel in the JSON data
for index, hotel in enumerate(data, start=1):

    # Extract the required fields
    fields = {
        'hotel_name': hotel['name'],
        'hotel_longitude': hotel['longitude'],
        'hotel_latitude': hotel['latitude'],
        'property_type': hotel['propertyType'],
        'sub-brand': hotel['brand'],
        'hotel_code': hotel['spiritCode'].lower(),
        'hotel_country': hotel['country'],
        'hotel_region': hotel['region'],
        'hotel_city': hotel['city'],
        'hotel_address': hotel['address1'],
        'hotel_status': hotel['hotelStatus'],
        'hotel_zipcode': hotel['zipcode'],
        'hotel_province': hotel['province'],
        'hotel_url': hotel['propertySiteURL'],
        'opening_date': hotel['openingDate'],
        'room_count': hotel['roomCount'],
        'hotel_brand': 'Hyatt'
    }

    # Check if the hotel already exists in the Airtable
    records = airtable.search('hotel_code', hotel['spiritCode'].lower())

    if records:
        # If the hotel exists, update the record
        record_id = records[0]['id']
        airtable.update(record_id, fields)
        print(f"Hotel {index}/{len(data)}: {hotel['name']} updated.")
    else:
        # If the hotel doesn't exist, create a new record
        airtable.insert(fields)
        print(f"Hotel {index}/{len(data)}: {hotel['name']} added.")