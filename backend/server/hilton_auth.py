from selenium_profiles.webdriver import Chrome
from selenium_profiles.profiles import profiles
from selenium.webdriver import ChromeOptions
import json
import random
import time
from dotenv import load_dotenv, find_dotenv
import os
import re
from bs4 import BeautifulSoup  # for parsing HTML

# Will be useful for refreshing auth tokens using selenium https://gist.github.com/rengler33/f8b9d3f26a518c08a414f6f86109863c

def extract_cacheId(query_str):
    pattern = r'"cacheId":"([^"]+)"'
    matches = re.findall(pattern, query_str)
    return matches[-1] if matches else None

def get_hilton_auth(check_in_date, check_out_date, hotel_code):
    load_dotenv(find_dotenv())
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
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = Chrome(profile=profile, options=options,uc_driver=False,injector_options=True, seleniumwire_options=True)
    driver.execute_cdp_cmd('Runtime.disable',{})
    injector = driver.profiles.injector

    url = f"https://www.hilton.com/en/book/reservation/rooms/?ctyhocn={hotel_code}&arrivalDate={check_in_date}&departureDate={check_out_date}&redeemPts=true&room1NumAdults=2"

    driver.get(url)

    # time.sleep(random.random()*2)
    # soup = BeautifulSoup(driver.page_source, 'html.parser')

    logs = driver.get_log("performance")

    driver.quit()

    for entry in logs:
        if "cacheId" in str(entry["message"]):
            auth_message_data = json.loads(str(entry["message"]))
            query = auth_message_data['message']["params"]["request"]["postData"]
            cacheId = extract_cacheId(query)
            auth_token = auth_message_data['message']['params']['request']['headers']['Authorization']
            return cacheId, auth_token
