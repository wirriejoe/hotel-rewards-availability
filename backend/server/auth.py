from selenium_profiles.webdriver import Chrome
from selenium_profiles.profiles import profiles
from selenium.webdriver import ChromeOptions
from retry import retry
import json
import random
import time
from dotenv import load_dotenv, find_dotenv
import os
import re

# Will be useful for refreshing auth tokens using selenium https://gist.github.com/rengler33/f8b9d3f26a518c08a414f6f86109863c

load_dotenv(find_dotenv())

def extract_cacheId(query_str):
    pattern = r'"cacheId":"([^"]+)"'
    matches = re.findall(pattern, query_str)
    return matches[-1] if matches else None

@retry(tries=5, delay=2)
def get_hilton_auth(check_in_date, check_out_date, hotel_code):
    print("Getting new auth!")
    selection = random.choice([1,2,3])
    if selection == 1:
        profile = json.loads(os.getenv('SELENIUM_PROFILE'))
    elif selection == 2:
        profile = json.loads(os.getenv('SELENIUM_PROFILE_2'))
    else:
        profile = profiles.Android()

    username = os.getenv('BRIGHTDATA_USERNAME')
    password = os.getenv('BRIHTDATA_PASSWORD')
    port = 22225
    session_id = random.random()
    super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"

    profile["proxy"] = {
        "proxy": super_proxy_url
    }

    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-images")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = Chrome(profile=profile, options=options,uc_driver=False,injector_options=True, seleniumwire_options=True)
    driver.execute_cdp_cmd('Runtime.disable',{})
    injector = driver.profiles.injector

    url = f"https://www.hilton.com/en/book/reservation/rooms/?ctyhocn={hotel_code}&arrivalDate={check_in_date}&departureDate={check_out_date}&redeemPts=true&room1NumAdults=2"

    driver.get(url)
    time.sleep(random.randint(1,2))

    logs = driver.get_log("performance")
    cacheId = None
    auth_token = None

    for entry in logs:
        if "cacheId" in str(entry["message"]):
            auth_message_data = json.loads(str(entry["message"]))
            query = auth_message_data['message']["params"]["request"]["postData"]
            cacheId = extract_cacheId(query)
            auth_token = auth_message_data['message']['params']['request']['headers']['Authorization']
            print(f"CacheId: {cacheId}")
            print(f"Auth Token: {auth_token}")
            break

    if cacheId and auth_token:
        driver.quit()
        return cacheId, auth_token

    driver.quit()
    raise Exception("Failed to get cacheId and auth_token")

@retry(tries=5, delay=2)
def get_ihg_auth(check_in_date, check_out_date):
    print("Getting new auth!")
    selection = random.choice([1,2,3])
    if selection == 1:
        profile = json.loads(os.getenv('SELENIUM_PROFILE'))
    elif selection == 2:
        profile = json.loads(os.getenv('SELENIUM_PROFILE_2'))
    else:
        profile = profiles.Android()

    username = os.getenv('BRIGHTDATA_USERNAME')
    password = os.getenv('BRIHTDATA_PASSWORD')
    port = 22225
    session_id = random.random()
    super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"

    profile["proxy"] = {
        "proxy": super_proxy_url
    }

    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-images")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = Chrome(profile=profile, options=options,uc_driver=False,injector_options=True, seleniumwire_options=True)
    driver.execute_cdp_cmd('Runtime.disable',{})
    injector = driver.profiles.injector

    check_in_month = "{:02d}".format(int(check_in_date.month) - 1)
    check_out_month = "{:02d}".format(int(check_out_date.month) - 1)


    # Open target URL
    url = f"https://www.ihg.com/hotels/us/en/find-hotels/hotel-search?qDest=San%20Francisco,%20CA,%20United%20States&qCiD={check_in_date.day}&qCiMy={check_in_month + str(check_in_date.year)}&qCoD={check_out_date.day}&qCoMy={check_out_month+str(check_out_date.year)}"
    driver.get(url)
    time.sleep(random.randint(0,1))

    # Parse performance logs to find X-Ihg-Api-Key
    logs = driver.get_log("performance")
    api_key = None

    for request in driver.requests:
        if 'https://apis.ihg.com/hotels/v1/profiles/' in request.url:
            api_key = request.response.headers.get('X-Ihg-Api-Key')
            if api_key:
                print(f"Found API Key: {api_key}")
                driver.quit()
                return api_key

    driver.quit()
    raise Exception("Failed to get X-Ihg-Api-Key")