from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, MetaData, select, and_, join
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from auth import get_ihg_auth
from helpers import queue_stays, upsert, update_rates, send_error_to_slack
from tenacity import retry, stop_after_attempt, wait_exponential
from itertools import chain
import pytz
import random
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

load_dotenv(find_dotenv())

database_url = os.getenv('POSTGRES_DB_URL')
print("Database URL: %s", database_url)  # Use lazy logging format
engine = create_engine(database_url) # add , echo=True for logging
Session = sessionmaker(bind=engine)
session = Session()

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
start_timer = datetime.now()
sem = asyncio.Semaphore(10)

def get_global_auths(num_runs):
    auths = []  # Declare global variable
    with ThreadPoolExecutor(max_workers=5) as executor:
        auths = list(executor.map(
            lambda _: {
                "api_key": get_ihg_auth(
                    (datetime.now() + timedelta(days=random.randint(4, 10))).date(),
                    (datetime.now() + timedelta(days=random.randint(4, 10) + random.randint(1, 5))).date()
                )
            },
            range(num_runs)
        ))
    return auths

def on_after(retry_state):
    if retry_state.attempt_number == 4:  # Replace 4 with your max retries
        print("Max retries reached. Skipping this run.")
        return

# IHG rate code definitions https://quizlet.com/395739938/hi-rate-codes-flash-cards/
@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=5), after=on_after)
async def get_ihg_awards(session, check_in_date, check_out_date, hotel_code, destination, stay_id, hotel_id, auths):
    async with sem:
        global search_counter
        award_updates = []

        try:
            rand_auth = random.randint(0,len(auths)-1)
            url = "https://apis.ihg.com/availability/v3/hotels/offers?fieldset=rateDetails"
                    # rateDetails.policies,
                    # rateDetails.bonusRates,
                    # rateDetails.upsells
            
            headers = {
                'X-Ihg-Api-Key': auths[rand_auth]['api_key']
            }
            query = {"products": [{
                        "productCode": "SR",
                        "guestCounts": [
                            {"otaCode": "AQC10",
                            "count": 2},
                            {"otaCode": "AQC8",
                            "count": 0}],
                        "startDate": check_in_date,
                        "endDate": check_out_date,
                        "quantity": 1}],
                "startDate": check_in_date,
                "endDate": check_out_date,
                "hotelMnemonics": [hotel_code],
                "rates": {"ratePlanCodes": [{"internal": "IVANI"}] # award program code = IVANI
            },
                "options": {"disabilityMode": "ACCESSIBLE_AND_NON_ACCESSIBLE",
                    "returnAdditionalRatePlanDescriptions": True,
                    "includePackageDetails": True}
            }

            # Make the POST request and capture the response
            async with session.post(url, json=query, headers=headers, proxy=super_proxy_url, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                try:
                    awards = [rate for rate in data['hotels'][0]['rateDetails']['offers'] if rate['availableStatus'] == 'AVAILABLE' and rate['ratePlanCode'] == 'IVANI']
                    # print("Awards found!")
                except Exception as e:
                    # print("No awards found!")
                    print(data)
                    print(f"Error on request: {e}")
                    return []
                check_in_year, check_in_month, check_in_day = check_in_date.split('-')[::-1]
                check_out_year, check_out_month, check_out_day = check_out_date.split('-')[::-1]

                currency_code = data['hotels'][0]['propertyCurrency']
                search_url = f'www.ihg.com/intercontinental/hotels/us/en/find-hotels/select-roomrate?qDest={destination}&qSlH={hotel_code}&qCiD={check_in_day}&qCiMy={check_in_month + check_in_year}&qCoD={check_out_day}&qCoMy={check_out_month + check_out_year}&qRms=1&qAdlt=2&displayCurrency={currency_code}&qRtP=IVANI'
                print(f"Response URL: {url}")
                print(f"Verification URL: {search_url}")

                for award in awards:
                    room_type_code = award['productUses'][0]['inventoryTypeCode']
                    hotel = [room for room in data['hotels'][0]['productDefinitions'] if room['inventoryTypeCode'] == room_type_code]
                    room_category = 'SUITE' if hotel[0]['isPremium'] else 'STANDARD'
                    award_id = f"{stay_id}-{room_type_code}-{room_category}"

                    award_updates.append({
                            'award_id': award_id,
                            'hotel_id': hotel_id,
                            'check_in_date': check_in_date,
                            'check_out_date': check_out_date,
                            'room_name': hotel[0]['inventoryTypeName'],
                            'room_desc': hotel[0]['description'],
                            'room_type_code': room_type_code,
                            'room_category': room_category,
                            # 'image': '',
                            'lowest_points_rate': award['rewardNights']['pointsOnly']['averageDailyPoints'],
                            'cash_rate': award['totalRate']['amountAfterTax'],
                            'currency_code': currency_code,
                            'availability': award['productUses'][0]['numberOfAvailableProducts'],
                            'search_url': search_url,
                            'stay_id': stay_id,
                            'last_checked_time': datetime.now(pytz.UTC)
                    })
                    print(award_id)
                search_counter += 1
                stay_updates.append({
                    'stay_id': stay_id,
                    'last_checked_time': datetime.now(pytz.UTC),
                    'status': 'Active'
                })
                print(f"Finished with Search #{search_counter} for hotel ID {str(hotel_id)} from {str(check_in_date)} to {str(check_out_date)}! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        except Exception as e:
            print(f"Response URL {url} failed with exception: {e}")
            raise  # Re-raise the exception to trigger the retry logic
        return award_updates

async def fetch_stay_awards(stay_records, auths):
    # Create a list of tasks
    tasks = []
    async with aiohttp.ClientSession() as session:
        for stay in stay_records:
            task = asyncio.ensure_future(get_ihg_awards(session, stay.check_in_date.strftime('%Y-%m-%d'), stay.check_out_date.strftime('%Y-%m-%d'), stay.hotel_code, stay.destination_code, stay.stay_id, stay.hotel_id, auths))
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out the exceptions and keep only successful results
        successful_results = [result for result in results if not isinstance(result, Exception)]
        print(f"Finished searches! Returning {len(successful_results)} results!")
        return successful_results

if __name__ == "__main__":
    try:
        # Single-thread: queue_stays
        stay_records = queue_stays("ihg", 24, 12000)
        # auths = ['se9ym5iAzaW8pxfBjkmgbuGjJcr3Pj6Y']
        auths = get_global_auths(1)

        # Asynchronous: Fetch awards
        award_results = asyncio.run(fetch_stay_awards(stay_records, auths))
        award_updates = list(chain.from_iterable(award_results))

        # Single-thread: upsert, update rates, close session
        print(f"Upserting {len(award_updates)} award updates to awards table! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        upsert(session, temp_awards, award_updates, ["award_id"])
        print(f"Upserting {len(stay_updates)} stay updates to stays table! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        upsert(session, stays, stay_updates, ['stay_id'])
        print(f"Updating rates! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        update_rates()
        session.close()
    except Exception as e:
        session.close()
        send_error_to_slack(str(e))
        print("Error in main function: %s", str(e))

# check_in_date = '2023-09-28'
# check_out_date = '2023-09-29'
# hotel_code = 'SINIC'
# destination = 'Singapore'
# auths = 'se9ym5iAzaW8pxfBjkmgbuGjJcr3Pj6Y'
# data = get_ihg_awards('', check_in_date, check_out_date, hotel_code, destination, '', '', auths)