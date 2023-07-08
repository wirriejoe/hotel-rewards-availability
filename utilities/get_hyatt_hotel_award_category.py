import json
from pyairtable import Table
from dotenv import load_dotenv
import os

# Helper function to extract key and label from a dictionary
def extract_key_label(dictionary):
    if dictionary is None:
        return None, None
    else:
        return dictionary.get('key'), dictionary.get('label')

# Helper function to extract the address
def extract_address(location):
    if location is None:
        return None
    else:
        addressLine1 = location.get('addressLine1', '')
        addressLine2 = location.get('addressLine2', '')
        return addressLine1 + (' ' + addressLine2 if addressLine2 else '')


# load the JSON file
with open('utilities/hotels.json', 'r') as f:
    hotels = json.load(f)

# list to store hotel data
airtable_data = []

# loop through the hotels
for hotel_code, hotel in hotels.items():
    # Extract details from hotel
    spirit_code = hotel.get('spiritCode')
    award_category_key, award_category_label = extract_key_label(hotel.get('awardCategory'))
    brand_key, brand_label = extract_key_label(hotel.get('brand'))

    # Extract details from location
    location = hotel.get('location')
    hotel_address = extract_address(location)
    hotel_city = location.get('city')
    hotel_zipcode = location.get('zipcode')
    hotel_province_key, hotel_province_label = extract_key_label(location.get('stateProvince'))
    hotel_country_key, hotel_country = extract_key_label(location.get('country'))
    hotel_region_key, hotel_region = extract_key_label(location.get('region'))
    hotel_latitude = location.get('geolocation', {}).get('latitude')
    hotel_longitude = location.get('geolocation', {}).get('longitude')
    hotel_name = hotel.get('name')
    hotel_url = hotel.get('url')
    image = hotel.get('image')
    hotel_status = 'Open'

    # Prepare the data for Airtable
    airtable_record = {
        'hotel_name': hotel_name,
        "hotel_brand": 'Hyatt',
        "hotel_code": spirit_code,
        'image': image,
        "award_category": award_category_label,
        "brand": brand_label,
        "hotel_address": hotel_address,
        "hotel_city": hotel_city,
        "hotel_zipcode": hotel_zipcode,
        "hotel_province": hotel_province_label,
        "hotel_country": hotel_country,
        "hotel_region": hotel_region,
        "hotel_latitude": str(hotel_latitude),
        "hotel_longitude": str(hotel_longitude),
        'hotel_url': hotel_url,
        'hotel_status': 'Open'
    }

    print(airtable_record)

    # Add the data to the list
    airtable_data.append({"fields": airtable_record})
# now airtable_data is a list of dictionaries ready to be used with the Airtable API

load_dotenv(os.path.realpath(os.path.join(os.path.dirname(__file__), '../.env')))

airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_name = os.getenv('AIRTABLE_BASE')
hotels_table = Table(base_id=base_name, table_name='Hotels', api_key=airtable_api_key)

# Retrieve all records
all_records = hotels_table.all()

# Create a dictionary mapping hotel_codes to record_ids
existing_hotels = {record['fields']['hotel_code']: record['id'] for record in all_records if 'hotel_code' in record['fields']}
# print(existing_hotels)

# Loop through the data
for hotel in airtable_data:
    hotel_code = hotel['fields']['hotel_code']
    
    # If hotel exists, get its record_id
    if hotel_code in existing_hotels:
        hotel['id'] = existing_hotels[hotel_code]
        print(hotel['id'])

# Batch upsert
hotels_table.batch_upsert(airtable_data, key_fields=['hotel_name'])