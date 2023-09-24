import sys
import eventlet
from eventlet.green.urllib import request, error
import random
import socket
from helpers import queue_stays, upsert, update_rates, send_error_to_slack
import os
import json
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, MetaData, select, and_, join
from sqlalchemy.orm import sessionmaker
import time
import traceback

class SingleSessionRetriever:
    url = "http://%s-route_err-pass_dyn-session-%s:%s@brd.superproxy.io:%d"
    port = 22225

    def __init__(self, username, password, requests_limit, failures_limit):
        self._username = username
        self._password = password
        self._requests_limit = requests_limit
        self._failures_limit = failures_limit
        print(f"Initializing SingleSessionRetriever with username: {username}, password: {password}, requests_limit: {requests_limit}, failures_limit: {failures_limit}")
        self._reset_session()

    def _reset_session(self):
        session_id = random.random()
        print(f"New session ID: {session_id}")
        proxy = self.url % (self._username, session_id, self._password, self.port)
        proxy_handler = request.ProxyHandler({'http': proxy, 'https': proxy})
        self._opener = request.build_opener(proxy_handler)
        self._requests = 0
        self._failures = 0

    def retrieve(self, url, headers, json_query, timeout):
        while True:
            if self._requests == self._requests_limit:
                print("Reached request limit. Resetting session.")
                self._reset_session()
            self._requests += 1
            try:
                timer = eventlet.Timeout(timeout)
                headers['Content-Type'] = 'application/json'
                json_data = json.dumps(json_query).encode('utf-8')
                req = request.Request(url, headers=headers, data=json_data, method='POST')
                response = self._opener.open(req)                
                status_code = response.getcode()
                print(f"Received HTTP Status Code: {status_code}.")
                result = response.read()
                timer.cancel()
                print(f"Retrieved {len(result)} bytes from {url}")
                return result
            except error.HTTPError as e:
                timer.cancel()
                if e.code == 400:
                    print(f"Received HTTP Status Code: {e.code}. No availabilities for this stay.")
                    return {}
                else:
                    print(f"Received HTTP Status Code: {e.code}. Got an error, triggering retry.")
                    self._failures += 1
            except Exception as e:
                timer.cancel()
                self._failures += 1
                print(f"An exception occurred while trying to open the URL: {str(e)}")
                # traceback.print_exc()
                print(f"Failure #{self._failures}.")
                if self._failures == self._failures_limit:
                    print("Reached failure limit. Resetting session.")
                    self._reset_session()

class MultiSessionRetriever:
    def __init__(self, username, password, session_requests_limit, session_failures_limit):
        self._username = username
        self._password = password
        self._sessions_stack = []
        self._session_requests_limit = session_requests_limit
        self._session_failures_limit = session_failures_limit
        # print(f"Initializing MultiSessionRetriever with username: {username}, password: {password}, session_requests_limit: {session_requests_limit}, session_failures_limit: {session_failures_limit}")

    # Updated retrieve method to work with list of lists containing [url, headers, json_query]
    def retrieve(self, url_data_list, timeout, parallel_sessions_limit, callback):
        pool = eventlet.GreenPool(parallel_sessions_limit)
        print(f"Starting to retrieve {len(url_data_list)} URLs")
        for url, body in pool.imap(lambda url_data: self._retrieve_single(url_data, timeout), url_data_list):
            callback(url, body)

    # Updated _retrieve_single to work with list containing [url, headers, json_query]
    def _retrieve_single(self, url_data, timeout):
        # print(url_data)
        url = url_data['url']
        headers = url_data['headers']
        json_query = url_data['query']
        # print(url)
        # print(headers)
        # print(json_query)
        # time.sleep(10)
        if self._sessions_stack:
            session = self._sessions_stack.pop()
        else:
            session = SingleSessionRetriever(self._username, self._password, self._session_requests_limit, self._session_failures_limit)
        body = session.retrieve(url, headers, json_query, timeout)
        self._sessions_stack.append(session)
        return url, body

def output(url, body):
    print(len(body))
    return body

# load_dotenv(find_dotenv())

# check_in_date = '2023-09-28'
# check_out_date = '2023-09-29'
# hotel_code = 'SINIC'
# username = os.getenv('BRIGHTDATA_USERNAME')
# password = os.getenv('BRIHTDATA_PASSWORD')

# requests = []

# url = "https://apis.ihg.com/availability/v3/hotels/offers?fieldset=rateDetails"            
# headers = {
#     'Content-Type': "application/json",
#     # 'X-Ihg-Api-Key': auths[rand_auth]['api_key']
#     'X-Ihg-Api-Key': "se9ym5iAzaW8pxfBjkmgbuGjJcr3Pj6Y"
# }
# query = {"products": [{
#             "productCode": "SR",
#             "guestCounts": [
#                 {"otaCode": "AQC10",
#                 "count": 2},
#                 {"otaCode": "AQC8",
#                 "count": 0}],
#             "startDate": check_in_date,
#             "endDate": check_out_date,
#             "quantity": 1}],
#     "startDate": check_in_date,
#     "endDate": check_out_date,
#     "hotelMnemonics": [hotel_code],
#     "rates": {"ratePlanCodes": [{"internal": "IVANI"}] # award program code = IVANI
#     },
#     "options": {"disabilityMode": "ACCESSIBLE_AND_NON_ACCESSIBLE",
#         "returnAdditionalRatePlanDescriptions": True,
#         "includePackageDetails": True}
# }
# requests.append({"url": url, "headers": headers, "query": query})
# print(requests)

# # session = SingleSessionRetriever(username, password, 10, 2)
# # session.retrieve(url, headers, query, 10)

# session = MultiSessionRetriever(username, password, 10, 2)
# session.retrieve(requests, 30, 1, output)