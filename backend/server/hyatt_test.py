import requests
from requests.exceptions import RequestException
import os
from dotenv import load_dotenv, find_dotenv
import random
import json

load_dotenv(find_dotenv())

username = os.getenv('BRIGHTDATA_USERNAME')
password = os.getenv('BRIHTDATA_PASSWORD')
port = 22225
session_id = random.random()
super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"

proxy_dict = {
    "http": super_proxy_url,
    "https": super_proxy_url
}

x_kpsdk_ct = '0CrlKJ9IXty90UV83cy2YWDdw81DbehJuCz26E8AFwtI8FNtGryTxmustCnhuO92HoyD0RIRhyIKBf2ifKnV8xxgS8YlGCBHvIGCg1uItEiZdgh3mnkyyHNFYhLOVxbYbyvRKagS3R7tFWoie4wyx2u2cIrqC;'
url = "https://www.hyatt.com/shop/service/rooms/roomrates/sfojd"

json_query = {
    "spiritCode": "sfojd",
    "rooms": "1",
    "adults": "1",
    "location": "San Francisco, California, United States",
    "checkinDate": "2023-09-24",
    "checkoutDate": "2023-09-25",
    "kids": "0",
    "rate": "Standard",
}

# request = "016bdrQ7qE32DX4qrKBGxJKqURJ8Gnvl1SMyoxYZbmUpJlHGOxkfHjT6KecxCdiGsayC0trnhZKXhfJTkiGxSN9hWAgJ019E9oNDflKS7cuWe2RJIDZPozpPkCfShKHBSLntMSqMQqYQoJzjJqfQv03kewVXWJ"
# response = "0RgonE2zl9aVpg4y67ShuaUuyS02DnCjN6Ht72gGkuna49NeXDLELLpQ7qGtEKmJXJuNyO5X60qDW8a3KaGDjnLdG43oDqzRBQsFmjeomhxbynms2bh3tJlMlAiCYP9ArgrAdjW3dnQUe7MmYwGcov4I2TaDI"

cookies = {
    # "source-country": "US",
    # "mb_locale": "en-US",
    # "_csrf": "2VAp3uWWjifm0R5U2gcMt8-q",
    # "rate_filter": "woh",
    # "_aff_booking_abs": "d6fca4e1442ec888",
    # "vrid": "rBEAAmUQkl+4fQEYP7h4Ag==",
    # "check": "true",
    # "cnry-hf1l5dj2aY": "6579be2e461b2bed",
    # "AMCVS_D7B27FF452128BAA0A490D4C@AdobeOrg": "1",
    # "s_ecid": "MCMID%7C61378060746824337373569340939400079306",
    # "AMCV_D7B27FF452128BAA0A490D4C@AdobeOrg": "-330454231%7CMCIDTS%7C19625%7CMCMID%7C61378060746824337373569340939400079306%7CMCAAMLH-1696189665%7C9%7CMCAAMB-1696189665%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1695592065s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-19632%7CvVersion%7C3.1.2",
    # "mboxEdgeCluster": "35",
    # "rand_1to3": "3",
    # "fs_sampling": "s",
    # "rndn": "20",
    # "newvisit": "true",
    # "email_90_10": "test",
    # "_cs_mk_aa": "0.8880321840757279_1695584866108",
    # "s_p26": "en-US",
    # "cm_dl": "1",
    # "c_m": "Typed%2FBookmarkedTyped%2FBookmarkedundefined",
    # "s_cc": "true",
    # "AAMC_hyatt_0": "REGION%7C9",
    # "aam_uuid": "66786339594052754674038110959450672712",
    # "_cs_c": "0",
    # "_cs_id": "da4d7277-1680-a3a3-fdc8-9e76ef8be13a.1695584866.1.1695584866.1695584866.1.1729748866482",
    # "_gcl_au": "1.1.1990360396.1695584866",
    # "s_cmch": "%5B%5B%27typed%2Fbookmarked%27%2C%271695584866585%27%5D%5D",
    # "s_cmkw": "%5B%5B%27n%2Fa%27%2C%271695584866585%27%5D%5D",
    # "s_advcs": "%5B%5B%27typed%2Fbookmarked%27%2C%271695584866585%27%5D%5D",
    # "_fbp": "fb.1.1695584866713.134817475",
    # "_cs_s": "1.0.1.1695586667233",
    # "OptanonConsent": "isGpcEnabled=0&datestamp=Sun+Sep+24+2023+12%3A47%3A56+GMT-0700+(Pacific+Daylight+Time)&version=202302.1.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0004%3A1%2CC0005%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1&AwaitingReconsent=false",
    # "utag_main": "v_id:018ac8bbcec4001761ce09dd7e6f0507500ed06d00fb8$_sn:1$_se:3$_ss:0$_st:1695586676881$ses_id:1695584865989%3Bexp-session$_pn:2%3Bexp-session$vapi_domain:hyatt.com$dc_visit:1$dc_event:2%3Bexp-session$dc_region:us-west-2%3Bexp-session",
    # "scPrevPage": "Resv:Flow1:Corp:Rooms:DailyRoomDisplay",
    # "tkrm_alpekz_s1.3-ssn": x_kpsdk_ct,
    "tkrm_alpekz_s1.3": x_kpsdk_ct,
    # "mbox": "session#47d3c23aa34a464495d69d05d6c46602#1695595737|PC#47d3c23aa34a464495d69d05d6c46602.35_0#1758838677"
}


