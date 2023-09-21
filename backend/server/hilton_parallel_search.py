from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, MetaData, select, and_, join
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from auth import get_hilton_auth
from helpers import queue_stays, upsert, update_rates, send_error_to_slack
from tenacity import retry, stop_after_attempt, wait_exponential
from itertools import chain
from helpers import queue_stays, upsert, update_rates, send_error_to_slack
import pytz
import random
import os
import asyncio
import aiohttp

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
sem = asyncio.Semaphore(80)

def get_global_auths(num_runs):
    auths = []  # Declare global variable
    
    for _ in range(num_runs):
        auth_check_in_date = datetime.now() + timedelta(days=random.randint(4,10))
        auth_check_out_date = auth_check_in_date + timedelta(days=random.randint(1,5))
        auth_hotel_code = 'LAXWAWA'
        
        cacheId, auth_token = get_hilton_auth(auth_check_in_date, auth_check_out_date, auth_hotel_code)
        auths.append({
            "cacheId": cacheId,
            "auth_token": auth_token
        })
    
    return auths

def on_after(retry_state):
    if retry_state.attempt_number == 4:  # Replace 3 with your max retries
        print("Max retries reached. Skipping this run.")
        return

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=5), after=on_after)
async def get_hilton_awards(session, check_in_date, check_out_date, hotel_code, stay_id, hotel_id, auths):
    async with sem:
        global search_counter, super_proxy_url, proxy_dict
        session_id = random.random()
        super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"
        proxy_dict["http"] = super_proxy_url  # Update proxy_dict with the new super_proxy_url
        award_updates = []

        try:
            # print(f"Auth_token: {auth_token}, cacheId: {cacheId}")
            rand_auth = random.randint(0,len(auths)-1)
            auth_token = auths[rand_auth]['auth_token']
            cacheId = auths[rand_auth]['cacheId']
            url = 'https://www.hilton.com/graphql/customer?appName=dx-res-ui&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=' + hotel_code
            headers = {
                'Content-Type': 'application/json',
                'Authorization': auth_token
            }
            query = {
                "query": """query hotel_shopAvailOptions_shopPropAvail($arrivalDate: String!, $ctyhocn: String!, $departureDate: String!, $language: String!, $guestLocationCountry: String, $numAdults: Int!, $numChildren: Int!, $numRooms: Int!, $displayCurrency: String, $guestId: BigInt, $specialRates: ShopSpecialRateInput, $rateCategoryTokens: [String], $selectedRoomRateCodes: [ShopRoomRateCodeInput!], $ratePlanCodes: [String], $pnd: String, $offerId: BigInt, $cacheId: String!, $knownGuest: Boolean, $modifyingReservation: Boolean, $currentlySelectedRoomTypeCode: String, $currentlySelectedRatePlanCode: String, $childAges: [Int], $adjoiningRoomStay: Boolean, $programAccountId: BigInt) {
                            hotel(ctyhocn: $ctyhocn, language: $language) {
                                ctyhocn
                                shopAvailOptions(input: {offerId: $offerId, pnd: $pnd}) {
                                maxNumChildren
                                }
                                shopAvail(
                                cacheId: $cacheId
                                input: {guestLocationCountry: $guestLocationCountry, arrivalDate: $arrivalDate, departureDate: $departureDate, displayCurrency: $displayCurrency, numAdults: $numAdults, numChildren: $numChildren, numRooms: $numRooms, guestId: $guestId, specialRates: $specialRates, rateCategoryTokens: $rateCategoryTokens, selectedRoomRateCodes: $selectedRoomRateCodes, ratePlanCodes: $ratePlanCodes, knownGuest: $knownGuest, modifyingReservation: $modifyingReservation, childAges: $childAges, adjoiningRoomStay: $adjoiningRoomStay, programAccountId: $programAccountId}
                                ) {
                                currentlySelectedRoom: roomTypes(
                                    filter: {roomTypeCode: $currentlySelectedRoomTypeCode}
                                ) {
                                    adaAccessibleRoom
                                    roomTypeCode
                                    roomRates(filter: {ratePlanCode: $currentlySelectedRatePlanCode}) {
                                    ratePlanCode
                                    rateAmount
                                    }
                                }
                                statusCode
                                currencyCode
                                roomTypes {
                                    code: roomTypeCode
                                    name: roomTypeName
                                    roomTypeDesc
                                    suite
                                    thumbnail: carousel(first: 1) {
                                    variants {
                                        url
                                    }
                                    }
                                    quickBookRate {
                                    fullAmountAfterTax: amountAfterTaxFmt
                                    }
                                    redemptionRoomRates(first: 1) {
                                    pointDetails(perNight: true) {
                                        pointsRate
                                    }
                                    }
                                }
                                }
                            }
                            }
                """,
                "operationName": "hotel_shopAvailOptions_shopPropAvail",
                "variables": {
                    "arrivalDate": check_in_date,
                    "departureDate": check_out_date,
                    "numAdults": 2,
                    "numChildren": 0,
                    "numRooms": 1,
                    "ctyhocn": hotel_code,
                    "language": "en",
                    "specialRates": {
                        "hhonors": True,
                    },
                    "cacheId": cacheId
                }
            }
            async with session.post(url, json=query, headers=headers, proxy=super_proxy_url, timeout=30) as response:
                response.raise_for_status()
                data = await response.json()
                try:
                    awards = data['data']['hotel']['shopAvail']['roomTypes']
                    # print("Awards found!")
                except Exception as e:
                    # print("No awards found!")
                    print(data)
                    print(f"Error on request: {e}")
                    return []

                currency_code = data['data']['hotel']['shopAvail']['currencyCode']
                search_url = f'https://www.hilton.com/en/book/reservation/rooms/?ctyhocn={hotel_code}&arrivalDate={check_in_date}&departureDate={check_out_date}&room1NumAdults=2&displayCurrency={currency_code}&redeemPts=true'
                print(f"Response URL: {url}")
                print(f"Verification URL: {search_url}")

                for award in awards:
                    try:
                        lowest_points_rate = award['redemptionRoomRates'][0]['pointDetails'][0]['pointsRate']
                    except IndexError:
                        continue
                    room_type_code = award['code']
                    room_category = 'SUITE' if award['suite'] else 'STANDARD'
                    award_id = f"{stay_id}-{room_type_code}-{room_category}"

                    award_updates.append({
                            'award_id': award_id,
                            'hotel_id': hotel_id,
                            'check_in_date': check_in_date,
                            'check_out_date': check_out_date,
                            'room_name': award['name'],
                            'room_desc': award['roomTypeDesc'],
                            'room_type_code': room_type_code,
                            'room_category': room_category,
                            'image': award['thumbnail'][0]['variants'][0]['url'] if award['thumbnail'] else '',
                            'lowest_points_rate': lowest_points_rate,
                            'cash_rate': ''.join(c for i, c in enumerate(award['quickBookRate']['fullAmountAfterTax']) if c.isdigit() or (c == '.' and award['quickBookRate']['fullAmountAfterTax'][:i].count('.') < 1)),
                            'currency_code': currency_code,
                            'availability': 1,
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
            task = asyncio.ensure_future(get_hilton_awards(session, stay.check_in_date.strftime('%Y-%m-%d'), stay.check_out_date.strftime('%Y-%m-%d'), stay.hotel_code, stay.stay_id, stay.hotel_id, auths))
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out the exceptions and keep only successful results
        successful_results = [result for result in results if not isinstance(result, Exception)]
        print(f"Finished searches! Returning {len(successful_results)} results!")
        return successful_results
    
if __name__ == "__main__":
    try:
        # Single-thread: queue_stays
        stay_records = queue_stays("hilton", 24, 15000)
        auths = get_global_auths(5)

        # Asynchronous: Fetch awards
        award_results = asyncio.run(fetch_stay_awards(stay_records, auths))
        award_updates = list(chain.from_iterable(award_results))

        # Single-thread: upsert, update rates, close session
        print("Finished joining threads! Upserting data.")
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