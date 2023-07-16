import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY
import logging
import time
from dotenv import load_dotenv, find_dotenv
import os

# initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(find_dotenv())

# PostgreSQL connection URL
connection_url = os.getenv('POSTGRES_DB_URL')

# establish a database connection
conn = psycopg2.connect(connection_url)

# create a new dictionary cursor object
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

logging.info('Retrieving all alerts where is_active = true')
start_time = time.time()
# Step 1: Retrieve all alerts where is_active = true
cur.execute("SELECT hotels.hotel_id, hotel_code, search_start_date, search_end_date FROM hotels where award_category <> '';")
hotels = cur.fetchall()
logging.info(f'Retrieved {len(hotels)} alerts in {time.time() - start_time} seconds')

# Step 2: Generate unique new_stays
logging.info('Generating new stays')
start_time = time.time()
new_stays = {}

for hotel in hotels:
    start_date = hotel['search_start_date']
    end_date = hotel['search_end_date']
    date_range = list(rrule(DAILY, dtstart=start_date, until=end_date - timedelta(days=1)))
    
    for date in date_range:
        stay_id = f"{hotel['hotel_code']}-{date.strftime('%Y-%m-%d')}-{(date + timedelta(days=1)).strftime('%Y-%m-%d')}"
        new_stays[stay_id] = {
            'hotel_id': hotel['hotel_id'],
            'hotel_code': hotel['hotel_code'],
            'check_in_date': date.strftime('%Y-%m-%d'),
            'check_out_date': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
            'status': 'Active',
            'last_checked_time': datetime(1900, 1, 1, 0, 0, 0)
        }

logging.info(f'Generated {len(new_stays)} new stays in {time.time() - start_time} seconds')

logging.info('Retrieving all existing stays')
start_time = time.time()
# Step 3: Retrieve all existing_stays from stays table
cur.execute("SELECT * FROM stays;")
existing_stays = cur.fetchall()
logging.info(f'Retrieved {len(existing_stays)} existing stays in {time.time() - start_time} seconds')

# Step 4: Modify new_stays based on existing_stays
logging.info('Modifying new stays based on existing stays')
start_time = time.time()

for existing_stay in existing_stays:
    stay_id = existing_stay['stay_id']
    if stay_id in new_stays:
        # Remove from upsert list if there are no changes
        del new_stays[stay_id]
        logging.info(f"Deleted existing {existing_stay['stay_id']} in {time.time() - start_time} seconds")
    

logging.info(f'Modified new stays in {time.time() - start_time} seconds')

# Step 5: Upsert new_stays to stays table
logging.info('Upserting new stays to stays table')
start_time = time.time()

# print(new_stays)
for stay_id, stay_info in new_stays.items():
    print(stay_id)
    query = """
    INSERT INTO stays (stay_id, hotel_id, hotel_code, check_in_date, check_out_date, status, last_checked_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (stay_id) DO UPDATE
    SET status = excluded.status, last_checked_time = excluded.last_checked_time;
    """
    cur.execute(query, (stay_id, stay_info['hotel_id'], stay_info['hotel_code'], stay_info['check_in_date'], stay_info['check_out_date'], stay_info['status'], stay_info['last_checked_time']))

    logging.info(f"Upserted {stay_id} in {time.time() - start_time} seconds")

logging.info(f'Upserted new stays to stays table in {time.time() - start_time} seconds')

# commit the transaction
conn.commit()

# close the cursor and connection
cur.close()
conn.close()

logging.info('All steps completed successfully')