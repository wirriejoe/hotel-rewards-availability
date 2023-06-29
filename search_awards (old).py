import os
from airtable import Airtable
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
import pytz
import time
import random
from dotenv import load_dotenv
from award_search import AwardSearch

# Load environment variables
load_dotenv()

airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_name = os.getenv('AIRTABLE_BASE')
alerts_table = Airtable(base_name, 'Alerts', airtable_api_key)
awards_table = Airtable(base_name, 'Awards', airtable_api_key)
stays_table = Airtable(base_name, 'Stays', airtable_api_key)

def main():
    awardsearch = AwardSearch()
    
    # Step 1: Get the records from the Alerts table
    alerts = alerts_table.get_all(formula="AND(is_active = 1)")
    
    for alert in alerts:
        fields = alert['fields']
        print(fields['hotel_brand'][0])
        print(fields['hotel_code'][0])
        print(fields['date_range_start'])
        print(fields['date_range_end'])

        hotel_name = fields['hotel_name']
        hotel_brand = fields['hotel_brand'][0]
        hotel_code = fields['hotel_code'][0]
        user_email = fields['user_email'][0]

        date_range_start = datetime.strptime(fields['date_range_start'], '%Y-%m-%d')
        date_range_end = datetime.strptime(fields['date_range_end'], '%Y-%m-%d')

        check_in_date = date_range_start
        while check_in_date < date_range_end:

            check_out_date = (check_in_date + timedelta(days=1)).strftime('%Y-%m-%d')
            check_in_date = check_in_date.strftime('%Y-%m-%d')

            time_check_query = f"{hotel_code}-{check_in_date}-{check_out_date}"
            time_checks = stays_table.search('stay_id', time_check_query)
            
            # Get UTC time
            utc_time = datetime.now(pytz.timezone('US/Pacific')).astimezone(pytz.UTC)

            if time_checks:
                time_check = time_checks[0]
                time_check_id = time_checks[0]['id']
                last_checked_time = parse_date(time_check['fields']['last_checked_time'])
                if (datetime.now(pytz.UTC) - last_checked_time) < timedelta(hours=3):
                    print(f"Skipping stay {time_check_query}, it was checked within the last hour.")
                    check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d') + timedelta(days=1)
                    continue
                stays_table.update(time_checks[0]['id'], {
                    'last_checked_time': str(utc_time)
                })
            else:
                time_check_id = stays_table.insert({
                    'stay_id': time_check_query,
                    'last_checked_time': str(utc_time)
                })['id']

            # Step 2: Search for awards
            award_stays = awardsearch.get_award_stays(hotel_brand, hotel_code, check_in_date, check_out_date)

            for room_details in award_stays:
                if room_details['Lowest Point Value'] is None:
                    print("No award stays available.")
                    continue
                # Step 3: Create award_id
                award_id = f"{hotel_code}-{check_in_date}-{check_out_date}-{room_details['Room Type Code']}-{room_details['Room Category']}"
                print(award_id)

                # Step 4 & 5: Check if award exists in Awards table and update/insert accordingly
                awards = awards_table.search('award_id', award_id)

                room_quantity = room_details.get('Room Quantity', 0)
                # Get UTC time
                utc_time = datetime.now(pytz.timezone('US/Pacific')).astimezone(pytz.UTC)
                if awards:  # Stay exists
                    awards_table.update(awards[0]['id'], {
                        'lowest_points_rate': room_details['Lowest Point Value'],
                        'cash_rate': room_details['Lowest Public Rate'],
                        'currency_code': room_details['Currency Code'],
                        'availability': room_quantity,
                        'search_url': room_details['Search URL'],
                        'stay_id': [time_check_id]
                        })
                else:  # Stay does not exist
                    awards_table.insert({
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
                        'stay_id': [time_check_id]
                    })
            print("Finished with " + hotel_code + " from " + check_in_date + " to " + check_out_date + "!")
            check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d') + timedelta(days=1)
            time.sleep(random.randint(5, 10))
    awardsearch.quit()

if __name__ == "__main__":
    main()
