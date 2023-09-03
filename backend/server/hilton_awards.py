from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, MetaData, select, and_, update, func, case, text, join
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta
from hilton_auth import get_hilton_auth
from threaded_search_awards import update_rates
from retry import retry
import pytz
import random
import requests
import json
import os

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

username = os.getenv('BRIGHTDATA_USERNAME')
password = os.getenv('BRIHTDATA_PASSWORD')
port = 22225
session_id = random.random()
super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"

proxy_dict = {
    "http": super_proxy_url
}

def queue_stays(hotel_brand, search_frequency_hours, search_batch_size):
    stay_records = session.execute(
        select(*stays.c)
        .select_from(
            join(stays, hotels, stays.c.hotel_id == hotels.c.hotel_id)
        )
        .where(
            and_(
                stays.c.status == "Active", 
                stays.c.last_checked_time < datetime.now(pytz.UTC) - timedelta(hours=search_frequency_hours),
                stays.c.check_in_date >= datetime.now(pytz.UTC).date(),
                hotels.c.hotel_brand == hotel_brand
            )
        )
        .order_by(stays.c.last_checked_time)
        .limit(search_batch_size)
    ).fetchall()

    # Update status of fetched stay_records to 'Queued'
    stay_ids_to_update = [stay.stay_id for stay in stay_records]
    update_query = stays.update().where(stays.c.stay_id.in_(stay_ids_to_update)).values(status='Queued', last_queued_time=datetime.now(pytz.UTC))
    session.execute(update_query)
    session.commit()
    
    return stay_records

def upsert(session, table, list_of_dicts, unique_columns):
    for data_dict in list_of_dicts:
        stmt = insert(table).values(**data_dict)
        upd_stmt = stmt.on_conflict_do_update(
            index_elements=unique_columns,
            set_=data_dict
        )
        session.execute(upd_stmt)
    session.commit()

