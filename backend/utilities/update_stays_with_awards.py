from sqlalchemy import create_engine, MetaData, select, update, func
from sqlalchemy.sql import label
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
hotels = meta.tables['hotels']
awards = meta.tables['awards']  # Add this line to map 'awards' table

def update_stays_with_awards(stays_column_name, awards_column_name, aggregation_func):
    logging.info(f"Starting batch update of {stays_column_name} from {awards_column_name} ...")

    # Subquery to aggregate the column in the awards table
    subquery = select(
        awards.c.stay_id,
        label(stays_column_name, aggregation_func(awards.c[awards_column_name]))
    ).group_by(awards.c.stay_id).alias('awards_subquery')

    # Batch update stays with the aggregated value
    update_query = update(stays).values(
        {stays_column_name: subquery.c[stays_column_name]}
    ).where(stays.c.stay_id == subquery.c.stay_id)

    # Execute the update query
    result = session.execute(update_query)

    logging.info(f"Batch update completed. {result.rowcount} rows affected.")

    # Commit the changes
    session.commit()
    session.close()
    logging.info("Changes committed to the database.")


if __name__ == "__main__":
    # Update 'stays_column_name' column in stays table using the 'awards_column_name' from awards table, aggregated by the 'aggregation_func' function
    update_stays_with_awards('booking_url', 'search_url', func.min)