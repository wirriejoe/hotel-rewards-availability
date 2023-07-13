from dotenv import load_dotenv, find_dotenv
from airtable import Airtable
import os
import requests

load_dotenv(find_dotenv())

airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_key = os.getenv('AIRTABLE_BASE')
table_name = 'Hotels'

airtable = Airtable(base_key, table_name, airtable_api_key)

def get_hotel_data():
    url = 'https://maxmypoint.com/hotels?search=&sort=&order=&offset=0&limit=2000&brand=Hyatt'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data["rows"]
    else:
        print(f"Unable to get data. HTTP Status code: {response.status_code}")
        return None

def save_to_airtable(hotels_data):
    for hotel in hotels_data:
        record = {
            'hotel_name': hotel['name'],
            'hotel_brand': 'Hyatt',
            'hotel_code': hotel['code'],
            'image': hotel['image'],
            'hotel_address': '',  # We don't have this information in the current data
            'hotel_city': '',  # We don't have this information in the current data
            'hotel_country': '',  # We don't have this information in the current data
            'maxmypoint_hotel_id': hotel['id']
        }
        
        airtable.insert(record)

hotels_data = get_hotel_data()

if hotels_data is not None:
    save_to_airtable(hotels_data)