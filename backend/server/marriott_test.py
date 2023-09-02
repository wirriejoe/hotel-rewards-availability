import requests
import json

# URL and query parameters
url = "https://marriottinternationa.tt.omtrdc.net/rest/v1/delivery"
params = {
    "client": "marriottinternationa",
    "sessionId": "c1d89ebd03f44cd091d7ad1bbfd1002b",
    "version": "2.5.0"
}

# JSON payload from your example
payload = {
    "requestId": "01e37c8c78c044e4a0819de15c0f00e8",
    "context": {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "timeOffsetInMinutes": -420,
        "channel": "web",
        "screen": {
            "width": 1440,
            "height": 900,
            "orientation": "landscape",
            "colorDepth": 30,
            "pixelRatio": 2
        },
        "window": {
            "width": 540,
            "height": 707
        },
        "browser": {
            "host": "www.marriott.com",
            "webGLRenderer": "ANGLE (Apple, Apple M2, OpenGL 4.1)"
        },
        "address": {
            "url": "https://www.marriott.com/reservation/rateListMenu.mi",
            "referringUrl": "https://www.marriott.com/reservation/rateListMenu.mi?defaultTab=standard&showFullPrice=true"
        }
    },
    "id": {
        "tntId": "794c1f7a007c40fca79f6bde42d7f6de.35_0",
        "marketingCloudVisitorId": "15153202086354645364527837472746698931"
    },
    "property": {
        "token": "c72849c6-2a3c-8a3b-bf17-94885baf8879"
    },
    "experienceCloud": {
        "audienceManager": {
            "locationHint": 9,
            "blob": "RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y"
        },
        "analytics": {
            "logging": "server_side",
            "supplementalDataId": "5636450B26146DDA-2A2FFF6A3AABB9E3"
        }
    },
    "execute": {
        "pageLoad": {
            "parameters": {
                "rpcCode": "0513,0513,",
                "offerCode": "ACQ_FNA_3,ACQ_EG250_50k,",
                "page_type": "www.marriott.com/reservation/rateListMenu.mi",
                "env_is_prod": "true",
                "env_site_id": "US",
                "prop_is_ers": "false",
                "env_platform": "ram-prod",
                "daysToCheckin": 0,
                "firstTimeUser": "isGpcEnabled=0&datestamp=Thu+Aug+31+2023+13:04:40+GMT-0700+(Pacific+Daylight+Time)&version=6.26.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=1:1,3:1,4:0,6:0&geolocation=NL;NH&AwaitingReconsent=false",
                "prop_brand_code": "JW",
                "prop_brand_tier": "Luxury",
                "daysSinceJoining": "",
                "mvpOffers_source": "MAPA-1A",
                "prop_marsha_code": "FRAJW",
                "cookie_merchViewed": "hpHero-RViewed|hp4P2-mbop0822|hp4P3-vacationsByMarriott0822|hp4P4-hertz0822|hpPopOffersCard1-globalpromo082923|availabilityCalendarFooterBanner-unlockYourStay1120|rlmFooterBanner-unlockYourStay1120|",
                "prop_currency_type": "EUR",
                "search_cluster_code": "MW1",
                "search_date_check_in": "09/01/2023",
                "page_url_query_string": "%page_url_query_string_&_patch%",
                "prop_address_lat_long": "50.115324,8.680378643",
                "search_date_check_out": "09/02/2023",
                "prop_address_country_abbr": "DE",
                "miRecentlyViewedProperties": "true|true|MC|FRAJW",
                "mr_prof_authentication_state": "unauthenticated",
                "search_advance_purchase_days": "1",
                "search_is_rewards_redemption": "true",
                "prop_address_city_state_country": "Frankfurt|null|DE",
                "search_google_places_destination": "",
                "mr_prof_upcoming_stay_consolidated": ""
            }
        }
    },
    "prefetch": {
        "views": [
            {
                "parameters": {
                    "rpcCode": "0513,0513,",
                    "offerCode": "ACQ_FNA_3,ACQ_EG250_50k,",
                    "page_type": "www.marriott.com/reservation/rateListMenu.mi",
                    "env_is_prod": "true",
                    "env_site_id": "US",
                    "prop_is_ers": "false",
                    "env_platform": "ram-prod",
                    "daysToCheckin": 0,
                    "firstTimeUser": "isGpcEnabled=0&datestamp=Thu+Aug+31+2023+13:04:40+GMT-0700+(Pacific+Daylight+Time)&version=6.26.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=1:1,3:1,4:0,6:0&geolocation=NL;NH&AwaitingReconsent=false",
                    "prop_brand_code": "JW",
                    "prop_brand_tier": "Luxury",
                    "daysSinceJoining": "",
                    "mvpOffers_source": "MAPA-1A",
                    "prop_marsha_code": "FRAJW",
                    "cookie_merchViewed": "hpHero-RViewed|hp4P2-mbop0822|hp4P3-vacationsByMarriott0822|hp4P4-hertz0822|hpPopOffersCard1-globalpromo082923|availabilityCalendarFooterBanner-unlockYourStay1120|rlmFooterBanner-unlockYourStay1120|",
                    "prop_currency_type": "EUR",
                    "search_cluster_code": "MW1",
                    "search_date_check_in": "09/01/2023",
                    "page_url_query_string": "%page_url_query_string_&_patch%",
                    "prop_address_lat_long": "50.115324,8.680378643",
                    "search_date_check_out": "09/02/2023",
                    "prop_address_country_abbr": "DE",
                    "miRecentlyViewedProperties": "true|true|MC|FRAJW",
                    "mr_prof_authentication_state": "unauthenticated",
                    "search_advance_purchase_days": "1",
                    "search_is_rewards_redemption": "true",
                    "prop_address_city_state_country": "Frankfurt|null|DE",
                    "search_google_places_destination": "",
                    "mr_prof_upcoming_stay_consolidated": ""
                }
            }
        ]
    }
}

# POST request
response = requests.post(url, params=params, json=payload)

# Response handling
if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Failed:", response.status_code)
