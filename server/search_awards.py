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
    
    for room_details in award_stays:
        if room_details['Lowest Point Value'] is None:
            print("No award stays available.")
            continue
        # Step 3: Create award_id
        award_id = f"{stay_id}-{room_details['Room Type Code']}-{room_details['Room Category']}"
        print(award_id)

        # Check if award exists in Awards table and update/insert accordingly
        existing_award = awards_table.all(formula=formulas.match({'award_id': award_id}))

        room_quantity = room_details.get('Room Quantity', 0)
        if existing_award:  # Award exists
            awards_table.update(existing_award[0]['id'], {
                'lowest_points_rate': room_details['Lowest Point Value'],
                'cash_rate': room_details['Lowest Public Rate'],
                'currency_code': room_details['Currency Code'],
                'availability': room_quantity,
                'search_url': room_details['Search URL'],
                'stay_id': [stay['id']]
                })
        else:  # Stay does not exist
            awards_table.create({
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
            })
    print("Finished with " + hotel_name[0] + " from " + check_in_date + " to " + check_out_date + "!")

def search_awards(search_frequency = timedelta(hours=24)):
    awardsearch = AwardSearch()
    
    # Step 1: Get the records from the Alerts table
    stays = stays_table.all(formula='AND(is_active = 1)')
    
    for stay in stays:
        stay_fields = stay['fields']
        hotel_code = stay_fields['hotel_code'][0]
        check_in_date = datetime.strptime(stay_fields['check_in_date'], '%Y-%m-%d').date()
        check_out_date = datetime.strptime(stay_fields['check_out_date'], '%Y-%m-%d').date()
        last_checked_time = parse_date(stay_fields['last_checked_time'])

        #skip if stay search had been searched more recently than search_frequency (e.g. 3 hours)
        if (datetime.now(pytz.UTC) - last_checked_time) < search_frequency:
            print(f"Skipping stay {stay_fields['stay_id']}, it was checked within the last hour.")
            continue
        
        awards = awardsearch.get_award_stays(hotel_brand='Hyatt', 
                                             hotel_code=hotel_code, 
                                             checkin_date=check_in_date, 
                                             checkout_date=check_out_date)
        update_awards_table(awards, stay)

        stays_table.update(stay['id'], {
                'last_checked_time': datetime.now(pytz.UTC).isoformat()
        })

        time.sleep(random.randint(3, 5))
    awardsearch.quit()

if __name__ == "__main__":
    search_awards()
    # stays = stays_table.all(max_records=1)
    # print(stays[0]['fields']['stay_id'])