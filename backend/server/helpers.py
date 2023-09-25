from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, MetaData, select, and_, update, func, case, text, join, desc
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta
from retry import retry
import pytz
import random
import os
import requests

load_dotenv(find_dotenv())

database_url = os.getenv('POSTGRES_DB_URL')
print("Database URL: %s", database_url)  # Use lazy logging format
engine = create_engine(database_url) # add , echo=True for logging
Session = scoped_session(sessionmaker(bind=engine))

meta = MetaData()
meta.reflect(bind=engine)

stays = meta.tables['stays']
awards = meta.tables['awards']
hotels = meta.tables['hotels']
temp_awards = meta.tables['temp_awards']

username = os.getenv('BRIGHTDATA_USERNAME')
password = os.getenv('BRIHTDATA_PASSWORD')
port = 22225
session_id = random.random()
super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"

proxy_dict = {
    "http": super_proxy_url
}

award_updates = []
stay_updates = []
search_counter = 0

def queue_stays(hotel_brand, search_frequency_hours, search_batch_size):
    session = Session()
    stay_records = session.execute(
        select(*stays.c, *hotels.c)
        .select_from(join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id))
        .where(and_(stays.c.status == "Active", 
            case([(stays.c.priority == True, stays.c.last_checked_time < datetime.now(pytz.UTC) - timedelta(hours=8)),],
                else_=stays.c.last_checked_time < datetime.now(pytz.UTC) - timedelta(hours=search_frequency_hours)),
            stays.c.check_in_date >= datetime.now(pytz.UTC).date(),
            hotels.c.hotel_brand == hotel_brand))
        .order_by(desc(stays.c.priority), stays.c.last_checked_time)
        .limit(search_batch_size)).fetchall()

    # Update status of fetched stay_records to 'Queued'
    stay_ids_to_update = [stay.stay_id for stay in stay_records]
    update_query = stays.update().where(stays.c.stay_id.in_(stay_ids_to_update)).values(status='Queued', last_queued_time=datetime.now(pytz.UTC))
    session.execute(update_query)
    session.commit()
    
    return stay_records

def upsert_chunk(table_name, list_of_dicts, unique_columns):
    session = Session()  # Create a new scoped session
    try:
        # print("Entering upsert_chunk...")
        keys = list_of_dicts[0].keys()
        columns = ', '.join(keys)
        values = ', '.join([f":{key}" for key in keys])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        update_str = ', '.join([f"{col}=EXCLUDED.{col}" for col in keys])
        conflict_str = ', '.join(unique_columns)
        upsert_sql = f"{insert_sql} ON CONFLICT ({conflict_str}) DO UPDATE SET {update_str}"
        
        session.execute(text(upsert_sql), list_of_dicts)
        # print("Executed UPSERT SQL, committing...")        
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()  # Rollback the session in case of an exception
    finally:
        session.close()

def upsert(table_name, list_of_dicts, unique_columns):
    print("Starting upsert...")
    chunk_size = 5  # Choose an appropriate size
    total = len(list_of_dicts)
    chunks = [list_of_dicts[i:i + chunk_size] for i in range(0, total, chunk_size)]
    print(f"Divided data into {len(chunks)} chunks of size {chunk_size}.")
    
    with ThreadPoolExecutor() as executor:
        # print("Starting ThreadPoolExecutor...")
        
        futures = {executor.submit(upsert_chunk, table_name, chunk, unique_columns): chunk for chunk in chunks}
        for future in as_completed(futures):
            # print(f"Completed a future with result: {future.result()}")
            # Handle future.result() or exceptions here
            pass

    # print(f"Table name: {table_name}")
    # print(table_name.name==temp_awards.name)

    # if table_name.name == temp_awards.name:
    #     print("Calling tempAwards webhook!")
    #     url = "https://api.retool.com/v1/workflows/412574f5-d537-442e-b2cb-4becd78c4cdb/startTrigger"
    #     params = {'workflowApiKey': 'retool_wk_4c776ddd5e9a4168839e4af2afeacc6c'}
    #     response = requests.get(url, params=params)
    #     if response.status_code == 200:
    #         print("Request successful:", response.json())
    #     else:
    #         print("Request failed:", response.status_code)
    #         send_error_to_slack("tempAwards webhook error: " + response)

def update_rates():
    print("Calling update_rates() webhook!")
    # url = "https://api.retool.com/v1/workflows/c5027803-ab81-4c30-85cd-57748fe8f44f/startTrigger"
    # params = {'workflowApiKey': 'retool_wk_a717023c42f24f558e28f0afe3dc2abb'}
    # response = requests.get(url, params=params)
    # if response.status_code == 200:
    #     print("Request successful:", response.json())
    # else:
    #     print("Request failed:", response.status_code)
    #     send_error_to_slack("update_rates() webhook error: " + response)

def send_error_to_slack(error_msg):
    url = os.getenv('SLACK_WEBHOOK')
    requests.post(url, json={"text": f"Error in award search worker! Error message: {error_msg}"})