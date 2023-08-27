import requests
import json
import time
from pprint import pprint

def fetch_graphql_data(endpoint, query, max_retries=3):
    # Initialize variables
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.WGTKJVCLgj5z_ed32UyCHNkgmJyP8KR9XVBrj2uUAcGWNH1gt5aQ1nwCTKbdDM5d5UdTxRiHWa3nRX0enhJZdaJ4zZIvXL2ER5w3BAjByUmKzetf6ATUnJfPpSfvKJkIyi2lGBaj_9yztcpbHM2sQ_uSi7OHuyrO9PqBWhoXzKGtYJ9UhZIyEAUjJoIxr81kE1-XtaPEK_mAkciF8Ia7CTkwJH_5QNghd-dF-0MI92HHrFdFWhNSyYa5u1XyAMjr-UeTloSOKvhypk7QqXHlwgGP_x53R5Cn1UaQgUVrK7O_1D_JmgwYQti_sWPjF-aO1NV7RcD8S3wyEEb9DFyh2w.fvr9f0JMms_j0ZLX.HPJsbqwkgbiDsZsJRScjlq1Noj3wikviwP4ZTFnQ_C4ptxM4YP7B0COCyG5WWVgu-sS5PS_D-J0fNMCJDXRQdXDuHppMeJzYHbs7kYYg-S9dgyGfDyQn65gN8FX9VO40ShuJBND7ii6_Z7TlZMSz-iWN4LdPgStPiRnbFD3dNqwKvtnlPKNHEPQukifNRDlIOsmm5AyLkKHQ8yvFBSBKomztx_cKKuaRQrNNHAOxYfwsb8cMeDPYvYpXU_x10-xrJFgsiGCCZR18uV-QRXoMeCKnE1qHWtKHYXupLIlsS6ngZMdNCwmgddYR5mz6la-pO1_cKeFkioqm-gVc_EjVrdf8Rx_oCrwsUZ_U51h0q9gAoI9jFuiJOV3SMiX42_KVbZ72Eco99TC9KrwdMP6Ys_6yOAL9kTGbOR7r1pm5ZW-aBURHiQrlSLv4lU4lF4sCcMekojgVwQ2k6VvSn-n2c5Ymk4PjMfoxT-KQ42VIH63bwO7sJj8k6nteyCV2q7mdGklfLRQZDw0nBwcrxsF_PSK9EROEqyApw121CE0oQ5JFMvzetxHgPeptGpt9jX5wiqrdrlB-zpqmF8gJOOe3kSoTkEn8F5ZpcG8uPyeciv0Q6uWNHbGagDHFthr18m8uyzEu4JpAS5vE1YC-knzERv5TGy-V2XF8NfrM-hk6MabO2-MY3nY.PCSCN3MEemoIkPe_jmkpzQ'
    }
    retries = 0

    # Loop to retry request
    while retries <= max_retries:
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=query
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            retries += 1
            print(f"Error occurred: {e}, Retrying ({retries}/{max_retries})")
            time.sleep(2 ** retries)  # Exponential backoff
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            break

    print('Max retries exhausted! Returning None.')
    return None  # Return None after max_retries