# X-Kpsdk-Ct: 0yk35hTEHrdJX8pDU4lsVPdEHRRJUjVPBQq1ghfo8CmWXZbMsgNHoIwIY5OKwQBm2h3n4i6kAA1LO4QGKhAtZBCSMRzYUWcL7DMQ5BVSRI2tQFkGFmNur24mvroWdeRAsUnY5n6sZuooKcMzeH4Kzuxu4wJQP
# X-Kpsdk-Dt: 1448y35x72x2ey0tgz6by58z1o0
# X-Kpsdk-Im: CiQzMjUyNzliMy1jZWEwLTRjNjMtOWQyMy1iODFhMDZlOTUyNzk

# X-Kpsdk-Ct: 0YCxyOdpXyCAKKKWFCTyMg9osFv4cYWUkQBxsoML15IUNSWsNqxJemgWoXHL3IJAOQSyoAfIU9oL3q6S1FEDzp9D2vgpDXuvXHjVd1L5sjqUWcWN0zvB5fYqSo4NabxB67soYjpoHdqqpya3lwiLBYRf6IMhN (changes)
# X-Kpsdk-Dt: 16az2dy72y13bpx449z03h8z35x57 (changes)
# X-Kpsdk-Im: CiQ1MzE3YTMzOS04OTkzLTQ4NDYtYWZmZi00MmU1ZTkzMTczNzk (does not change)


# Request Cookie: 0ECQdhvOAVhaAew75xUXIeX6nr0tJ4oYX1FdYuKBEJFxRMwxFbNJLgjHmjKDt6h9v7RE8WZOX7YorL0r3ZmNHMOqCicZYB8oCw43Dvgeiv7DEBeC1opEK3rdV4ZSJH4uKudwjIVsl22ImaseIsuCD7tulkMEz
# Response Cookie: 0GR3bCoZg4TYWGOS5qwfJpHUTf42Of5CAOvP9vDgCgZsnURrCChZiCbdgfYAihaUjfl9CfjzI77P6TABgc2nHLaMZ9fDaHoqxuzfveAwKpP9GCaz2LSUE58pPWj5Y63sMdoXEgBj82z9eBopULg6ytab2nXFL




# https://www.hyatt.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/ips.js?
# tkrm_alpekz_s1.3=010T3HXVpqLqmkJHE8GWmPIYXec3sCNYJ0zTfjz004BIhRI9msNVTBMfwWoBLXp6yUKbeswZPO59mrbYRi1aqxgl5Z4LCNEuTvmAYGmJflBQH72fUusVbDZjE3o5OgfWAlWBjFWg33ymj3ou7aGIwCkD2DErGy&
# x-kpsdk-im=CiQ1MzE3YTMzOS04OTkzLTQ4NDYtYWZmZi00MmU1ZTkzMTczNzk










# url = 'https://mboxedge35.tt.omtrdc.net/m2/hyattcorporation/mbox/json'

