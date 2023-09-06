from sqlalchemy import create_engine, MetaData, select, and_, update, func, case, text, join
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from award_search import AwardSearch
from retry import retry
from threading import Thread, Lock
from queue import Queue
import os
import pytz
import logging
import requests

# Load environment variables
# load_dotenv(os.path.realpath(os.path.join(os.path.dirname(__file__), '../.env')))
load_dotenv(find_dotenv())

# Set up logging
logging.basicConfig(level=logging.ERROR)

# Initialize connection and Session
database_url = os.getenv('POSTGRES_DB_URL')
print("Database URL: %s", database_url)  # Use lazy logging format
engine = create_engine(database_url) # add , echo=True for logging
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
meta.reflect(bind=engine)

# Map tables
stays = meta.tables['stays']
awards = meta.tables['awards']
hotels = meta.tables['hotels']
temp_awards = meta.tables['temp_awards']

award_updates = []
stay_updates = []
search_counter = 0
counter_lock = Lock()

def upsert(session, table_name, list_of_dicts, unique_columns):
    # Prepare the base INSERT statement
    keys = list_of_dicts[0].keys()
    columns = ', '.join(keys)
    values = ', '.join([f":{key}" for key in keys])
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
    
    # Prepare the UPDATE statement for conflict
    update_str = ', '.join([f"{col}=EXCLUDED.{col}" for col in keys])
    conflict_str = ', '.join(unique_columns)
    upsert_sql = f"{insert_sql} ON CONFLICT ({conflict_str}) DO UPDATE SET {update_str}"
    
    # Execute the raw SQL upsert query
    session.execute(text(upsert_sql), list_of_dicts)
    session.commit()

    if table_name == temp_awards:
        print("Calling tempAwards webhook!")
        url = "https://api.retool.com/v1/workflows/412574f5-d537-442e-b2cb-4becd78c4cdb/startTrigger"
        params = {'workflowApiKey': 'retool_wk_4c776ddd5e9a4168839e4af2afeacc6c'}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("Request successful:", response.json())
        else:
            print("Request failed:", response.status_code)
            send_error_to_slack("tempAwards webhook error: " + response)


def update_awards_table(award_stays, stay_record):
    # Replaced 'stay' with 'stay_record' to avoid naming conflict with stay from the outer function
    stay_fields = stay_record
    stay_id = stay_fields['stay_id']
    hotel_id = stay_fields['hotel_id']
    check_in_date = stay_fields['check_in_date']
    check_out_date = stay_fields['check_out_date']
    award_data_to_update = []
    
    for room_details in award_stays:
        if room_details['Lowest Point Value'] is None:
            print("No award stays available.")
            continue
        # Step 3: Create award_id
        award_id = f"{stay_id}-{room_details['Room Type Code']}-{room_details['Room Category']}"
        print(award_id)

        room_quantity = room_details.get('Room Quantity', 0)

        award_data_to_update.append({
            'award_id': award_id,
            'hotel_id': hotel_id,
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
            'stay_id': stay_id,
            'last_checked_time': datetime.now(pytz.UTC)
        })
    
    print("Finished with hotel ID " + str(hotel_id) + " from " + str(check_in_date) + " to " + str(check_out_date) + "!")
    return award_data_to_update

# Create a worker function
def worker(task_queue, award_updates, stay_updates, counter_lock):
    awardsearch = AwardSearch()  # Initialize the driver here
    while not task_queue.empty():
        stay = task_queue.get()._asdict()

        with counter_lock:
            global search_counter  # Make sure to declare this variable as global at the start of your script
            search_counter += 1
            print(f"Searching #{search_counter} stay! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        
        hotel_code = stay['hotel_code']
        check_in_date = stay['check_in_date']
        check_out_date = stay['check_out_date']

        award_stays = awardsearch.get_award_stays(
            hotel_brand='Hyatt',
            hotel_code=hotel_code,
            checkin_date=check_in_date,
            checkout_date=check_out_date
        )
        
        if award_stays:
            award_data = update_awards_table(award_stays, stay)
            
            # Update award_updates and stay_updates in a thread-safe way
            with counter_lock:
                award_updates.extend(award_data)
        
        with counter_lock:
            stay_updates.append({
                'stay_id': stay['stay_id'],
                'last_checked_time': datetime.now(pytz.UTC),
                'status': 'Active'
            })
    awardsearch.quit()

def search_awards(search_frequency_hours = 24, search_batch_size = 1000):
    global search_counter
    global start_timer
    start_timer = datetime.now()
    
    stay_records = session.execute(
        select(*stays.c)
        .select_from(
            join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)
        )
        .where(
            and_(
                stays.c.status == "Active", 
                stays.c.last_checked_time < datetime.now(pytz.UTC) - timedelta(hours=search_frequency_hours),
                stays.c.check_in_date >= datetime.now(pytz.UTC).date(),
                hotels.c.hotel_brand == 'hyatt'
            )
        )
        .order_by(stays.c.last_checked_time)
        .limit(search_batch_size)
    ).fetchall()

    # Update status of fetched stay_records to 'Queued'
    stay_ids_to_update = [record.stay_id for record in stay_records]
    update_query = stays.update().where(stays.c.stay_id.in_(stay_ids_to_update)).values(status='Queued', last_queued_time=datetime.now(pytz.UTC))
    session.execute(update_query)
    session.commit()

    task_queue = Queue()
    for stay in stay_records:
        task_queue.put(stay)
    
    num_threads = 18 # You can change this number
    threads = []
    
    for _ in range(num_threads):
        t = Thread(target=worker, args=(task_queue, award_updates, stay_updates, counter_lock))
        threads.append(t)
        t.start()
    
    print("Finished jobs! Closing out threads.")

    for t in threads:
        t.join()
    
    print("Finished joining threads! Upserting data.")
    print(f"Num award updates: {len(award_updates)}")
    print(f"Num stay updates: {len(stay_updates)}")
    upsert(session, temp_awards, award_updates, ['award_id'])
    upsert(session, stays, stay_updates, ['stay_id'])

