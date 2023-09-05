from datetime import datetime
import requests
import json
import pytz
import random

# IHG rate code definitions https://quizlet.com/395739938/hi-rate-codes-flash-cards/

def get_ihg_awards(check_in_date, check_out_date, hotel_code, destination, stay_id='', hotel_id=''):
    url = "https://apis.ihg.com/availability/v3/hotels/offers?fieldset=rateDetails,rateDetails.policies,rateDetails.bonusRates,rateDetails.upsells"

    headers = {
        'X-Ihg-Api-Key': 'se9ym5iAzaW8pxfBjkmgbuGjJcr3Pj6Y'
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
    response = requests.post(url, headers=headers, json=query)
    # Parse the JSON response
    data = response.json()

    award_updates = []
    awards = [rate for rate in data['hotels'][0]['rateDetails']['offers'] if rate['availableStatus'] == 'AVAILABLE' and rate['ratePlanCode'] == 'IVANI']
    check_in_year, check_in_month, check_in_day = check_in_date.split('-')[::-1]
    check_out_year, check_out_month, check_out_day = check_in_date.split('-')[::-1]

    currency_code = data['hotels'][0]['propertyCurrency']
    search_url = f'www.ihg.com/intercontinental/hotels/us/en/find-hotels/select-roomrate?qDest={destination}&qSlH={hotel_code}&qCiD={check_in_day}&qCiMy={check_in_month + check_in_year}&qCoD={check_out_day}&qCoMy={check_out_month + check_out_year}&qRms=1&qAdlt=2&displayCurrency={currency_code}&qRtP=IVANI'
    print(f"Response URL: {url}")
    print(f"Verification URL: {search_url}")

    for award in awards:
        room_type_code = award['productUses'][0]['inventoryTypeCode']
        hotel = [room for room in data['hotels'][0]['productDefinitions'] if room['inventoryTypeCode'] == room_type_code]
        # award_id = f"{stay_id}-{room_type_code}-{room_category}"

        award_updates.append({
                # 'award_id': award_id,
                # 'hotel_id': hotel_id,
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
                'room_name': hotel[0]['inventoryTypeName'],
                'room_desc': hotel[0]['description'],
                'room_type_code': room_type_code,
                'room_category': 'SUITE' if hotel[0]['isPremium'] else 'STANDARD',
                # 'image': '',
                'lowest_points_rate': award['rewardNights']['pointsOnly']['averageDailyPoints'],
                'cash_rate': award['totalRate']['amountAfterTax'],
                'currency_code': currency_code,
                'availability': award['productUses'][0]['numberOfAvailableProducts'],
                'search_url': search_url,
                # 'stay_id': stay_id,
                'last_checked_time': datetime.now(pytz.UTC)
        })
        # print(award_id)
        print(award_updates)
    return award_updates
    

check_in_date = '2023-09-28'
check_out_date = '2023-09-29'
hotel_code = 'SINIC'
destination = 'Singapore'
data = get_ihg_awards(check_in_date, check_out_date, hotel_code, destination)