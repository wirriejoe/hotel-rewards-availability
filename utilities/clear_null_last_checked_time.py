from sqlalchemy import create_engine, MetaData, update, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv(os.path.realpath(os.path.join(os.path.dirname(__file__), '../.env')))

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
awards = meta.tables['awards']

def clear_null_last_checked_time():
    logging.info("Starting to update 'last_checked_time' with null values to 1900-01-01 00:00:00+00...")

    # Update statement to set last_checked_time='1900-01-01 00:00:00+00' where last_checked_time is NULL
    update_query = update(awards).where(awards.c.last_checked_time == None).values(last_checked_time=text("'1900-01-01 00:00:00+00'"))

    # Execute the update query
    result = session.execute(update_query)

    logging.info(f"Update completed. {result.rowcount} rows affected.")

    # Commit the changes
    session.commit()
    session.close()
    logging.info("Changes committed to the database.")

if __name__ == "__main__":
    clear_null_last_checked_time()