@retry(tries=5, delay=1, backoff=2)
def update_rates():
    print("Calling update_rates() webhook!")
    url = "https://api.retool.com/v1/workflows/c5027803-ab81-4c30-85cd-57748fe8f44f/startTrigger"
    params = {'workflowApiKey': 'retool_wk_a717023c42f24f558e28f0afe3dc2abb'}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Request successful:", response.json())
    else:
        print("Request failed:", response.status_code)
        send_error_to_slack("update_rates() webhook error: " + response)

    # print("Starting batch update of rates...")

    # # Prepare the raw SQL statement
    # stmt = text("""
    #     UPDATE stays
    #     SET 
    #         standard_rate = coalesce(subquery.min_standard_rate,0),
    #         premium_rate = coalesce(subquery.min_premium_rate,0),
    #         currency_code = subquery.currency_code,
    #         standard_cash = coalesce(subquery.min_standard_cash,0),
    #         premium_cash = coalesce(subquery.min_premium_cash,0),
    #         standard_cash_usd = coalesce(subquery.standard_cash_usd,0),
    #         premium_cash_usd = coalesce(subquery.premium_cash_usd,0),
    #         booking_url = search_url
    #     FROM (
    #         SELECT 
    #             stay_id,
    #             MIN(CASE WHEN room_category = 'STANDARD' AND last_checked_time >= now() - interval '48 hours' THEN lowest_points_rate ELSE 0 END) AS min_standard_rate,
    #             MIN(CASE WHEN room_category in ('SUITE','PREMIUM') AND last_checked_time >= now() - interval '48 hours' THEN lowest_points_rate ELSE 0 END) AS min_premium_rate,
    #             awards.currency_code,
    #             MIN(CASE WHEN room_category = 'STANDARD' AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal ELSE 0 END) AS min_standard_cash,
    #             MIN(CASE WHEN room_category in ('SUITE','PREMIUM') AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal ELSE 0 END) AS min_premium_cash,
    #             MIN(CASE WHEN room_category = 'STANDARD' AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal ELSE 0 END) * fx.usd_exchange_rate AS standard_cash_usd,
    #             MIN(CASE WHEN room_category in ('SUITE','PREMIUM') AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal ELSE 0 END) * fx.usd_exchange_rate AS premium_cash_usd,
    #             search_url
    #         FROM awards
    #         left join fx on awards.currency_code = fx.currency_code
    #         GROUP BY stay_id, search_url, awards.currency_code, fx.usd_exchange_rate
    #     ) AS subquery
    #     WHERE stays.stay_id = subquery.stay_id
    # """)

    # # Calculate available award inventory
    # stmt2 = text("""
    #     UPDATE stays
    #     SET available_inventory = subquery.stays_available::decimal / subquery.total_tracked_dates::decimal
    #     FROM (
    #     SELECT
    #         stay_id,
    #         sum(case when standard_rate > 0 or premium_rate > 0 then 1 else 0 end) over (partition by hotel_id) as stays_available,
    #         count(stay_id) over (partition by hotel_id) as total_tracked_dates
    #     FROM stays
    #     WHERE status <> 'Inactive'
    #     AND check_in_date >= CURRENT_DATE
    #     ) AS subquery
    #     WHERE stays.stay_id = subquery.stay_id
    #     """)

    # # Execute the UPDATE statement
    # result = session.execute(stmt)
    # result = session.execute(stmt2)
    # session.commit()

    # print("Batch update completed. {} rows affected.".format(result.rowcount))
    # print("Changes committed to the database.")

def send_error_to_slack(error_msg):
    url = os.getenv('SLACK_WEBHOOK')
    requests.post(url, json={"text": f"Error in threaded search awards! Error message: {error_msg}"})

if __name__ == "__main__":
    try:
        search_awards(search_frequency_hours=24, search_batch_size=12000)
        update_rates()
        session.close()
    except Exception as e:
        session.close()
        send_error_to_slack(str(e))
        logging.error("Error in main function: %s", str(e))  # Log exceptions