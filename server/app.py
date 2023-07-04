from flask import Flask, request, jsonify, render_template
from search_stays import search_by_consecutive_nights
from pyairtable import Table
from dotenv import load_dotenv
import os
import logging

load_dotenv()

app = Flask(__name__, static_folder='../static', template_folder='../templates')

stays_table = Table(base_id=os.getenv('AIRTABLE_BASE'), table_name='Stays', api_key=os.getenv('AIRTABLE_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/api/consecutive_stays', methods=['POST'])
def consecutive_stays():
    data = request.json

    start_date = data['startDate']
    end_date = data['endDate']
    length_of_stay = int(data['lengthOfStay'])
    hotel_name_text = data.get('hotel')  # These are optional, so use .get() to return None if they are not present
    hotel_city = data.get('city')
    hotel_country = data.get('country')
    rate_filter = data.get('rateFilter')
    app.logger.info(data.get('pointsBudget'))
    max_points_budget = int(data.get('pointsBudget'))

    stays = search_by_consecutive_nights(start_date, end_date, length_of_stay, hotel_name_text, hotel_city, hotel_country, rate_filter, max_points_budget)
    return jsonify(stays)  # Convert list of stays to JSON

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    # current_app.logger.info(f"Received data: {data}")  # logging incoming data

    # Build the filter formula
    filter_formula = f"AND( \
        or(check_in_date >= '{data['startDate']}','{data['startDate']}'=blank()), \
        or(check_in_date < '{data['endDate']}', '{data['endDate']}'=blank()), \
        find('{data['hotel']}', hotel_name_text), \
        or(find('{data['city']}', hotel_city),'{data['city']}'=blank()), \
        or(standard_rate > 0, premium_rate > 0) \
    )"
    
    # current_app.logger.info(f"Filter formula: {filter_formula}")  # logging generated formula

    records = stays_table.all(formula=filter_formula)
    # current_app.logger.info(f"Retrieved records: {records}")  # logging retrieved records

    # Format records to match your table structure
    formatted_records = [
        {
            'Date': rec['fields'].get('check_in_date'),
            'Last Checked': rec['fields'].get('last_checked'),
            'Hotel': rec['fields'].get('hotel_name_text'),
            'City': rec['fields'].get('hotel_city'),
            'Country': rec['fields'].get('hotel_country'),
            'Standard': rec['fields'].get('standard_rate'),
            'Premium': rec['fields'].get('premium_rate')
        } 
        for rec in records
    ]
    # current_app.logger.info(f"Formatted records: {formatted_records}")  # logging formatted records
    return jsonify(formatted_records)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=3000)