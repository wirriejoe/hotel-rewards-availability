from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, MetaData, select, and_, update, func, case, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta
from hilton_auth import get_hilton_auth
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

# Map tables
stays = meta.tables['stays']
awards = meta.tables['awards']

username = os.getenv('BRIGHTDATA_USERNAME')
password = os.getenv('BRIHTDATA_PASSWORD')
port = 22225
session_id = random.random()
super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"

proxy_dict = {
    "http": super_proxy_url
}

def get_hilton_award(check_in_date, check_out_date, hotel_code, auth_token, cacheId):
    
    award_updates = []
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_token
    }
    url = 'https://www.hilton.com/graphql/customer?appName=dx-res-ui&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=' + hotel_code

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

    response = requests.post(url, json=query, headers=headers, proxies=proxy_dict)
    # print(response.json())
    if response.status_code == 200:
        print("Success!")
        response_json = response.json()
        with open("response.json", "w") as f:
            json.dump(response_json, f)
    else:
        print("Failed! " + response.status_code)
        print(response.text)

    awards = response.json()['data']['hotel']['shopAvail']['roomTypes']
    currency_code = response.json()['data']['hotel']['shopAvail']['currencyCode']

    for award in awards:
        award_updates.append({
                # 'award_id': award_id,
                # 'hotel_id': hotel_id,
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
                'room_name': award['name'],
                'room_desc': award['roomTypeDesc'],
                'room_type_code': award['code'],
                'room_category': 'SUITE' if award['suite'] else 'STANDARD',
                'image': award['thumbnail'][0]['variants'][0]['url'],
                'lowest_points_rate': award['redemptionRoomRates'][0]['pointDetails'][0]['pointsRate'],
                'cash_rate': ''.join(c for c in award['quickBookRate']['fullAmountAfterTax'] if c.isdigit() or c == '.'),
                'currency_code': response.json()['data']['hotel']['shopAvail']['currencyCode'],
                # 'availability': room_quantity,
                'search_url': f'https://www.hilton.com/en/book/reservation/rooms/?ctyhocn={hotel_code}&arrivalDate={check_in_date}&departureDate={check_out_date}&room1NumAdults=2&displayCurrency={currency_code}&redeemPts=true',
                # 'stay_id': stay_id,
                'last_checked_time': datetime.now(pytz.UTC)
        })
    print(award_updates)
    return award_updates

