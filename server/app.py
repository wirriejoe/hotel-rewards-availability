from flask import Flask, request, jsonify, render_template
from search_stays import search_by_consecutive_nights
from sqlalchemy import create_engine, MetaData, select, and_, join, func, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
from pytz import utc
import os
import logging

load_dotenv(find_dotenv())

app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Initialize connection and Session
database_url = os.getenv('POSTGRES_DB_URL')
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
meta.reflect(bind=engine)

stays = meta.tables['stays']
hotels = meta.tables['hotels']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/api/consecutive_stays', methods=['POST'])
def consecutive_stays():
    data = request.json

    start_date = data['startDate']
    end_date = data['endDate']
    length_of_stay = int(data['lengthOfStay'])
    hotel_name_text = data.get('hotel', None)  # These are optional, so use .get() to return None if they are not present
    hotel_city = data.get('city', None)
    hotel_country = data.get('country', None)
    rate_filter = data.get('rateFilter', None)
    app.logger.info(data.get('pointsBudget'))
    max_points_budget = int(data.get('pointsBudget')) if data.get('pointsBudget') != '' else 0

    stays = search_by_consecutive_nights(start_date, end_date, length_of_stay, hotel_name_text, hotel_city, hotel_country, rate_filter, max_points_budget)

    # Apply time_since function to every last_checked object in the list
    stays = [{**stay, 'last_checked': time_since(stay['last_checked'])} for stay in stays]

    return jsonify(stays)  # Convert list of stays to JSON

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json

    j = join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)

    query = select(stays.c.check_in_date, stays.c.last_checked_time, hotels.c.hotel_name, hotels.c.hotel_city, hotels.c.hotel_country, stays.c.standard_rate, stays.c.premium_rate, stays.c.booking_url).select_from(j).where(
        or_(stays.c.check_in_date >= data['startDate'], data['startDate'] == None),
        or_(stays.c.check_in_date < data['endDate'], data['endDate'] == None),
        hotels.c.hotel_name.ilike(f"%{data['hotel']}%"),
        or_(hotels.c.hotel_city.ilike(f"%{data['city']}%"), data['city'] == None),
        or_(stays.c.standard_rate > 0, stays.c.premium_rate > 0)
    )

    with engine.connect() as connection:
        result = connection.execute(query)

    stay_results = [row._mapping for row in result]
    # Apply time_since function to every last_checked_time object in the list
    stay_results = [{**stay, 'last_checked': time_since(stay['last_checked_time'])} for stay in stay_results]

    connection.close()
    # print(stay_results)
    return jsonify(stay_results)

def time_since(last_checked_time):
    now = datetime.now().astimezone(utc)
    last_checked_time = last_checked_time.astimezone(utc)
    difference = now - last_checked_time

    if difference < timedelta(hours=1):
        return "Just now"
    elif difference < timedelta(days=1):
        hours = difference // timedelta(hours=1)
        return f"{hours} hours ago"
    else:
        days = difference // timedelta(days=1)
        return f"{days} days ago"

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=3000)