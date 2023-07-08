import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY
import logging
import time
from dotenv import load_dotenv
import os

# initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(os.path.realpath(os.path.join(os.path.dirname(__file__), '../.env')))

# PostgreSQL connection URL
connection_url = os.getenv('POSTGRES_DB_URL')

# establish a database connection
conn = psycopg2.connect(connection_url)

# create a new dictionary cursor object
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

logging.info('Retrieving all alerts where is_active = true')
start_time = time.time()
# Step 1: Retrieve all alerts where is_active = true
cur.execute("SELECT alerts.hotel_id, hotel_code, date_range_start, date_range_end, user_email FROM alerts LEFT JOIN hotels on alerts.hotel_id = hotels.hotel_id WHERE is_active = 'true';")
alerts = cur.fetchall()
logging.info(f'Retrieved {len(alerts)} alerts in {time.time() - start_time} seconds')

# Step 2: Generate unique new_stays
logging.info('Generating new stays')
start_time = time.time()
new_stays = {}

for alert in alerts:
    start_date = alert['date_range_start']
    end_date = alert['date_range_end']
    date_range = list(rrule(DAILY, dtstart=start_date, until=end_date - timedelta(days=1)))
    
    for date in date_range:
        stay_id = f"{alert['hotel_code']}-{date.strftime('%Y-%m-%d')}-{(date + timedelta(days=1)).strftime('%Y-%m-%d')}"
        new_stays[stay_id] = {
            'hotel_id': alert['hotel_id'],
            'user_email': alert['user_email'],
            'check_in_date': date.strftime('%Y-%m-%d'),
            'check_out_date': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
            'status': 'Active',
            'last_checked_time': datetime(1900, 1, 1, 0, 0, 0)
        }

logging.info(f'Generated {len(new_stays)} new stays in {time.time() - start_time} seconds')

logging.info('Retrieving all existing stays')
start_time = time.time()
# Step 3: Retrieve all existing_stays from stays table
cur.execute("UPDATE stays SET user_email = ''")
cur.execute("SELECT * FROM stays;")
existing_stays = cur.fetchall()
logging.info(f'Retrieved {len(existing_stays)} existing stays in {time.time() - start_time} seconds')

# Step 4: Modify new_stays based on existing_stays
logging.info('Modifying new stays based on existing stays')
start_time = time.time()

for existing_stay in existing_stays:
    stay_id = existing_stay['stay_id']
    if stay_id in new_stays:
        new_user_emails = list(set(new_stays[stay_id]['user_email'].split(',') + existing_stay.get('user_email', None).split(',')))
        print(new_user_emails)
        new_user_emails = ','.join(new_user_emails).strip(',')
        print(new_user_emails)
        if new_stays[stay_id]['user_email'] != new_user_emails:
            # Update if there are changes
            new_stays[stay_id]['user_email'] = new_user_emails
            new_stays[stay_id]['last_checked_time'] = existing_stay['last_checked_time']
            logging.info(f"Updated existing {existing_stay['stay_id']} in {time.time() - start_time} seconds")
        else:
            # Remove from upsert list if there are no changes
            del new_stays[stay_id]
            logging.info(f"Deleted existing {existing_stay['stay_id']} in {time.time() - start_time} seconds")
    

logging.info(f'Modified new stays in {time.time() - start_time} seconds')

# Step 5: Upsert new_stays to stays table
logging.info('Upserting new stays to stays table')
start_time = time.time()

print(new_stays)
for stay_id, stay_info in new_stays.items():
    print(stay_id)
    query = """
    INSERT INTO stays (stay_id, hotel_id, user_email, check_in_date, check_out_date, status, last_checked_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (stay_id) DO UPDATE
    SET user_email = excluded.user_email, status = excluded.status, last_checked_time = excluded.last_checked_time;
    """
    cur.execute(query, (stay_id, stay_info['hotel_id'], stay_info['user_email'], stay_info['check_in_date'], stay_info['check_out_date'], stay_info['status'], stay_info['last_checked_time']))

    logging.info(f"Upserted {stay_id} in {time.time() - start_time} seconds")

logging.info(f'Upserted new stays to stays table in {time.time() - start_time} seconds')

# commit the transaction
conn.commit()

# close the cursor and connection
cur.close()
conn.close()

logging.info('All steps completed successfully')