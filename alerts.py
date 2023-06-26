from pyairtable import Table
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from datetime import timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()  

airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_name = os.getenv('AIRTABLE_BASE')
alerts_table = Table(base_id=base_name, table_name='Alerts', api_key=airtable_api_key)
stays_table = Table(base_id=base_name, table_name='Stays', api_key=airtable_api_key)

def update_alerts_stays(alert_ids, alert_on=True):
    print('Retrieving alerts with specified alert_ids...')
    # Assuming 'id' is a field in your table
    alerts = alerts_table.all(formula="OR(" + ', '.join([f'alert_id = "{alert_id}"' for alert_id in alert_ids]) + ")")

    print(f"Retrieved {len(alerts)} alerts")

    stays = {}
    for alert in alerts:
        print(f"Processing alert with ID {alert['id']}...")
        start_date = parse(alert['fields']['date_range_start'])
        end_date = parse(alert['fields']['date_range_end'])
        dates = list(rrule(DAILY, dtstart=start_date, until=end_date - timedelta(days=1)))

        for check_in_date in dates:
            check_out_date = check_in_date + timedelta(days=1)
            stay_id = f"{alert['fields']['hotel_code'][0]}-{check_in_date.strftime('%Y-%m-%d')}-{check_out_date.strftime('%Y-%m-%d')}"
            print(f"Generated stay_id: {stay_id}")
            
            if stay_id in stays:
                stays[stay_id]['alert_emails'].append(alert['fields'].get('user_email', []))
                if alert_on:
                    stays[stay_id]['is_active'] = True
                print(f"Stay already exists in stays. Appended email {alert['fields'].get('user_email', [])} to alert_emails.")
            else:
                stays[stay_id] = {
                    'alert_emails': alert['fields'].get('user_email', []),
                    'is_active': True # if alert_on = True, the alert should be active. If alert_on = False, the alert should be inactive
                }
                print(f"Created new stay with stay_id {stay_id} and email {alert['fields'].get('user_email', [])}")

    print('Retrieving existing stays from Stays table...')
    existing_stays = stays_table.all(formula="OR(" + ', '.join([f'stay_id = "{stay_id}"' for stay_id in stays.keys()]) + ")")
    print(f"Retrieved {len(existing_stays)} existing stays")

    print('Updating stays with existing alert_emails...')
    for existing_stay in existing_stays:
        print(existing_stay)
        existing_alert_emails = existing_stay['fields'].get('alert_emails', [])
                
        if alert_on:
            existing_alert_emails.extend(email for email in stays[existing_stay['fields']['stay_id']]['alert_emails'] if email not in existing_alert_emails)
            stays[existing_stay['fields']['stay_id']]['alert_emails'] = existing_alert_emails
            print(f"Appended new emails to existing emails for stay_id {existing_stay['fields']['stay_id']}")
        else:
            stays[existing_stay['fields']['stay_id']]['alert_emails'] = [email for email in existing_alert_emails if email not in stays[existing_stay['fields']['stay_id']]['alert_emails']]
            print(f"Removed emails from alert_emails for stay_id {existing_stay['fields']['stay_id']}")

            if not stays[existing_stay['fields']['stay_id']]['alert_emails']:
                stays[existing_stay['fields']['stay_id']]['is_active'] = False
                print(f"Set is_active to False for stay_id {existing_stay['fields']['stay_id']} as there are no more alert_emails")

    # After updating the existing stays, update the rest of the stays that do not exist in `existing_stays`
    if not alert_on:
        for stay_id in stays:
            if stay_id not in [existing_stay['fields']['stay_id'] for existing_stay in existing_stays]:
                stays[stay_id]['alert_emails'] = []
                stays[stay_id]['is_active'] = False

    print(stays)
    print('Preparing data for batch_upsert...')
    data_for_upsert = [{"fields": {'stay_id': stay_id, 'alert_emails': info['alert_emails'], 'is_active': info['is_active']}} for stay_id, info in stays.items()]
    stays_table.batch_upsert(data_for_upsert, key_fields=['stay_id'])
    print("Upsert complete!")

def update_active_alerts():
    print('Retrieving active alerts...')
    active_alerts = alerts_table.all(formula="is_active=1")  # retrieves only active alerts

    print(f"Found {len(active_alerts)} active alerts.")
    for alert in active_alerts:
        print(f"Updating stays for alert {alert['id']}")
        update_alerts_stays(alert['id'], alert_on=False)


    # print('Data for batch_upsert:')
    # for item in data_for_upsert:
    #     print(item)

# test = stays_table.all(formula="stay_id = 'cdgys-2023-08-19-2023-08-20'")
# print(test)


# Use the function
# alerts = ["1",
#           "2",
#           "3"]

# update_alerts_stays(alerts)

update_active_alerts()