def fetch_hotel_data(uri):
    hotel_url = 'https://www.hilton.com//graphql/customer?appName=dx_shop_search_app&operationName=hotelSummaryOptions_geocodePage&originalOpName=hotelSummaryOptions_geocodePage&bl=en'
    
    hotel_query =  {
        "query": "query hotelSummaryOptions_geocodePage($language: String!, $path: String!, $queryLimit: Int!, $currencyCode: String!, $distanceUnit: HotelDistanceUnit, $titleFormat: MarkdownFormatType!) {\n  geocodePage(language: $language, path: $path) {\n    location {\n      pageInterlinks {\n        title\n        links {\n          name\n          uri\n        }\n      }\n      title(format: $titleFormat)\n      accessibilityTitle\n      meta {\n        pageTitle\n        description\n      }\n      name\n      brandCode\n      category\n      uri\n      globalBounds\n      breadcrumbs {\n        uri\n        name\n      }\n      about {\n        contentBlocks {\n          title(format: text)\n          descriptions\n          orderedList\n          unorderedList\n        }\n      }\n      paths {\n        base\n      }\n    }\n    match {\n      address {\n        city\n        country\n        countryName\n        state\n        stateName\n      }\n      geometry {\n        location {\n          latitude\n          longitude\n        }\n        bounds {\n          northeast {\n            latitude\n            longitude\n          }\n          southwest {\n            latitude\n            longitude\n          }\n        }\n      }\n      name\n      type\n    }\n    hotelSummaryOptions(distanceUnit: $distanceUnit, sortBy: distance) {\n      _hotels {\n        totalSize\n      }\n      bounds {\n        northeast {\n          latitude\n          longitude\n        }\n        southwest {\n          latitude\n          longitude\n        }\n      }\n      amenities {\n        id\n        name\n        hint\n      }\n      amenityCategories {\n        name\n        id\n        amenityIds\n      }\n      brands {\n        code\n        name\n      }\n      hotels(first: $queryLimit) {\n        amenityIds\n        brandCode\n        ctyhocn\n        distance\n        distanceFmt\n        facilityOverview {\n          allowAdultsOnly\n        }\n        name\n        contactInfo {\n          phoneNumber\n        }\n        display {\n          open\n          openDate\n          preOpenMsg\n          resEnabled\n          resEnabledDate\n        }\n        disclaimers {\n          desc\n          type\n        }\n        address {\n          addressFmt\n          addressLine1\n          city\n          country\n          countryName\n          postalCode\n          state\n          stateName\n        }\n        localization {\n          currencyCode\n          coordinate {\n            latitude\n            longitude\n          }\n        }\n        masterImage(variant: searchPropertyImageThumbnail) {\n          altText\n          variants {\n            size\n            url\n          }\n        }\n        leadRate {\n          lowest {\n            rateAmount(currencyCode: $currencyCode)\n            rateAmountFmt(decimal: 0, strategy: trunc)\n            ratePlanCode\n            ratePlan {\n              ratePlanName\n              ratePlanDesc\n            }\n          }\n        }\n      }\n    }\n  }\n}",
        "operationName": "hotelSummaryOptions_geocodePage",
        "variables": {
            "path": f"{uri}",
            "language": "en",
            "queryLimit": 150,
            "currencyCode": "USD",
            "titleFormat": "md"
        }
    }
    hotel_data = fetch_graphql_data(hotel_url, hotel_query)['data']['geocodePage']

    return hotel_data

def process_hotels(hotels):
    result = []
    for hotel in hotels:
        hotel_data = {
            'hotel_name': hotel.get('name', ''),
            'hotel_brand': 'Hilton',
            'sub_brand': hotel.get('brandCode', ''),
            'hotel_code': hotel.get('ctyhocn', ''),
            'image': hotel.get('masterImage', {}).get('variants', [-1])[-1].get('url', '') if hotel.get('masterImage') else '',
            'hotel_address': hotel.get('address', {}).get('addressLine1', ''),
            'hotel_zipcode': hotel.get('address', {}).get('postalCode', ''),
            'hotel_city': hotel.get('address', {}).get('city', ''),
            'hotel_province': hotel.get('address', {}).get('stateName', ''),
            'hotel_country': hotel.get('address', {}).get('countryName', ''),
            'hotel_longitude': hotel.get('localization', {}).get('coordinate', {}).get('longitude', ''),
            'hotel_latitude': hotel.get('localization', {}).get('coordinate', {}).get('latitude', ''),
            'hotel_status': 'Open' if hotel.get('display', {}).get('open', False) else ''
        }
        result.append(hotel_data)
    return result

