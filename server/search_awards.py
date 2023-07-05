import os
from pyairtable import Table, formulas
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
import pytz
import time
import random
from dotenv import load_dotenv
from selenium_profiles.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from award_search import AwardSearch

# Load environment variables
load_dotenv()

airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_name = os.getenv('AIRTABLE_BASE')
alerts_table = Table(base_id=base_name, table_name='Alerts', api_key=airtable_api_key)
awards_table = Table(base_id=base_name, table_name='Awards', api_key=airtable_api_key)
stays_table = Table(base_id=base_name, table_name='Stays', api_key=airtable_api_key)

def update_awards_table(award_stays, stay):
    stay_fields = stay['fields']
    stay_id = stay_fields['stay_id']
    hotel_name = stay_fields['hotel_name']
    check_in_date = stay_fields['check_in_date']
    check_out_date = stay_fields['check_out_date']
    award_updates = []
    
    for room_details in award_stays:
        if room_details['Lowest Point Value'] is None:
            print("No award stays available.")
            continue
        # Step 3: Create award_id
        award_id = f"{stay_id}-{room_details['Room Type Code']}-{room_details['Room Category']}"
        print(award_id)

        room_quantity = room_details.get('Room Quantity', 0)

        award_updates.append({
            'fields': {
                'award_id': award_id,
                'hotel_name': hotel_name,
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
                'room_name': room_details['Room Name'],
                'room_type_code': room_details['Room Type Code'],
                'room_category': room_details['Room Category'],
                'lowest_points_rate': room_details['Lowest Point Value'],
                'cash_rate': room_details['Lowest Public Rate'],
                'currency_code': room_details['Currency Code'],
                'availability': room_quantity,
                'search_url': room_details['Search URL'],
                'stay_id': [stay['id']]
            }
        })
    
    print("Finished with " + hotel_name[0] + " from " + check_in_date + " to " + check_out_date + "!")

    return award_updates[0]

def search_awards(search_frequency_hours = 24, search_batch_size = 100):
    search_frequency = timedelta(hours=search_frequency_hours)
    
    awardsearch = AwardSearch()
    award_updates = []
    stay_updates = []
    
    # Step 1: Get the search_batch_size num records from the Stays table where status = Active and last_checked_time is longer than search_frequency (default 24 hours) and check_in_date is after today
    stays = stays_table.all(formula=f'AND(status="Active", \
                            DATETIME_DIFF(NOW(),last_checked_time,"hours")>={search_frequency_hours}), \
                            check_in_date>=today()\
                                ', max_records = search_batch_size)

    status_update = [{
        'id': stay['id'],
        'fields': {
        'status': 'Queued'
    }} for stay in stays]

    stays_table.batch_upsert(status_update, key_fields=['stay_id'])

    for stay in stays:
        stay_fields = stay['fields']
        hotel_code = stay_fields['hotel_code'][0]
        check_in_date = datetime.strptime(stay_fields['check_in_date'], '%Y-%m-%d').date()
        check_out_date = datetime.strptime(stay_fields['check_out_date'], '%Y-%m-%d').date()

        awards = awardsearch.get_award_stays(hotel_brand='Hyatt', 
                                             hotel_code=hotel_code, 
                                             checkin_date=check_in_date, 
                                             checkout_date=check_out_date)
        
        if awards:
            award_updates.append(update_awards_table(awards, stay))
        stay_updates.append({
            'id': stay['id'],
            'fields': {
                'last_checked_time': datetime.now(pytz.UTC).isoformat(),
                'status': 'Active'
            }
        })

        time.sleep(random.randint(1, 2))
    awards_table.batch_upsert(award_updates, key_fields=['award_id'])
    stays_table.batch_upsert(stay_updates, key_fields=['stay_id'])
    awardsearch.quit()

if __name__ == "__main__":
    search_awards(search_frequency_hours=24,search_batch_size=1000)