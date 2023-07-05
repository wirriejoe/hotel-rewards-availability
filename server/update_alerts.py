from pyairtable import Table
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from datetime import timedelta, datetime
from dotenv import load_dotenv
import os

load_dotenv()  

airtable_api_key = os.getenv('AIRTABLE_API_KEY')
base_name = os.getenv('AIRTABLE_BASE')
alerts_table = Table(base_id=base_name, table_name='Alerts', api_key=airtable_api_key)
stays_table = Table(base_id=base_name, table_name='Stays', api_key=airtable_api_key)

def update_alert(alerts, alert_on=True):
    stays = {}

    print('Processing alerts and generating stays...')
    for alert in alerts:
        start_date = parse(alert['fields']['date_range_start'])
        end_date = parse(alert['fields']['date_range_end'])
        dates = list(rrule(DAILY, dtstart=start_date, until=end_date - timedelta(days=1)))

        for check_in_date in dates:
            check_out_date = check_in_date + timedelta(days=1)
            stay_id = f"{alert['fields']['hotel_code'][0]}-{check_in_date.strftime('%Y-%m-%d')}-{check_out_date.strftime('%Y-%m-%d')}"
            
            stays[stay_id] = {
                'alert_emails': alert['fields'].get('user_email', []),
                'hotel_name': alert['fields'].get('hotel_name', []),
                'check_in_date': check_in_date.isoformat(),
                'check_out_date': check_out_date.isoformat(),
                'last_checked_time': datetime(1900, 1, 1, 0, 0, 0).isoformat(),
                'status': 'Active' if alert_on else 'Inactive'
            }
            
    print('Retrieving existing stays...')
    existing_stays = stays_table.all()

    print('Updating generated stays with existing alert emails...')
    for existing_stay in existing_stays:
        stay_id = existing_stay['fields']['stay_id']
        if stay_id in stays:
            new_alert_emails = list(set(stays[stay_id]['alert_emails'] + existing_stay['fields'].get('alert_emails', [])))
            # Check if there are changes
            if stays[stay_id]['alert_emails'] != new_alert_emails:
                # Update if there are changes
                stays[stay_id]['alert_emails'] = new_alert_emails
                stays[stay_id]['last_checked_time'] = existing_stay['fields']['last_checked_time']
            else:
                # Remove from upsert list if there are no changes
                del stays[stay_id]
    
    print('Preparing data for batch_upsert...')
    data_for_upsert = [{"fields": {'stay_id': stay_id, **stay}} for stay_id, stay in stays.items()]
    stays_table.batch_upsert(data_for_upsert, key_fields=['stay_id'])
    print("Upsert complete!")

def update_active_alerts():
    print('Retrieving active alerts...')
    active_alerts = alerts_table.all(formula='is_active=1')  # retrieves only active alerts

    print(f"Found {len(active_alerts)} active alerts.")
    add_alert(active_alerts)
    # delete_alert(active_alerts)

def add_alert(alerts):
    update_alert(alerts, alert_on=True)

def delete_alert(alerts):
    update_alert(alerts, alert_on=False)

update_active_alerts()