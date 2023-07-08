from pyairtable import Table
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv(os.path.realpath(os.path.join(os.path.dirname(__file__), '../.env')))

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

def get_consecutive_stays(data, num_consecutive_days, rate_filter = None, max_points_budget = 0):
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
            stays = [data[i+j] for j in range(num_consecutive_days)]
            dates = [stay["fields"]["check_in_date"] for stay in stays]
            
            # If the dates are consecutive
            if all((dates[j+1] - dates[j]).days == 1 for j in range(len(dates)-1)):
                # Calculate max last_checked, average standard_rate and average premium_rate
                
                last_checked = max(stay["fields"]["last_checked"] for stay in stays)
                if sum(1 for stay in stays if stay["fields"].get("standard_rate")) == num_consecutive_days:
                    standard_rate = sum(stay["fields"]["standard_rate"] for stay in stays) / len(stays)
                else:
                    standard_rate = 0
                if sum(1 for stay in stays if stay["fields"].get("premium_rate")) == num_consecutive_days:
                    premium_rate = sum(stay["fields"]["premium_rate"] for stay in stays) / len(stays)
                else:
                    premium_rate = 0
                
                if max_points_budget == 0 or (standard_rate <= max_points_budget and standard_rate > 0 and rate_filter != 'Premium') or (premium_rate <= max_points_budget and premium_rate > 0 and rate_filter != 'Standard'):
                    # Yield the results
                    yield {
                        'hotel_name': hotel_name,
                        'date_range_start': dates[0],
                        'date_range_end': dates[-1] + timedelta(days=1),
                        'last_checked': last_checked,
                        'standard_rate': standard_rate,
                        'premium_rate': premium_rate,
                        'hotel_city': stays[0]["fields"]["hotel_city"],
                        'hotel_country': stays[0]["fields"]["hotel_country"],
                    }

def search_by_consecutive_nights(start_date, end_date, length_of_stay, hotel_name_text=None, hotel_city=None, hotel_country=None, rate_filter=None, max_points_budget=0):
    records = fetch_stays_from_airtable(start_date=start_date, end_date=end_date, length_of_stay=length_of_stay, hotel_name_text=hotel_name_text, hotel_city=hotel_city, hotel_country=hotel_country, rate_filter=rate_filter)
    print(len(records))

    consecutive_stays = list(get_consecutive_stays(records, length_of_stay, rate_filter ,max_points_budget))

    return consecutive_stays