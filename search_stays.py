from pyairtable import Table
from datetime import datetime, timedelta
import json
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE')
TABLE_NAME = 'Stays'

stays_table = Table(API_KEY, BASE_ID, TABLE_NAME)

def fetch_stays_from_airtable(start_date, end_date, length_of_stay, hotel_name_text, hotel_city=None, hotel_country=None, rate_filter=None):
    filter_formula = f"AND( \
        {{check_in_date}} >= '{datetime.strptime(start_date, '%Y-%m-%d').date()}', \
        {{check_in_date}} <= '{datetime.strptime(end_date, '%Y-%m-%d').date() - timedelta(days=length_of_stay)}', \
        FIND('{hotel_name_text}', {{hotel_name}}) > 0, \
        OR(FIND('{hotel_city}', {{hotel_city}}) > 0, '{hotel_city}' = BLANK()), \
        OR(FIND('{hotel_country}', {{hotel_country}}) > 0, '{hotel_country}' = BLANK()), \
        FIND('{rate_filter}', {{rate_filter}}) > 0 \
    )"
    
    return stays_table.all(formula=filter_formula, sort=["hotel_name_text", "check_in_date"])

def get_consecutive_stays(data, num_consecutive_days):
    # Convert date strings to datetime objects and group data by hotel_name_text
    hotel_data = defaultdict(list)
    for d in data:
        d = {
            **d, 
            "fields": {
                **d["fields"], 
                "check_in_date": datetime.strptime(d["fields"]["check_in_date"], "%Y-%m-%d")
            }
        }
        hotel_data[d["fields"]["hotel_name_text"]].append(d)
    
    # Loop through each hotel
    for hotel_name, data in hotel_data.items():
        # Loop through the data
        for i in range(len(data) - num_consecutive_days + 1):
            dates = [data[i+j]["fields"]["check_in_date"] for j in range(num_consecutive_days)]
            # If the dates are consecutive
            if all((dates[j+1] - dates[j]).days == 1 for j in range(len(dates)-1)):
                # Return the hotel name, first date, and last date + 1 day to show the whole range of dates
                yield hotel_name, dates[0], dates[-1] + timedelta(days=1)

def search_consecutive_stays(start_date, end_date, length_of_stay, hotel_name_text=None, hotel_city=None, hotel_country=None, rate_filter=None, max_points_budget=None):
    records = fetch_stays_from_airtable(start_date=start_date, end_date=end_date, length_of_stay=length_of_stay, hotel_name_text=hotel_name_text, hotel_city=hotel_city, hotel_country=hotel_country, rate_filter=rate_filter)

    consecutive_stays = list(get_consecutive_stays(records, length_of_stay))

    for hotel_name, start_date, end_date in consecutive_stays:
        print(f"Found {length_of_stay}-night consecutive stays at {hotel_name} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    return consecutive_stays

consecutive_stays = search_consecutive_stays('2023-08-01',
        '2023-08-31',
        7,
        hotel_name_text='',
        hotel_city='',
        hotel_country='',
        rate_filter='Standard')

print(consecutive_stays)

# print(fetch_stays('2023-08-01',
#              '2023-08-31',
#              3,
#              hotel_name_text='',
#              hotel_city='Paris',
#              hotel_country='',
#              rate_filter='Standard'))