def search_awards(search_frequency_hours=24, search_batch_size=750):
    # awardsearch = AwardSearch()
    award_updates = []
    stay_updates = []
    search_counter = 0
    start_timer = datetime.now()
    check_in_date = "2023-09-29"
    check_out_date = "2023-09-30"
    hotel_code = 'LAXWAWA'

    # cacheId, auth_token = get_hilton_auth(check_in_date, check_out_date, hotel_code)

    # print(cacheId)
    # print(auth_token)

    cacheId = '0667d1a2-35e0-4a73-a74a-d3f3795d5e72'
    auth_token = 'Bearer DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.teTcGiEZaKAO5Ldb6_48VPXbB9XiGtSfpeCiKt1YpB9lzLIPCnc3NWXaydvttLFXSYgmyOHY0dqpbDgsh--P4ksEh7cqAwqrLBaI5F2t7AV8NRE5JkstRJ6WJsS8UxqDtFhuUuUs9zQCYkYUc2pL0qe3uder7dfCJ2nDmI7ZJ714MjerDL2RYtDH8_PfVkGGSYJ1YLQxemA3UH0g8bQeTY1YJtBWWPAz2RqaeIVp4hUttiNbt9mO1yc1QjXOMbiQ4PYcRB9LmDhKJtPmZn-7r28CakBdldZitj6wATkOhu6eucaBQ7Wv_rsDYoIp0Z1ZwJKNqlmLaDh-ZTIRMJEauw.pudlUgBuIV1HgdIq.L4MF_IljCmRAaQgDg52avjc55zxDsUrAGHK-7Xs7Y8uhxI539bde2yip6TD41PdOFJVz-YDTbPiGSt3lqDG1NoAUEJ4So6R7LP2kKnrHSHrxiA-rJ2m89btBMKVsV2ZIgWqogfqMMiRQlKVvDYmszYE28bIEyL2tvlBqATq4frPjurVMyRskOdrzciFtZ4HrjkNv7gA8BaGwlXxIEeUupVO2VC9csdZUi6l27-IzZBqaM_TgC9yz0HEp5iAQQABw7qjvdBBBd1FSF5gIjyK9356laMd_nrA23weWabLiN89RWBoCvX_UXP-Wxt5NDPzMNNJYh2WwrVMNnWm-R_FX1XcgRxfJx9HvCGVCCYIYGisCcmKwH18dBClPFKokfx5W2qxmSldkGWLhf8XauzgPgh6o-1sjmjZt4Dyl5sRf1YvdGFGxYk9FPTOjk2Ng6Ex06vebx4VIRsz4YtnqM1LWK3ioGJHKZ2rNGbZcpJ-diAojJMY4A-xA2GmSJa0jhvyqhh1jvI8i1lpBGCEhQLehOZ3KtBgL5iReHtHY9W-0Gb2EhcMhsHmS7KOT99fLUI-Rx-iAUdjhBbz6re5Is2y6Gc-6WJgmZ8TJbOF9T-ObvL8HjFMu0WNuhMamYe2bcnGoq7h-vzE8gL5cUOGVCR1CSpRXFMl6btKEelzbAEYoL3dfh-GFdm4.De3AU2T1vYpQPLUrpdYhRg'

    stay_records = [
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-21',
            'check_out_date': '2023-09-22'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-22',
            'check_out_date': '2023-09-23'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-23',
            'check_out_date': '2023-09-24'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-24',
            'check_out_date': '2023-09-25'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-25',
            'check_out_date': '2023-09-26'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-26',
            'check_out_date': '2023-09-27'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-27',
            'check_out_date': '2023-09-28'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-28',
            'check_out_date': '2023-09-29'
        },
        {
            'hotel_code': 'LAXWAWA',
            'check_in_date': '2023-09-29',
            'check_out_date': '2023-09-30'
        }
    ]

    # stay_records = session.execute(
    #     select(*stays.c).where(
    #         and_(
    #             stays.c.status == "Active", 
    #             stays.c.last_checked_time < datetime.now(pytz.UTC) - timedelta(hours=search_frequency_hours),
    #             stays.c.check_in_date >= datetime.now(pytz.UTC).date()
    #         )
    #     ).order_by(stays.c.last_checked_time)
    #     .limit(search_batch_size)
    # ).fetchall()

    # print(stay_records)

    # # Update status of fetched stay_records to 'Queued'
    # # stay_ids_to_update = [record.stay_id for record in stay_records]
    # # update_query = stays.update().where(stays.c.stay_id.in_(stay_ids_to_update)).values(status='Queued')
    # # session.execute(update_query)
    # # session.commit()

    for stay in stay_records:
        print(stay)
        search_counter += 1
        print(f"Searching #{search_counter} stay! {(datetime.now()-start_timer).total_seconds()}s has elapsed.")
        # stay = stay._asdict()
        hotel_code = stay['hotel_code']
        check_in_date = stay['check_in_date']
        check_out_date = stay['check_out_date']

        award_stays = get_hilton_award(
                                        #  hotel_brand='Hyatt', 
                                        hotel_code=hotel_code, 
                                        check_in_date=check_in_date, 
                                        check_out_date=check_out_date,
                                        auth_token=auth_token,
                                        cacheId=cacheId)
        
        # if award_stays:
        #     award_updates.extend(update_awards_table(award_stays, stay))

    #     stay_updates.append({
    #         'stay_id': stay['stay_id'],
    #         'last_checked_time': datetime.now(pytz.UTC),
    #         'status': 'Active'
    #     })
    # upsert(session, awards, award_updates, ['award_id'])
    # upsert(session, stays, stay_updates, ['stay_id'])

if __name__ == "__main__":
    # try:
    search_awards(search_frequency_hours=24, search_batch_size=10)
    # except Exception as e:
    #     print("Error in main function: %s", str(e))  # Log exceptions

# award_data_to_update = get_hilton_awards(check_in_date, check_out_date, hotel_code, auth_token, cacheId)
# print(award_data_to_update)