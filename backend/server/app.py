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
import stytch

load_dotenv(find_dotenv())

app = Flask(__name__)
CORS(app)

stytch = stytch.Client(
    project_id=os.getenv('STYTCH_PROJECT_ID'),
    secret=os.getenv('STYTCH_SECRET'),
    environment='test',
)

# Initialize connection and Session
database_url = os.getenv('POSTGRES_DB_URL')
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
meta.reflect(bind=engine)

users = meta.tables['users']
stays = meta.tables['stays']
hotels = meta.tables['hotels']

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

@app.route('/')
def index():
    return render_template('index.html')

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
    
def create_user(stytch_user_id, user_email, created_at):
    # create user using stytch_user_id
    ins = users.insert().values(stytchUserID=stytch_user_id, email=user_email, created_at=created_at)
    conn = engine.connect()
    conn.execute(ins)
    conn.commit()
    conn.close()

@app.route('/api/authenticate', methods=['GET'])
def authenticate_user():
    token = request.args.get('token')
    token_type = request.args.get('token_type')
    try:
        if token_type == 'oauth':
            auth_resp = stytch.oauth.authenticate(token)
        elif token_type == 'magic_links':
            auth_resp = stytch.magic_links.authenticate(token)
    except Exception as e:
        return jsonify({'message': 'Failed to authenticate user.', 'error': str(e)}), 401
    
    stytch_user_id = auth_resp.user_id
    user_email = auth_resp.user.emails[0].email
    created_at = auth_resp.user.created_at

    sel = users.select().where(users.c.stytchUserID == stytch_user_id)
    conn = engine.connect()
    result = conn.execute(sel)
    user = result.fetchone()
    print(user)
    conn.close()

    if not user:
        print("creating user")
        create_user(stytch_user_id, user_email, created_at)

    # Session management, which can be done via Stytch or manually
    # stytch.sessions.create(user_id=user.id)

    return jsonify({'message': 'User authenticated successfully.'}), 200

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=3000) #locally, i've been using port 3000, but render default is 10000