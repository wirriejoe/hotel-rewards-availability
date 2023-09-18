from sqlalchemy import create_engine, MetaData, select, and_, update, func, case, text, join
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from award_search import AwardSearch
from threading import Thread, Lock
from queue import Queue
import os
import pytz
import logging
from search_helpers import upsert, update_rates, send_error_to_slack

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
if __name__ == "__main__":
    try:
        search_awards(search_frequency_hours=24, search_batch_size=12000)
        print("Finished joining threads! Upserting data.")
        print(f"Num award updates: {len(award_updates)}")
        print(f"Num stay updates: {len(stay_updates)}")
        upsert(session, temp_awards, award_updates, ['award_id'])
        upsert(session, stays, stay_updates, ['stay_id'])
        update_rates()
        session.close()
    except Exception as e:
        session.close()
        send_error_to_slack(str(e))
        logging.error("Error in main function: %s", str(e))  # Log exceptions