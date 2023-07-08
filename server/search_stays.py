from sqlalchemy import create_engine, MetaData, select, and_, join
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from dotenv import load_dotenv
from operator import itemgetter
from itertools import groupby
from datetime import timedelta
import os

# Load environment variables
load_dotenv(os.path.realpath(os.path.join(os.path.dirname(__file__), '../.env')))

# Initialize connection and Session
database_url = os.getenv('POSTGRES_DB_URL')
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

meta = MetaData()
meta.reflect(bind=engine)

# Map tables
stays = meta.tables['stays']
hotels = meta.tables['hotels']

def fetch_stays(start_date, end_date, hotel_name_text = None, hotel_city=None, hotel_country=None, rate_filter=None):
    filter_conditions = [
        stays.c.check_in_date >= start_date,
        stays.c.check_out_date <= end_date
    ]
    
    if hotel_name_text:
        filter_conditions.append(hotels.c.hotel_name.contains(hotel_name_text))
    if hotel_city:
        filter_conditions.append(hotels.c.hotel_city.contains(hotel_city))
    if hotel_country:
        filter_conditions.append(hotels.c.hotel_country.contains(hotel_country))
    if rate_filter == 'Standard':
        filter_conditions.append(stays.c.standard_rate > 0)
    elif rate_filter == 'Premium':
        filter_conditions.append(stays.c.premium_rate > 0)

    j = join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)

    stay_records = session.execute(
        select(*stays.c, *hotels.c).select_from(j).where(
            and_(*filter_conditions)
        ).group_by(*stays.c, *hotels.c)
        .order_by(hotels.c.hotel_name, stays.c.check_in_date)
    ).fetchall()

    session.close()

    return [record._mapping for record in stay_records]

def get_consecutive_stays(hotel_data, num_consecutive_days, rate_filter=None, max_points_budget=0):
    # Sort data by hotel code and check in date
    hotel_data.sort(key=lambda x: (x['hotel_code'], x['check_in_date']))

    # Group data by hotel code
    grouped_data = groupby(hotel_data, key=itemgetter('hotel_code'))

    result = []

    # Iterate over each group
    for hotel_code, group in grouped_data:
        stays = list(group)

        for i in range(len(stays) - num_consecutive_days + 1):
            # Check if the dates are consecutive
            if all((stays[i + j + 1]['check_in_date'] - stays[i + j]['check_in_date'] == timedelta(days=1) for j in range(num_consecutive_days - 1))):
                
                standard_rate = 0
                premium_rate = 0

                if all(stay['premium_rate'] > 0 for stay in stays[i:i + num_consecutive_days]):
                    premium_rate = sum(stay['premium_rate'] for stay in stays[i:i + num_consecutive_days]) / num_consecutive_days
                if all(stay['standard_rate'] > 0 for stay in stays[i:i + num_consecutive_days]):
                    standard_rate = sum(stay['standard_rate'] for stay in stays[i:i + num_consecutive_days]) / num_consecutive_days
                
                if standard_rate == 0 and premium_rate == 0:
                    continue
                
                response_url, booking_url = build_url('Hyatt', hotel_code, stays[i]['check_in_date'].strftime('%Y-%m-%d'), (stays[i]['check_in_date'] + timedelta(days=num_consecutive_days)).strftime('%Y-%m-%d'), room_qty = 1, adults = 2, kids = 0)

                result_stay = {
                    'hotel_name': stays[i]['hotel_name'],
                    'date_range_start': stays[i]['check_in_date'],
                    'date_range_end': stays[i]['check_in_date'] + timedelta(days=num_consecutive_days),
                    'last_checked': stays[i]["last_checked_time"],
                    'standard_rate': standard_rate,
                    'premium_rate': premium_rate,
                    'hotel_city': stays[i]["hotel_city"],
                    'hotel_country': stays[i]["hotel_country"],
                    'booking_url': booking_url
                }

                if rate_filter == 'Standard':
                    if max_points_budget == 0 or standard_rate <= max_points_budget:
                        result.append(result_stay)
                elif rate_filter == 'Premium':
                    if max_points_budget == 0 or premium_rate <= max_points_budget:
                        result.append(result_stay)
                else:
                    if max_points_budget == 0 or standard_rate <= max_points_budget or premium_rate <= max_points_budget:
                        result.append(result_stay)
                
    return result

def build_url(hotel_brand, hotel_code, checkin_date, checkout_date, room_qty = 1, adults = 2, kids = 0):
    base_url_dict = {
        'Hyatt': 'https://www.hyatt.com/shop/service/rooms/roomrates/'
    }
    search_base_url_dict = {
        'Hyatt': 'https://www.hyatt.com/shop/rooms/'
    }
    base_url = base_url_dict[hotel_brand] + hotel_code
    search_base_url = search_base_url_dict[hotel_brand] + hotel_code
    response_url = base_url + f'?spiritCode={hotel_code}&rooms={room_qty}&adults={adults}&checkinDate={checkin_date}&checkoutDate={checkout_date}&kids={kids}'
    search_url = search_base_url + f'?checkinDate={checkin_date}&checkoutDate={checkout_date}&rateFilter=woh'
    print("Response URL: " + response_url)
    print("Verification URL: " + search_url)
    return response_url, search_url


def search_by_consecutive_nights(start_date, end_date, length_of_stay, hotel_name_text=None, hotel_city=None, hotel_country=None, rate_filter=None, max_points_budget=0):
    records = fetch_stays(start_date=start_date, end_date=end_date, hotel_name_text=hotel_name_text, hotel_city=hotel_city, hotel_country=hotel_country, rate_filter=rate_filter)
    print(len(records))

    consecutive_stays = get_consecutive_stays(records, length_of_stay, rate_filter, max_points_budget)

    return consecutive_stays

# print(search_by_consecutive_nights(datetime(2023, 8, 1), datetime(2023,8,31), 16))