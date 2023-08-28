from sqlalchemy import create_engine, MetaData, select, and_, join, text
from sqlalchemy.orm import sessionmaker
from datetime import timedelta, datetime
from pytz import utc
from dotenv import load_dotenv, find_dotenv
from operator import itemgetter
from itertools import groupby
import os

# Load environment variables
load_dotenv(find_dotenv())

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

def fetch_stays(start_date, end_date, hotels_name_text = [], hotel_cities=[], hotel_countries=[], hotel_regions=[], award_categories=[], rate_filter=None):

    filter_conditions = [
        stays.c.check_in_date >= start_date,
        stays.c.check_out_date <= end_date,
        stays.c.duration == 1,
        stays.c.last_checked_time > datetime.now().astimezone(utc) - timedelta(hours=48)
    ]
    
    if [name for name in hotels_name_text if name]:
        filter_conditions.append(hotels.c.hotel_name.in_(hotels_name_text))
    if [name for name in hotel_cities if name]:
        filter_conditions.append(hotels.c.hotel_city.in_(hotel_cities))
    if [name for name in hotel_countries if name]:
        filter_conditions.append(hotels.c.hotel_country.in_(hotel_countries))
    if [name for name in hotel_regions if name]:
        filter_conditions.append(hotels.c.hotel_region.in_(hotel_regions))
    if [name for name in award_categories if name]:
        filter_conditions.append(hotels.c.award_category.in_(award_categories))
    if rate_filter == 'Standard':
        filter_conditions.append(stays.c.standard_rate > 0)
    if rate_filter == 'Premium':
        filter_conditions.append(stays.c.premium_rate > 0)

    j = join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)

    stay_records = session.execute(
        select(*stays.c, *hotels.c).select_from(j).where(
            and_(*filter_conditions)
        ).group_by(*stays.c, *hotels.c)
        .order_by(hotels.c.hotel_name, stays.c.check_in_date)
    ).fetchall()

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
            result_stay = {}
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
                    'hotel_code': stays[i]['hotel_code'],
                    'date_range_start': stays[i]['check_in_date'],
                    'date_range_end': stays[i]['check_in_date'] + timedelta(days=num_consecutive_days),
                    'last_checked': stays[i]["last_checked_time"],
                    'standard_rate': standard_rate,
                    'premium_rate': premium_rate,
                    'hotel_city': stays[i]["hotel_city"],
                    'hotel_province': stays[i]["hotel_province"],
                    'hotel_country': stays[i]["hotel_country"],
                    'hotel_region': stays[i]["hotel_region"],
                    'award_category': stays[i]["award_category"],
                    'booking_url': booking_url
                }

                if rate_filter == 'Standard':
                    if max_points_budget == 0 or (standard_rate <= max_points_budget and standard_rate != 0):
                        result.append(result_stay)
                elif rate_filter == 'Premium':
                    if max_points_budget == 0 or (premium_rate <= max_points_budget and premium_rate != 0):
                        result.append(result_stay)
                else:
                    if max_points_budget == 0 or (standard_rate <= max_points_budget and standard_rate != 0) or (premium_rate <= max_points_budget and premium_rate != 0):
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
    return response_url, search_url

def search_by_consecutive_nights(start_date, end_date, length_of_stay, hotel_name_text=[], hotel_city=[], hotel_country=[], hotel_region=[], award_category=[], rate_filter=None, max_points_budget=0):
    try:
        records = fetch_stays(start_date=start_date, end_date=end_date, hotels_name_text=hotel_name_text, hotel_cities=hotel_city, hotel_countries=hotel_country, hotel_regions=hotel_region, award_categories=award_category, rate_filter=rate_filter)
        # print(len(records))
        consecutive_stays = get_consecutive_stays(records, length_of_stay, rate_filter, max_points_budget)
        session.close()
        return consecutive_stays
    except Exception as e:
        session.close()
        return "Error in search_stays.py: %s", str(e)
    

def get_consecutive_stays_2(start_date, end_date, hotel_cities, hotel_countries, award_categories, length_of_stay, rate_filter, max_points_budget):
    query = text(
        """
        with ConsecutiveNights as (
            SELECT 
                stays.hotel_id,
                check_in_date,
                check_out_date,
                check_out_date - check_in_date AS duration,
                standard_rate,
                premium_rate,
                case when :rate_filter = 'Standard' then standard_rate
                    when :rate_filter = 'Premium' then premium_rate
                    else LEAST(
                        CASE WHEN standard_rate = 0 THEN NULL ELSE standard_rate END,
                        CASE WHEN premium_rate = 0 THEN NULL ELSE premium_rate END
                    )
                    end as available_rate,
                row_number() over (partition by stays.hotel_id, check_out_date - check_in_date order by check_in_date) - sum(case when standard_rate > 0 or premium_rate > 0 then 1 else 0 end) over (partition by stays.hotel_id, check_out_date - check_in_date order by check_in_date) as group_number
            FROM stays
            LEFT JOIN hotels on stays.hotel_id = hotels.hotel_id
            WHERE check_in_date >= :start_date
            AND check_out_date <= :end_date
            AND status <> 'Inactive'
            AND last_checked_time >= now() - interval '48 hours'
            AND (hotels.hotel_city in (:hotel_cities) OR :hotel_cities is null)
            AND (hotels.hotel_country in (:hotel_countries) OR :hotel_countries is null)
            AND (hotels.award_category in (:award_categories) OR :award_categories is null)
        ), GroupedCounts as (
            SELECT
                c.*, 
                count(*) over (partition by hotel_id, group_number order by check_in_date, duration rows between current row AND UNBOUNDED FOLLOWING) as num_consecutive_nights,
                sum(available_rate * duration) / :lenght_of_stay over (partition by hotel_id, group_number order by check_in_date, duration rows between current row and unbounded following) as nightly_rate
            FROM ConsecutiveNights as c
        )
        select * from GroupedCounts
        where duration + num_consecutive_nights - 1 >= :length_of_stay
        and nightly_rate > 0 and nightly_rate <= :max_points_budget
        order by hotel_id, group_number, num_consecutive_nights
        """
    )

    def to_sql_param(lst):
        return ", ".join(f"'{item}'" for item in lst) if lst else None
    
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'hotel_cities': to_sql_param(hotel_cities),
        'hotel_countries': to_sql_param(hotel_countries),
        'award_categories': to_sql_param(award_categories),
        'length_of_stay': length_of_stay,
        'rate_filter': to_sql_param(rate_filter),
        'max_points_budget': max_points_budget
    }

    result = session.execute(statement=query, params=params).fetchall()

    return result

# result = get_consecutive_stays_2(
#     start_date='2023-08-31',
#     end_date='2023-08-31',
#     hotel_cities=['New York', 'Paris'],
#     hotel_countries=['United States', 'France'],
#     award_categories=[],
#     length_of_stay='3',
#     rate_filter=[],
#     max_points_budget='0',
# )