region_url = 'https://www.hilton.com/graphql/customer?appName=dx_shop_search_app&operationName=regions&originalOpName=allRegions&bl=en'
# Fetch country links
region_query = {
    "query": "query regions($language: String!) {\n  na: regions(\n    language: $language\n    containsHotels: true\n    filter: {htmlSiteMap: true, name: \"North America\"}\n  ) {\n    name\n    locationPageUri\n    countries {\n      code\n      name\n      locationPageUri\n      displayName\n      states(sort: {by: name, order: asc}) {\n        name\n        locationPageUri\n      }\n      cities(sort: {by: name, order: asc}, onlyIfNoStates: true) {\n        name\n        locationPageUri\n      }\n    }\n  }\n  others: regions(\n    language: $language\n    containsHotels: true\n    filter: {htmlSiteMap: true, name_not: \"North America\"}\n  ) {\n    name\n    locationPageUri\n    countries(sort: {by: name, order: asc}) {\n      code\n      name\n      locationPageUri\n      displayName\n      states {\n        name\n        locationPageUri\n      }\n    }\n  }\n}",
    "operationName": "regions",
    "variables": {
        "language": "en"
    }
}

countries = []
all_hotels = []

with open('hilton_hotels.json', 'r') as f:
    all_hotels = json.load(f)

region_data = fetch_graphql_data(region_url, region_query)['data']

for country in region_data['na'][0]['countries']:
    hotel_region = region_data['na'][0]['name']
    hotel_country = country['name']
    print(country['locationPageUri'])
    for state in country['states']:
        hotel_state = state['name']
        state_uri = state['locationPageUri']
        print(f"{hotel_state}, {hotel_country}, {hotel_region}: {state['locationPageUri']}")
        countries.append({
            'name': hotel_state,
            'uri': state_uri
        })
    # for city in country['cities']:
    #     hotel_city = city['name']
    #     print(f"{hotel_city}, {hotel_country}, {hotel_region}: {city['locationPageUri']}")

# for region in region_data['others']:
#     hotel_region = region['name']
#     region_uri = region['locationPageUri']

#     for country in region['countries']:
#         hotel_country = country['name']
#         country_uri = country['locationPageUri']
#         print(f"{hotel_country}, {hotel_region}: {country_uri}")
#         countries.append({
#             'name': hotel_country,
#             'uri': country_uri
#         })

# countries.append({
#     'name': 'Malaysia',
#     'uri': 'locations/malaysia/'
# })

counter = 0
num_countries = len(countries)

for country in countries:
    counter += 1
    print(f"Processing #{counter}/{num_countries}: hotels from {country['name']}")
    
    if counter < 39:
        continue

    country_data = fetch_hotel_data(country['uri'])

    if 'hotelSummaryOptions' in country_data and country_data['hotelSummaryOptions'] is not None:
        num_hotels = len(country_data['hotelSummaryOptions']['hotels'])
    else:
        print(f"No hotels in {country['name']}, moving on!")
        continue

    if num_hotels < 150:
        hotels = country_data['hotelSummaryOptions']['hotels']
        all_hotels.extend(process_hotels(hotels))
    else:
        for city in country_data['location']['pageInterlinks'][0]['links']:
            print(f"Processing hotels from {city['name']}")
            city_data = fetch_hotel_data(city['uri'])
            if 'hotelSummaryOptions' in city_data and city_data['hotelSummaryOptions'] is not None:
                num_hotels = len(city_data['hotelSummaryOptions']['hotels'])
                # print(num_hotels)
                if num_hotels < 150:
                    hotels = city_data['hotelSummaryOptions']['hotels']
                    all_hotels.extend(process_hotels(hotels))
                else:
                    raise ValueError(f"{city['name']} has more than 150 hotels! Please take a look.")
            else:
                print(f"No hotels in {city['name']}, moving on!")
                continue
    with open('hilton_hotels.json', 'w') as f:
        json.dump(all_hotels, f, indent=4)

# pprint(fetch_hotel_data('locations/usa/canopy-by-hilton/'),indent=4)