# body = {
#     "mbox": "target-global-mbox",
#     "mboxSession": "8d6d028dac96481681720438f8662abe",
#     "mboxPC": "8d6d028dac96481681720438f8662abe.35_0",
#     "mboxPage": "ccaa823490cb42a4b7b3d2e5e59100ec",
#     "mboxRid": "ca2bda41759242869b3dedd1490f0bf0",
#     "mboxVersion": "1.7.1",
#     "mboxCount": 1,
#     "mboxTime": 1695567836980,
#     "mboxHost": "www.hyatt.com",
#     "mboxURL": "https://www.hyatt.com/shop/rooms/sfojd?rooms=1&adults=1&location=San+Francisco%2C+California%2C+United+States&checkinDate=2023-09-27&checkoutDate=2023-09-28&kids=0&rate=Standard&hpesrId=ps__LQ8tsBwMU1_uRRauIralJ5HAuavc1s1B&rateFilter=woh",
#     "mboxReferrer": "https://www.hyatt.com/shop/rooms/sfojd?rooms=1&adults=1&location=San+Francisco%2C+California%2C+United+States&checkinDate=2023-09-27&checkoutDate=2023-09-28&kids=0&rate=Standard&hpesrId=ps__LQ8tsBwMU1_uRRauIralJ5HAuavc1s1B&rateFilter=woh",
#     "mboxXDomain": "enabled",
#     "browserHeight": 1330,
#     "browserWidth": 775,
#     "browserTimeOffset": -420,
#     "screenHeight": 1440,
#     "screenWidth": 2560,
#     "colorDepth": 24,
#     "devicePixelRatio": 1,
#     "screenOrientation": "landscape",
#     "webGLRenderer": "ANGLE (Apple, Apple M2, OpenGL 4.1)",
#     "pagedata": {
#         "locale": "en-US",
#         "page_url": "/shop/rooms/sfojd?rooms=1&adults=1&location=San+Francisco%2C+California%2C+United+States&checkinDate=2023-09-27&checkoutDate=2023-09-28&kids=0&rate=Standard&hpesrId=ps__LQ8tsBwMU1_uRRauIralJ5HAuavc1s1B&rateFilter=woh",
#         "site_id": "hyhyattcom",
#         "page_type": "room_types",
#         "sc_page_title": "Resv:Flow1:Corp:Rooms:DailyRoomDisplay",
#         "product_category": "hotel",
#         "event_string": "scOpen,event1",
#         "rearch_flag": 'true',
#         "full_page_test_group": "roomsratesredesign_test_group",
#         "hotel_spirit_code": "sfojd",
#         "hotel_name": "Hotel Kabuki",
#         "hotel_brand": "JdV by Hyatt",
#         "hotel_city": "San Francisco",
#         "hotel_country": "United States",
#         "hotel_country_code": "US",
#         "hotel_postal_code": "94115",
#         "hotel_state": "California",
#         "number_of_adults": 1,
#         "number_of_children": 0,
#         "number_of_travelers": 1,
#         "number_of_rooms": 1,
#         "search_term": "San Francisco, California, United States",
#         "special_rate": "Standard",
#         "accessibility_check": 'false',
#         "qb_use_points": "woh",
#         "date_checkin": "2023-09-27",
#         "date_checkout": "2023-09-28",
#         "number_of_nights": 1,
#         "gp_login_status": "Logged-out"
#     },
#     "at_property": "d2047a9b-ddbd-2127-113c-74d074037708",
#     "entity": {
#         "id": "prop_sfojd",
#         "category": "Property",
#         "brand": "JdV by Hyatt"
#     },
#     "mboxMCSDID": "0B27731321CC1DE9-51734EF17E4AED59",
#     "vst.trk": "o8.hyatt.com",
#     "vst.trks": "so8.hyatt.com",
#     "mboxMCGVID": "78988653485526501653819554763198937534",
#     "mboxAAMB": "6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y",
#     "mboxMCGLH": 9
# }
# data = json.dumps(body).encode('utf-8')

headers = {
    # "X-Kpsdk-Ct": "0OeIB19c5O2Ia2goqASJn9cRpRcWI4pjqDK4X5ISLjliFEhTRiUqs1u7maZ9HVyLNzMKjdxM0eq3HsSEzTwOR9xCxIo80CoyvzCE0hTQukgACarDUQ32XoMggmXvWs56kzGBQFgUS4nvxuXKlnP7paW3q0ckv",
    # "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

try:
    # Send the GET request
    response = requests.get(url, params=json_query, headers=headers, cookies=cookies)
    # response = requests.post(url, data=data, headers=headers)
    response_headers = response.headers
    print(response_headers)
    # Check for a successful request
    if response.status_code == 200:
        # Parse and process JSON response
        data = response.json()
        print(len(data))
        # print(data)
    else:
        print(f"Failed to get data. Status Code: {response.status_code}")
except RequestException as e:
    print(f"An error occurred: {e}")