from sqlalchemy import create_engine, MetaData, update
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv(find_dotenv())

# Initialize connection and Session
database_url = os.getenv('POSTGRES_DB_URL')
print(database_url)
print(os.getcwd())

engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
meta.reflect(bind=engine)

# Map tables
stays = meta.tables['stays']

def clear_queued_stays():
    logging.info("Starting to update 'Queued' stays to 'Active'...")

    # Update statement to set status='Active' where status='Queued'
    update_query = update(stays).where(stays.c.status == 'Queued').values(status='Active')

    # Execute the update query
    result = session.execute(update_query)

    logging.info(f"Update completed. {result.rowcount} rows affected.")

    # Commit the changes
    session.commit()
    session.close()
    logging.info("Changes committed to the database.")


if __name__ == "__main__":
    clear_queued_stays()