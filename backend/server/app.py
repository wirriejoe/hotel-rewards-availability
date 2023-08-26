from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, emit
from .search_stays import search_by_consecutive_nights, build_url
from sqlalchemy import create_engine, MetaData, select, join, and_, or_, desc, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
from pytz import utc
import os
import stytch
import stripe
import json

load_dotenv(find_dotenv())

app = Flask(__name__)
CORS(app, supports_credentials=True)
# csrf = CSRFProtect(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # enable CORS

stripe.api_key = os.getenv('STRIPE_API_KEY')

stytch = stytch.Client(
    project_id=os.getenv('STYTCH_PROJECT_ID'),
    secret=os.getenv('STYTCH_SECRET'),
    environment=os.getenv('STYTCH_ENV')
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
events = meta.tables['events']
requests = meta.tables['requests']

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

# Custom authentication error
class AuthenticationError(Exception):
    pass

def authenticate_session(session_token):
    # session_token = request.cookies.get('session_token')
    session_duration_minutes = 43200 # 1440 minutes = 1 day

    if not session_token:
        raise AuthenticationError('No session token provided.')

    try:
        # Authenticate the session first
        auth_resp = stytch.sessions.authenticate(session_token=session_token, session_duration_minutes=session_duration_minutes)
        user_id = auth_resp.user.user_id
        return user_id

    except Exception as e:
        raise AuthenticationError('Session authentication failed.')
    
def log_event(event_name, user_id, request = "", response = ""):
    # Insert a new row into the event_logs table
    ins = events.insert().values(event_name=event_name, stytchUserID=user_id, request=request, response = response)
    conn = engine.connect()
    conn.execute(ins)
    conn.commit()
    conn.close()

@app.route('/api/log_event', methods=['POST'])
def log_user_event():
    # This endpoint logs user events such as button clicks. The data to be logged is received as JSON in the POST request.

    data = request.json  # get data from POST request

    session_token = data.get('session_token')
    try:
        stytchUserID = authenticate_session(session_token)
    except AuthenticationError as e:
        return jsonify({'message': str(e)}), 401

    event_name = data['event_name']  # extract event name from the data
    event_details = data.get('event_details', '')  

    log_event(event_name, stytchUserID, event_details)  # log event

    return jsonify({'message': f'Event {event_name} logged successfully.'}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/consecutive_stays', methods=['POST'])
def consecutive_stays():
    data = request.json
    print(data)

    session_token = data.get('session_token', 'default_value')
    try:
        stytchUserID = authenticate_session(session_token)
    except AuthenticationError as e:
        return jsonify({'message': str(e)}), 401

    start_date = data['startDate']
    end_date = data['endDate']
    length_of_stay = int(data['lengthOfStay'])
    hotel_name_text = data.get('hotel', None)  # These are optional, so use .get() to return None if they are not present
    hotel_city = data.get('city', None)
    hotel_country = data.get('country', None)
    hotel_region = data.get('region', None)
    award_category = data.get('category', None)
    rate_filter = data.get('rateFilter', None)
    # print(data.get('pointsBudget'))
    max_points_budget = int(data.get('pointsBudget')) if data.get('pointsBudget') != '' else 0

    try:
        stays = search_by_consecutive_nights(start_date, end_date, length_of_stay, hotel_name_text, hotel_city, hotel_country, hotel_region, award_category, rate_filter, max_points_budget)
    except Exception as e:
        return jsonify({'message': str(e)}), 401

    # Apply time_since function to every last_checked object in the list
    stays = [{**stay, 'last_checked_string': time_since(stay['last_checked'])} for stay in stays]

    print(f"Search finished! Found {len(stays)} results!")
    log_event('search', stytchUserID, json.dumps(data), f"Returned {len(stays)} results.")
    return jsonify(stays)  # Convert list of stays to JSON

@app.route('/api/explore', methods=['POST'])
def explore():
    data = request.json
    print(data)
    print(request)

    session_token = data.get('session_token', 'default_value')
    try:
        stytchUserID = authenticate_session(session_token)
    except AuthenticationError as e:
        return jsonify({'message': str(e)}), 401

    isCustomer = data.get('isCustomer')
    today = datetime.now().astimezone(utc)
    if isCustomer:
        future_date = today + timedelta(days=360)
    else:    
        future_date = today + timedelta(days=61)

    filter_conditions = [
        stays.c.check_in_date >= today + timedelta(days=1),
        stays.c.check_in_date < future_date,
        stays.c.last_checked_time > datetime.now().astimezone(utc) - timedelta(hours=48),
        or_(stays.c.standard_rate > 0, stays.c.premium_rate > 0)
    ]

    j = join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)

    if data['award_category'] and data['award_category'] != [None]:
        filter_conditions.append(hotels.c.award_category.in_(data['award_category']))
    if data['brand'] != [''] and data['brand'] != [None]:
        filter_conditions.append(hotels.c.brand.in_(data['brand']))
    if data['country'] != '' and data['country'] != None:
        filter_conditions.append(hotels.c.hotel_country.in_([data['country']]))
    if data['points_budget'] != '' and data['points_budget'] != None:
        filter_conditions.append(
            or_(
                and_(stays.c.standard_rate <= float(data['points_budget']), stays.c.standard_rate > 0),
                and_(stays.c.premium_rate <= float(data['points_budget']), stays.c.premium_rate > 0)
        ))
    if data['is_weekend'] == 'true':
        print('test')
        filter_conditions.append(
            or_(
                func.extract('dow', stays.c.check_in_date) == 5,  # Friday
                func.extract('dow', stays.c.check_in_date) == 6   # Saturday
        ))
    if data['cents_per_point'] != '' and data['cents_per_point'] != None:
        print(data['cents_per_point'])
        filter_conditions.append(
            or_(
                text("stays.standard_cash_usd / NULLIF(stays.standard_rate::decimal, 0) >= :cpp").bindparams(cpp=data['cents_per_point']),
                text("stays.premium_cash_usd / NULLIF(stays.premium_rate::decimal, 0) >= :cpp").bindparams(cpp=data['cents_per_point'])
        ))
        
    query = select(
        stays.c.stay_id, 
        stays.c.check_in_date, 
        stays.c.last_checked_time, 
        hotels.c.hotel_name, 
        hotels.c.hotel_city, 
        hotels.c.hotel_province,
        hotels.c.hotel_country,
        hotels.c.hotel_region,
        hotels.c.brand,
        hotels.c.award_category,
        stays.c.standard_rate, 
        stays.c.premium_rate,
        stays.c.currency_code,
        stays.c.standard_cash,
        stays.c.premium_cash,
        stays.c.available_inventory,
        stays.c.standard_cash_usd,
        stays.c.premium_cash_usd,
        stays.c.booking_url).select_from(j).where(and_(*filter_conditions))

    with engine.connect() as connection:
        result = connection.execute(query)

    stay_results = [row._mapping for row in result]
    # Apply time_since function to every last_checked_time object in the list
    stay_results = [{**stay, 'last_checked': time_since(stay['last_checked_time'])} for stay in stay_results]

    connection.close()

    print(f"Explore finished! Found {len(stay_results)} results!")
    log_event('explore', stytchUserID, json.dumps(data), f"Returned {len(stay_results)} results.")
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
        s = select(hotels.c.brand).where(hotels.c.brand != '').distinct()
        result = connection.execute(s)
        return jsonify([row[0] for row in result])
    
def create_user(stytch_user_id, user_email, created_at):
    # create user using stytch_user_id
    ins = users.insert().values(stytchUserID=stytch_user_id, email=user_email, created_at=created_at)
    conn = engine.connect()
    conn.execute(ins)
    conn.commit()
    conn.close()
    log_event('create_user', stytch_user_id, user_email)

@app.route('/api/authenticate', methods=['GET'])
def authenticate_user():
    token = request.args.get('token')
    token_type = request.args.get('token_type')
    session_duration_minutes = 43200 # 1440 minutes = 1 day

    try:
        print(f"Session token type: {token_type}")
        if token_type == 'oauth':
            auth_resp = stytch.oauth.authenticate(token=token, session_duration_minutes=session_duration_minutes)
            log_event('oauth_authenticate', auth_resp.user_id, auth_resp.user.emails[0].email)
        elif token_type == 'magic_links':
            auth_resp = stytch.magic_links.authenticate(token=token, session_duration_minutes=session_duration_minutes)
            log_event('magic_link_authenticate', auth_resp.user_id, auth_resp.user.emails[0].email)
        # elif token_type == 'passwords':
        #     auth_resp = stytch.passwords.authenticate(token=token, session_duration_minutes=session_duration_minutes)
        #     log_event('password_authenticate', auth_resp.user_id, auth_resp.user.emails[0].email)
    except Exception as e:
        return jsonify({'message': 'Failed to authenticate user.', 'error': str(e)}), 401
    
    stytch_user_id = auth_resp.user_id
    user_email = auth_resp.user.emails[0].email
    created_at = auth_resp.user.created_at

    sel = users.select().where(users.c.stytchUserID == stytch_user_id)
    conn = engine.connect()
    result = conn.execute(sel)
    user = result.fetchone()
    # print(user)
    conn.close()

    if not user:
        print("creating user")
        create_user(stytch_user_id, user_email, created_at)

    # Save the session token and session jwt
    session_token = auth_resp.session_token
    session_jwt = auth_resp.session_jwt

    return jsonify({'message': 'User authenticated successfully.', 'session_token': session_token, 'session_jwt': session_jwt}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    try:
        session_token = request.json.get('session_token')
        session_id = request.json.get('session_id')
        print(session_token)
        print(session_id)
        response = {}

        # Delete the session using the Stytch API
        if session_token:
            response = stytch.sessions.revoke(session_token=session_token)
            log_event('log_out', "", f"session_token: {session_token}")
        elif session_id:
            response = stytch.sessions.revoke(session_id=session_id)
            log_event('log_out', "", f"session_id: {session_id}")

        print("User session deleted: " + str(response))

        return jsonify({'message': 'Logged out successfully.'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to log out.', 'error': str(e)}), 500

@app.route('/api/request', methods=['POST'])
def make_request():
    data = request.json
    now = datetime.now().astimezone(utc)
    print(data)

    session_token = data.get('session_token')
    try:
        stytchUserID = authenticate_session(session_token)
    except AuthenticationError as e:
        return jsonify({'message': str(e)}), 401
    
    sel = select(users.c.customer_status).where(users.c.stytchUserID == stytchUserID, users.c.customer_expiration_time >= now, users.c.customer_status == 'pro').limit(1)
    conn = engine.connect()
    user = conn.execute(sel).fetchone()
    print(type(user))
    print(user)
    if user:
        hotel_id = data.get('hotel_id')
        hotel_code = data.get('hotel_code')
        ins = requests.insert().values(hotel_id=hotel_id, hotel_code = hotel_code, request_user_id=stytchUserID)
        conn.execute(ins)
        conn.commit()
        conn.close()
        return jsonify({'message': f'Request made successfully for {hotel_code}. Stays will start tracking within the next 24 hours.'}), 200
    else:
        conn.close()
        return jsonify({'message': f'Failed to make request for {hotel_code}. Please try again or contact Willie in Discord.'}), 500

@app.route('/api/requests', methods=['GET'])
def get_requests():
    session_token = request.args.get('session_token')
    try:
        stytchUserID = authenticate_session(session_token)
    except AuthenticationError as e:
        return jsonify({'message': str(e)}), 401

    # Retrieve all requests from the requests table
    sel = select(requests.c.hotel_code).distinct().where(requests.c.request_user_id == stytchUserID)
    conn = engine.connect()
    result = conn.execute(sel)
    conn.close()
    request_results = [dict(row._mapping) for row in result]
    return jsonify(request_results)

@app.route('/api/stays', methods=['GET'])
def get_stays():
    session_token = request.args.get('session_token')
    try:
        stytchUserID = authenticate_session(session_token)
    except AuthenticationError as e:
        return jsonify({'message': str(e)}), 401
    
    j = join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)

    # Retrieve all stays from the stays table
    sel = select(
        hotels.c.hotel_name,
        hotels.c.hotel_id,
        hotels.c.hotel_code,
        func.count(stays.c.check_in_date).label('num_night_monitored')).select_from(j).where(
            stays.c.status.in_(['Active', 'Queued']),
            stays.c.check_in_date >= datetime.now() + timedelta(days=1)
        ).group_by(hotels.c.hotel_name, hotels.c.hotel_id, hotels.c.hotel_code).order_by(desc('num_night_monitored'),hotels.c.hotel_name)

    conn = engine.connect()
    result = conn.execute(sel)
    conn.close()
    stay_results = [dict(row._mapping) for row in result]
    
    log_event('get_stays', stytchUserID, "Requested all stays.", f"Returned {len(stay_results)} results.")
    return jsonify(stay_results)

# @csrf.exempt
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.data
    event = None
    ins = ""

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload, return 400 status (bad request)
        return jsonify({'error': 'Invalid payload'}), 400

    # Handle the event
    if event.type == 'invoice.paid':
        if event.data.object.status == 'paid':
            invoice_paid = event.data.object
            ins = users.update().values(
                stripe_user_id = invoice_paid.customer,
                customer_status = 'pro',
                customer_expiration_time = datetime.fromtimestamp(invoice_paid.lines.data[0].period.end)
            ).where(
                users.c.email == invoice_paid.customer_email
            )
            event_type = 'customer_paid'
            event_user = invoice_paid.customer
            event_msg = f'Invoice Paid! Customer {invoice_paid.customer_email} with Stripe customer ID {invoice_paid.customer} paid {invoice_paid.amount_paid/100} {invoice_paid.currency} to subscribe until {datetime.fromtimestamp(invoice_paid.lines.data[0].period.end)}'
            print(event_msg)
    elif event.type == 'customer.subscription.updated':
        print(f'Subscription updated: {event.data.object.status}')
        if event.data.object.status == 'canceled' or event.data.object.status == 'unpaid' or event.data.object.cancel_at_period_end:
            ins = users.update().values(
                customer_status = 'churned'
            ).where(
                users.c.stripe_user_id == event.data.object.customer
            )
            event_type = 'customer_churned'
            event_user = event.data.object.customer
            event_msg = f'Customer just churned! Stripe customer ID {event.data.object.customer}'
            print(event_msg)
    elif event.type == 'charge.refunded':
        charge_refunded = event.data.object
        print(f'Refund status: {charge_refunded.refunded}')
        if charge_refunded.refunded:
            ins = users.update().values(
                customer_status = 'churned',
                customer_expiration_time = datetime.now()
            ).where(
                users.c.stripe_user_id == charge_refunded.customer
            )
            event_type = 'customer_refunded'
            event_user = charge_refunded.customer
            event_msg = f'Stripe customer ID {charge_refunded.customer} just got a refund for {charge_refunded.amount_refunded/100} {charge_refunded.currency}! Remove their access immediately!'
            print(event_msg)
    else:
        print('Unhandled event type {}'.format(event.type))
    
    if ins != "":
        conn = engine.connect()
        conn.execute(ins)
        conn.commit()
        conn.close()
        log_event(event_type, event_user, "", event_msg)

    return jsonify({'message': 'Success'}), 200

@socketio.on('connect')
def test_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('get_status')
def handle_get_status(message):
    now = datetime.now().astimezone(utc)
    try:
        session_token = message.get('session_token')
        user_id = authenticate_session(session_token)
    except Exception as e:
        return jsonify({'message': str(e)}), 401
    sel = select(users.c.customer_status).where(users.c.stytchUserID == user_id, users.c.customer_expiration_time >= now).limit(1)
    conn = engine.connect()
    user = conn.execute(sel)
    conn.close()
    customer_status = [row[0] for row in user]
    try:
        if customer_status[0] == 'pro':
            emit('customer_status', {'customer_status': True})
        else:
            emit('customer_status', {'customer_status': False})
    except Exception as e:
        emit('customer_status', {'customer_status': False})
        return jsonify({'message': str(e)}), 401

if __name__ == '__main__':
    app.run(port=3001) #locally, i've been using port 3000, but render default is 10000
    socketio.run(app)