@retry(tries=5, delay=1, backoff=2)
def get_hilton_award(check_in_date, check_out_date, hotel_code, auth_token, cacheId, stay_id, hotel_id):
    award_updates = []
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_token
    }
    response_url = 'https://www.hilton.com/graphql/customer?appName=dx-res-ui&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=' + hotel_code
    query = {
        "query": "query hotel_shopAvailOptions_shopPropAvail($arrivalDate: String!, $ctyhocn: String!, $departureDate: String!, $language: String!, $guestLocationCountry: String, $numAdults: Int!, $numChildren: Int!, $numRooms: Int!, $displayCurrency: String, $guestId: BigInt, $specialRates: ShopSpecialRateInput, $rateCategoryTokens: [String], $selectedRoomRateCodes: [ShopRoomRateCodeInput!], $ratePlanCodes: [String], $pnd: String, $offerId: BigInt, $cacheId: String!, $knownGuest: Boolean, $modifyingReservation: Boolean, $currentlySelectedRoomTypeCode: String, $currentlySelectedRatePlanCode: String, $childAges: [Int], $adjoiningRoomStay: Boolean, $programAccountId: BigInt) {\n  hotel(ctyhocn: $ctyhocn, language: $language) {\n    ctyhocn\n    shopAvailOptions(input: {offerId: $offerId, pnd: $pnd}) {\n      maxNumChildren\n      altCorporateAccount {\n        corporateId\n        name\n      }\n      contentOffer {\n        name\n      }\n    }\n    shopAvail(\n      cacheId: $cacheId\n      input: {guestLocationCountry: $guestLocationCountry, arrivalDate: $arrivalDate, departureDate: $departureDate, displayCurrency: $displayCurrency, numAdults: $numAdults, numChildren: $numChildren, numRooms: $numRooms, guestId: $guestId, specialRates: $specialRates, rateCategoryTokens: $rateCategoryTokens, selectedRoomRateCodes: $selectedRoomRateCodes, ratePlanCodes: $ratePlanCodes, knownGuest: $knownGuest, modifyingReservation: $modifyingReservation, childAges: $childAges, adjoiningRoomStay: $adjoiningRoomStay, programAccountId: $programAccountId}\n    ) {\n      currentlySelectedRoom: roomTypes(\n        filter: {roomTypeCode: $currentlySelectedRoomTypeCode}\n      ) {\n        adaAccessibleRoom\n        roomTypeCode\n        roomRates(filter: {ratePlanCode: $currentlySelectedRatePlanCode}) {\n          ratePlanCode\n          rateAmount\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          rateChangeIndicator\n          ratePlan {\n            ratePlanName\n            commissionable\n            confidentialRates\n            specialRateType\n            hhonorsMembershipRequired\n            salesRate\n            redemptionType\n          }\n          pointDetails {\n            pointsRateFmt\n          }\n        }\n      }\n      statusCode\n      summary {\n        specialRates {\n          specialRateType\n          roomCount\n        }\n        requestedRates {\n          ratePlanCode\n          ratePlanName\n          roomCount\n        }\n      }\n      notifications {\n        subText\n        subType\n        title\n        text\n      }\n      addOnsAvailable\n      currencyCode\n      roomTypes {\n        roomTypeCode\n        adaAccessibleRoom\n        numBeds\n        roomTypeName\n        roomTypeDesc\n        roomOccupancy\n        premium\n        executive\n        towers\n        suite\n        code: roomTypeCode\n        name: roomTypeName\n        adjoiningRoom\n        thumbnail: carousel(first: 1) {\n          _id\n          altText\n          variants {\n            size\n            url\n          }\n        }\n        quickBookRate {\n          cashRatePlan\n          roomTypeCode\n          rateAmount\n          rateChangeIndicator\n          feeTransparencyIndicator\n          cmaTotalPriceIndicator\n          ratePlanCode\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          roomTypeCode\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          ratePlan {\n            commissionable\n            confidentialRates\n            ratePlanName\n            specialRateType\n            hhonorsMembershipRequired\n            salesRate\n            redemptionType\n            serviceChargesAndTaxesIncluded\n          }\n          serviceChargeDetails\n          pointDetails(perNight: true) {\n            pointsRate\n            pointsRateFmt\n          }\n        }\n        moreRatesFromRate {\n          rateChangeIndicator\n          feeTransparencyIndicator\n          cmaTotalPriceIndicator\n          roomTypeCode\n          rateAmount\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          serviceChargeDetails\n          ratePlanCode\n          ratePlan {\n            confidentialRates\n            serviceChargesAndTaxesIncluded\n          }\n        }\n        bookNowRate {\n          roomTypeCode\n          rateAmount\n          rateChangeIndicator\n          feeTransparencyIndicator\n          cmaTotalPriceIndicator\n          ratePlanCode\n          rateAmountFmt(decimal: 0, strategy: trunc)\n          amountAfterTaxFmt(decimal: 0, strategy: trunc)\n          fullAmountAfterTax: amountAfterTaxFmt\n          roomTypeCode\n          ratePlan {\n            commissionable\n            confidentialRates\n            ratePlanName\n            specialRateType\n            hhonorsMembershipRequired\n            salesRate\n            disclaimer {\n              diamond48\n            }\n            serviceChargesAndTaxesIncluded\n          }\n          serviceChargeDetails\n        }\n        redemptionRoomRates(first: 1) {\n          rateChangeIndicator\n          pointDetails(perNight: true) {\n            pointsRate\n            pointsRateFmt\n          }\n          sufficientPoints\n          pamEligibleRoomRate {\n            ratePlan {\n              ratePlanCode\n              rateCategoryToken\n              redemptionType\n            }\n            roomTypeCode\n            sufficientPoints\n          }\n        }\n      }\n      lowestPointsInc\n    }\n  }\n}",
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
    print(f"Response URL: {response_url}")
    response = requests.post(response_url, json=query, headers=headers, proxies=proxy_dict)
    try:
        awards = response.json()['data']['hotel']['shopAvail']['roomTypes']
        print("Awards found!")
    except Exception as e:
        print("No awards found!")
        print(response.json())
        print(f"Error on request: {e}")
        return []

    currency_code = response.json()['data']['hotel']['shopAvail']['currencyCode']
    search_url = f'https://www.hilton.com/en/book/reservation/rooms/?ctyhocn={hotel_code}&arrivalDate={check_in_date}&departureDate={check_out_date}&room1NumAdults=2&displayCurrency={currency_code}&redeemPts=true'
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
    print(f"Finished with hotel ID {str(hotel_id)} from {str(check_in_date)} to {str(check_out_date)}!")
    return award_updates

def search_awards(search_frequency_hours=24, search_batch_size=750):
    # awardsearch = AwardSearch()
    award_updates = []
    stay_updates = []
    search_counter = 0
    start_timer = datetime.now()
    auth_check_in_date = datetime.now() + timedelta(days=7)
    auth_check_out_date = datetime.now() + timedelta(days=8)
    hotel_code = 'LAXWAWA'
    cacheId, auth_token = get_hilton_auth(auth_check_in_date, auth_check_out_date, hotel_code)

    stay_records = queue_stays(hotel_brand='hilton', search_frequency_hours=search_frequency_hours, search_batch_size=search_batch_size)

    for stay in stay_records:
        search_counter += 1
        # print(stay)
        print(f"Searching #{search_counter} stay! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        stay = stay._asdict()
        hotel_code = stay['hotel_code']
        check_in_date = stay['check_in_date'].strftime('%Y-%m-%d')
        check_out_date = stay['check_out_date'].strftime('%Y-%m-%d')

        award_stays = get_hilton_award(
                                        #  hotel_brand='Hyatt', 
                                        hotel_code=hotel_code, 
                                        check_in_date=check_in_date, 
                                        check_out_date=check_out_date,
                                        auth_token=auth_token,
                                        cacheId=cacheId,
                                        stay_id=stay['stay_id'],
                                        hotel_id=stay['hotel_id'])
        
        if award_stays:
            award_updates.extend(award_stays)

        stay_updates.append({
            'stay_id': stay['stay_id'],
            'last_checked_time': datetime.now(pytz.UTC),
            'status': 'Active'
        })
    upsert(session, awards, award_updates, ['award_id'])
    upsert(session, stays, stay_updates, ['stay_id'])

# @retry(tries=5, delay=1, backoff=2)
# def update_rates():
#     print("Starting batch update of rates...")


#     stmt = stays.update().where(stays.c.last_checked_time >= (datetime.now(pytz.UTC) - timedelta(hours=2))).values(standard_rate=0, premium_rate=0)

#     # Prepare the raw SQL statement
#     stmt2 = text("""
#         UPDATE stays
#         SET 
#             standard_rate = coalesce(subquery.min_standard_rate,0),
#             premium_rate = coalesce(subquery.min_premium_rate,0),
#             currency_code = subquery.currency_code,
#             standard_cash = coalesce(subquery.min_standard_cash,0),
#             premium_cash = coalesce(subquery.min_premium_cash,0),
#             standard_cash_usd = coalesce(subquery.standard_cash_usd,0),
#             premium_cash_usd = coalesce(subquery.premium_cash_usd,0),
#             booking_url = search_url
#         FROM (
#             SELECT 
#                 stay_id,
#                 MIN(CASE WHEN room_category = 'STANDARD' AND last_checked_time >= now() - interval '24 hours' THEN lowest_points_rate END) AS min_standard_rate,
#                 MIN(CASE WHEN room_category in ('PREMIUM', 'SUITE') AND last_checked_time >= now() - interval '24 hours' THEN lowest_points_rate END) AS min_premium_rate,
#                 awards.currency_code,
#                 MIN(CASE WHEN room_category = 'STANDARD' AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal END) AS min_standard_cash,
#                 MIN(CASE WHEN room_category in ('PREMIUM', 'SUITE') AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal END) AS min_premium_cash,
#                 MIN(CASE WHEN room_category = 'STANDARD' AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal END) * fx.usd_exchange_rate AS standard_cash_usd,
#                 MIN(CASE WHEN room_category in ('PREMIUM', 'SUITE') AND last_checked_time >= now() - interval '48 hours' THEN cash_rate::decimal END) * fx.usd_exchange_rate AS premium_cash_usd,
#                 search_url
#             FROM awards
#             left join fx on awards.currency_code = fx.currency_code
#             GROUP BY stay_id, search_url, awards.currency_code, fx.usd_exchange_rate
#         ) AS subquery
#         WHERE stays.stay_id = subquery.stay_id
#     """)

#     # Calculate available award inventory
#     stmt3 = text("""
#         UPDATE stays
#         SET available_inventory = subquery.stays_available::decimal / subquery.total_tracked_dates::decimal
#         FROM (
#         SELECT
#             stay_id,
#             sum(case when standard_rate > 0 or premium_rate > 0 then 1 else 0 end) over (partition by hotel_id) as stays_available,
#             count(stay_id) over (partition by hotel_id) as total_tracked_dates
#         FROM stays
#         WHERE status <> 'Inactive'
#         AND check_in_date >= CURRENT_DATE
#         ) AS subquery
#         WHERE stays.stay_id = subquery.stay_id
#         """)

#     # Execute the UPDATE statement
#     try:
#         session.execute(stmt)
#         session.commit()
#     except SQLAlchemyError:
#         session.rollback()
#         raise
#     result = session.execute(stmt)
#     result = session.execute(stmt2)
#     result = session.execute(stmt3)
#     session.commit()

#     print("Batch update completed. {} rows affected.".format(result.rowcount))
#     print("Changes committed to the database.")

if __name__ == "__main__":
    # try:
        search_awards(search_frequency_hours=24, search_batch_size=10)
        update_rates()
        session.close()
    # except Exception as e:
    #     print("Error in main function: %s", str(e))  # Log exceptions

# cacheId = '5f704afc-7da3-478f-ba70-4db75b6c97d0'
# auth_token = 'Bearer DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.tYwYyjGMUGHHO4ilpwgeesNc_t_paQePrakSCIbkcSANh-cZ5WxzW_i3rzU_7AQIHUZE4eNRt1xLrwlvJgwevajiAB0c40E03FdiopqWNOYVxVA-840drZGgKbWqVH7St6uIJSaRGjugSkTmxjLCqhXSG27WmYW_E8amdU_kFN_dhgjwDsDXFChJu9hVhrqAhSLPTxo481lAlVLhAP4IfN0u1pXDMxegBWjxmTpjnpXNruNoISvVQSTyFOHJi_9yEz-UWP53Nh2OuYAHCE1SHmJxbk6bf1VPMmfFrjyikEoKHWdfWmebeEUo2e481-VJ1pfEMTVK--BR4MJhD0cV5A._Jor1rFpUkp4wLNz.YGxsTcA4BFtFTvc3vxmLRZDR7iRoUzax14-w9zWajAy7YL1qpuCVhLeFMgv7xKThHrpd41u8qa_9pSum1bFdH7YjkbbXKV5BgPykT0AfamfSEUzDfBEyyVnFAzIbu5hN20SaCwO7kpRRx1zUnclXuGo09ekOJDJWPkDmQ5x_EYLgQSwWMpM7cdnFN_G59actaLpdAeonN9XRrZnxTf-IGGSihf7rEGZM4mYOYxR-ct4uhP1emF1VLqsXwS5BEEZu8mTZ7--VTwpLBxj2U1H6y17PMk5hiCr1Q0rb5HDeD-i2RKlp5a7Q--5ZaeI19drXuB_kIUWw8ygt6x8H9FMsuo0BvY21ixHx4UMA4QKqQubvHvlfplzgYf7kHQSzfi2nFLs8fEVPYYiFffoiOefBvxxcdNsLPEhPUvrohLJSl_ZOiGWdp1Hafvcu48MmTDqNB24kbZ5xYqeC6ADT5Q-5z4FuFTyBb3omtruw3Frvavq583b2TpQF1_TB1fIQux6IJtz_xRjjj7wj7uNl3mX4-3UNl81CBJa6mllPovr5GM4h6HPMymHUuq2Ia1K-anYDSEIu-zjhZaEJZ320ahBWH1VsuDqr-Unx7jOQNQXfv7JhkowQHMhah5Hyc5gQr_NE8J7I9M_FCka6AUtBj_icttiHQInWsAQi-T3pNTMZZab4NF9upMo.HUw6RpCDbkJVo6ALqFw35A'
# award_data_to_update = get_hilton_awards(check_in_date, check_out_date, hotel_code, auth_token, cacheId)
# print(award_data_to_update)