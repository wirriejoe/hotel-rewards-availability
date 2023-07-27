from sqlalchemy import create_engine, MetaData, select, and_, update, func, case, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from award_search import AwardSearch
import os
import pytz
import time
import random
import logging

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

def upsert(session, table, list_of_dicts, unique_columns):
    for data_dict in list_of_dicts:
        stmt = insert(table).values(**data_dict)
        upd_stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=data_dict
        )
        session.execute(upd_stmt)
    session.commit()

def update_awards_table(award_stays, stay_record):
    # Replaced 'stay' with 'stay_record' to avoid naming conflict with stay from the outer function
    stay_fields = stay_record
    stay_id = stay_fields['stay_id']
    hotel_id = stay_fields['hotel_id']
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
    return award_updates

def search_awards(search_frequency_hours = 24, search_batch_size = 1000):
    awardsearch = AwardSearch()
    award_updates = []
    stay_updates = []
    search_counter = 0
    start_timer = datetime.now()
    
    stay_records = session.execute(
        select(*stays.c).where(
            and_(
                stays.c.status == "Active", 
                stays.c.last_checked_time < datetime.now(pytz.UTC) - timedelta(hours=search_frequency_hours),
                stays.c.check_in_date >= datetime.now(pytz.UTC).date()
            )
        ).limit(search_batch_size)
    ).fetchall()

    # Update status of fetched stay_records to 'Queued'
    stay_ids_to_update = [record.stay_id for record in stay_records]
    update_query = stays.update().where(stays.c.stay_id.in_(stay_ids_to_update)).values(status='Queued')
    session.execute(update_query)
    session.commit()

    for stay in stay_records:
        time.sleep(random.randint(0, 1))
        search_counter += 1
        print(f"Searching #{search_counter} stay! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        stay = stay._asdict()
        hotel_code = stay['hotel_code']
        check_in_date = stay['check_in_date']
        check_out_date = stay['check_out_date']

        award_stays = awardsearch.get_award_stays(hotel_brand='Hyatt', 
                                             hotel_code=hotel_code, 
                                             checkin_date=check_in_date, 
                                             checkout_date=check_out_date)
        
        if award_stays:
            award_updates.extend(update_awards_table(award_stays, stay))

        stay_updates.append({
            'stay_id': stay['stay_id'],
            'last_checked_time': datetime.now(pytz.UTC),
            'status': 'Active'
        })
    upsert(session, awards, award_updates, ['award_id'])
    upsert(session, stays, stay_updates, ['stay_id'])
    awardsearch.quit()

def update_rates():
    logging.log("Starting batch update of rates...")

    # Define "24 hours ago"
    one_day_ago = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')

    # Prepare the raw SQL statement
    stmt = text("""
        UPDATE stays
        SET 
            standard_rate = subquery.min_standard_rate,
            premium_rate = subquery.min_premium_rate
        FROM (
            SELECT 
                stay_id,
                MIN(CASE WHEN room_category = 'STANDARD' AND last_checked_time <= :one_day_ago THEN lowest_points_rate ELSE 0 END) AS min_standard_rate,
                MIN(CASE WHEN room_category = 'PREMIUM' AND last_checked_time <= :one_day_ago THEN lowest_points_rate ELSE 0 END) AS min_premium_rate
            FROM awards
            GROUP BY stay_id
        ) AS subquery
        WHERE stays.stay_id = subquery.stay_id
    """)

    # Execute the UPDATE statement
    result = session.execute(stmt, {'one_day_ago': one_day_ago})
    session.commit()

    logging.log("Batch update completed. {} rows affected.".format(result.rowcount))
    logging.log("Changes committed to the database.")

if __name__ == "__main__":
    try:
        search_awards(search_frequency_hours=24, search_batch_size=1500)
        update_rates()
    except Exception as e:
        logging.error("Error in main function: %s", str(e))  # Log exceptions