import json
import random
from dotenv import load_dotenv, find_dotenv
import os
import traceback
import time
import random
from selenium_profiles.webdriver import Chrome
from selenium_profiles.profiles import profiles
from selenium.webdriver.common.by import By  # locate elements
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # for parsing HTML

class AwardSearch:
    @staticmethod
    def initialize_driver():
        # Load Selenium profile
        load_dotenv(find_dotenv())
        # profile = json.loads(os.getenv('SELENIUM_PROFILE'))
        selection = random.choice([1,2,3])
        print(selection)
        if selection == 1:
            profile = json.loads(os.getenv('SELENIUM_PROFILE'))
        elif selection == 2:
            profile = json.loads(os.getenv('SELENIUM_PROFILE_2'))
        else:
            profile = profiles.Android()
        print(profile)

        # username = 'brd-customer-hl_94decac0-zone-isp'
        # password = 'fgezgl3cvg66'
        username = os.getenv('BRIGHTDATA_USERNAME')
        password = os.getenv('BRIHTDATA_PASSWORD')
        port = 22225
        session_id = random.random()
        super_proxy_url = f"http://{username}-dns-remote-route_err-block-session-{session_id}:{password}@brd.superproxy.io:{port}"
        
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--proxy-server={super_proxy_url}")
        driver = Chrome(profile=profile, options=options,uc_driver=False,injector_options=True, seleniumwire_options=True)
        driver.execute_cdp_cmd('Runtime.disable',{})
        injector = driver.profiles.injector

        return driver

    def __init__(self):
        self.driver = self.initialize_driver()

    def build_url(self, hotel_brand, hotel_code, checkin_date, checkout_date, room_qty = 1, adults = 2, kids = 0):
        base_url_dict = {
            'Hyatt': 'https://www.hyatt.com/shop/service/rooms/roomrates/'
        }
        search_base_url_dict = {
            'Hyatt': 'https://www.hyatt.com/shop/rooms/'
        }
        base_url = base_url_dict[hotel_brand] + hotel_code
        search_base_url = search_base_url_dict[hotel_brand] + hotel_code
        response_url = base_url + f'?spiritCode={hotel_code}&rooms={room_qty}&adults={adults}&checkinDate={checkin_date}&checkoutDate={checkout_date}&kids={kids}'
        search_url = search_base_url + f'?checkinDate={checkin_date}&checkoutDate={checkout_date}&rateFilter=woh'
        print("Response URL: " + response_url)
        print("Verification URL: " + search_url)
        return response_url, search_url

    def get_award_stays(self, hotel_brand, hotel_code, checkin_date, checkout_date, room_qty = 1, adults = 2, kids = 0):
        max_retries = 5
        delay = 1
        backoff_factor = 2
        for attempt in range(max_retries):
            try:
                url, search_url = self.build_url(hotel_brand, hotel_code, checkin_date, checkout_date, room_qty, adults, kids)

                # Get award stays
                # self.driver.implicitly_wait(5)
                self.driver.get(url)
                # wait = WebDriverWait(self.driver, 20)
                time.sleep(random.randint(2, 3))
                # pre_element = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'pre')))

                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                pre_element_text = soup.find('pre').text

                json_data = json.loads(pre_element_text)

                room_rates = json_data.get('roomRates', {})  # Using get to avoid KeyError
                awards_list = []

                for room, room_data in room_rates.items():
                    if room_data.get('lowestPointValue') is not None:  # Using get to avoid KeyError
                        room_details = {
                            "Room Name": room,
                            "Room Type Code": room_data.get('roomTypeCode'),
                            "Room Category": room_data.get('roomCategory'),
                            "Room Quantity": room_data.get('roomQuantity'),
                            "Lowest Point Value": room_data.get('lowestPointValue'),
                            "Lowest Public Rate": room_data.get('lowestPublicRate'),
                            "Currency Code": room_data.get('currencyCode'),
                            "Search URL": search_url
                        }
                        awards_list.append(room_details)
                
                return awards_list
            except Exception as e:
                print(f"An error occurred while getting award stays: {e}. Attempt {attempt + 1} of {max_retries}")
                traceback.print_exc()
                if attempt < max_retries - 1:
                    sleep_time = delay * (backoff_factor ** attempt)
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)  # Wait before retrying
            
        print("Max retries reached. Returning an empty list.")
        return []  # Return empty list after max retries

    def quit(self):
        self.driver.quit()