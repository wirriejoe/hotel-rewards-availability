from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from .search_stays import search_by_consecutive_nights, build_url
from sqlalchemy import create_engine, MetaData, select, join, and_, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
from pytz import utc
import os
import logging

load_dotenv(find_dotenv())

app = Flask(__name__)
CORS(app)

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

@app.route('/explore')
def explore_page():
    return render_template('explore.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/api/consecutive_stays', methods=['POST'])
def consecutive_stays():
    data = request.json

    print(data)

    start_date = data['startDate']
    end_date = data['endDate']
    length_of_stay = int(data['lengthOfStay'])
    hotel_name_text = data.get('hotel', None)  # These are optional, so use .get() to return None if they are not present
    hotel_city = data.get('city', None)
    hotel_country = data.get('country', None)
    hotel_region = data.get('region', None)
    award_category = data.get('category', None)
    rate_filter = data.get('rateFilter', None)
    app.logger.info(data.get('pointsBudget'))
    max_points_budget = int(data.get('pointsBudget')) if data.get('pointsBudget') != '' else 0

    stays = search_by_consecutive_nights(start_date, end_date, length_of_stay, hotel_name_text, hotel_city, hotel_country, hotel_region, award_category, rate_filter, max_points_budget)

    # Apply time_since function to every last_checked object in the list
    stays = [{**stay, 'last_checked': time_since(stay['last_checked'])} for stay in stays]

    return jsonify(stays)  # Convert list of stays to JSON

from datetime import datetime, timedelta

@app.route('/api/explore', methods=['POST'])
def explore():
    data = request.json
    today = datetime.now()
    future_date = today + timedelta(days=60)

    filter_conditions = [
        stays.c.check_in_date >= today + timedelta(days=1),
        stays.c.check_in_date < future_date,
        or_(stays.c.standard_rate > 0, stays.c.premium_rate > 0)
    ]

    j = join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)

    filter_conditions.append(hotels.c.award_category.in_(data['award_category']))
    if data['brand'] != [None] and data['brand'] != "":
        filter_conditions.append(hotels.c.brand.in_(data['brand']))
        
    query = select(
        stays.c.stay_id, 
        stays.c.check_in_date, 
        stays.c.last_checked_time, 
        hotels.c.hotel_name, 
        hotels.c.hotel_city, 
        hotels.c.hotel_country, 
        hotels.c.hotel_region,
        hotels.c.brand,
        hotels.c.award_category,
        stays.c.standard_rate, 
        stays.c.premium_rate, 
        stays.c.booking_url).select_from(j).where(and_(*filter_conditions))

    with engine.connect() as connection:
        result = connection.execute(query)

    stay_results = [row._mapping for row in result]
    # Apply time_since function to every last_checked_time object in the list
    stay_results = [{**stay, 'last_checked': time_since(stay['last_checked_time'])} for stay in stay_results]

    print(stay_results)
    connection.close()
    return jsonify(stay_results)

@app.route('/api/hotels', methods=['GET'])
def get_hotels():
    with engine.connect() as connection:
        s = select(hotels.c.hotel_name).where(hotels.c.award_category != '').distinct()
        result = connection.execute(s)
        return jsonify([row[0] for row in result])
    
@app.route('/api/cities', methods=['GET'])
def get_cities():
    with engine.connect() as connection:
        s = select(hotels.c.hotel_city).where(hotels.c.award_category != '').distinct()
        result = connection.execute(s)
        return jsonify([row[0] for row in result])

@app.route('/api/countries', methods=['GET'])
def get_countries():
    with engine.connect() as connection:
        s = select(hotels.c.hotel_country).where(hotels.c.award_category != '').distinct()
        result = connection.execute(s)
        return jsonify([row[0] for row in result])
    
@app.route('/api/regions', methods=['GET'])
def get_regions():
    with engine.connect() as connection:
        s = select(hotels.c.hotel_region).where(hotels.c.award_category != '').distinct()
        result = connection.execute(s)
        return jsonify([row[0] for row in result])

@app.route('/api/award_categories', methods=['GET'])
def get_categories():
    with engine.connect() as connection:
        s = select(hotels.c.award_category).where(hotels.c.award_category != '').distinct()
        result = connection.execute(s)
        return jsonify([row[0] for row in result])
    
@app.route('/api/brands', methods=['GET'])
def get_brands():
    with engine.connect() as connection:
        s = select(hotels.c.brand).where(hotels.c.award_category != '').distinct()
        result = connection.execute(s)
        return jsonify([row[0] for row in result])

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
    app.run(port=3000) #locally, i've been using port 3000, but render default is 10000