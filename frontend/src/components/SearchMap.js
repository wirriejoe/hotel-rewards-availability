import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxGeocoder from '@mapbox/mapbox-gl-geocoder';
import '@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-daterangepicker/daterangepicker.css'; // Import the daterangepicker CSS
import $ from 'jquery';
import 'bootstrap-daterangepicker'; // Import the daterangepicker JS
import moment from 'moment';
import axios from 'axios';
import Cookies from 'js-cookie';

// Set Mapbox API token
mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_API_KEY;
// eslint-disable-next-line import/no-webpack-loader-syntax
mapboxgl.workerClass = require("worker-loader!mapbox-gl/dist/mapbox-gl-csp-worker").default;

const SearchMap = ({stays, setStays, isLoading, setIsLoading, isCustomer}) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const geocoder = useRef(null);
  const geocoderContainer = useRef(null); // New ref for geocoder container
  const lng = -122.4194;
  const lat = 37.7749;
  const zoom = 12;
  const session_token = Cookies.get('session_token')
  const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'
  const [geography, setGeography] = useState({ lat: lat, lng: lng });
  const [startDate, setStartDate] = useState(moment().startOf('hour').add(24, 'hour'));
  const [endDate, setEndDate] = useState(moment().startOf('hour').add(7, 'day'));

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const urlLat = parseFloat(searchParams.get('lat'));
    const urlLng = parseFloat(searchParams.get('lng'));
    const urlStartDate = searchParams.get('startDate');
    const urlEndDate = searchParams.get('endDate');
    const urlNumNights = parseInt(searchParams.get('numNights'), 10);
    const urlAwardCategory = searchParams.get('awardCategory');

    if (urlLat && urlLng) {
      setGeography({ lat: urlLat, lng: urlLng });
    }

    if (urlStartDate && urlEndDate) {
      setStartDate(moment(urlStartDate, 'MM-DD-YYYY'));
      setEndDate(moment(urlEndDate, 'MM-DD-YYYY'));
    }
    
    if (urlNumNights) {
      document.getElementById('length-of-stay').value = urlNumNights;
    }

    if (urlAwardCategory) {
      document.getElementById('category').value = urlAwardCategory;
    }

    $('#date-range').daterangepicker({
      startDate: startDate,  // Use state
      endDate: endDate,      // Use state
      locale: {
        format: 'MM/DD/YYYY'
      }
    }, function(start, end) {
      // Update state when date range changes
      setStartDate(start);
      setEndDate(end);
    });
  
    if (!map.current) {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/streets-v12',
        center: [lng, lat],
        zoom: zoom,
        attributionControl: false,
      });

      geocoder.current = new MapboxGeocoder({
        accessToken: mapboxgl.accessToken,
        mapboxgl: mapboxgl,
        marker: false,
      });  
    
      // Listen to 'result' events on geocoder
      geocoder.current.on('result', (event) => {
        setGeography({
          lat: event.result.geometry.coordinates[1],
          lng: event.result.geometry.coordinates[0]
        });      
        map.current.jumpTo({
          center: [event.result.geometry.coordinates[0], event.result.geometry.coordinates[1]],
          zoom: 10
        });
      });
    
      // Append geocoder to its container
      geocoderContainer.current.appendChild(geocoder.current.onAdd(map.current));
    }

    if (map.current) {
      // If _markers array already exists, remove all previous markers
      if (map.current._markers) {
        map.current._markers.forEach(marker => marker.remove());
      }
      
      // Initialize an empty array for new markers
      map.current._markers = [];    
  
      // Loop through stays data to create markers
      stays.forEach(row => {
        const url = `/${row.hotel_brand}/hotel/${row.hotel_code}`;
        const popupHTML = `
          <div>
            <a href="${url}" target="_blank"><b>${row.hotel_name}</b></a>
            <br />
            <span><b>Standard rate: </b>${row.standard_rate}</span>
            <br />
            <span><b>Premium rate: </b>${row.premium_rate}</span>
            <br />
            <span><b>Standard cash rate: </b>$${row.standard_cash_usd}</span>
            <br />
            <span><b>Premium cash rate: </b>$${row.premium_cash_usd}</span>
          </div>
        `;
      
        const popup = new mapboxgl.Popup({ offset: 25 }) // add popups
          .setHTML(popupHTML);
      
        const marker = new mapboxgl.Marker()
          .setLngLat([row.hotel_longitude, row.hotel_latitude])
          .setPopup(popup) // sets a popup on this marker
          .addTo(map.current);
      
        // Add marker to _markers array
        map.current._markers.push(marker);
      });
    }  
  }, [lng, lat, zoom, stays, startDate, endDate]);

  const submitForm = async () => {
    const dateRange = document.getElementById('date-range').value;
    const numNights = document.getElementById('length-of-stay').value;
    const awardCategory = document.getElementById('category').value;
    const dateRangePicker = $('#date-range').data('daterangepicker');
    setStartDate(dateRangePicker.startDate);
    setEndDate(dateRangePicker.endDate);  

    // Add form values to URL as query parameters
    const params = new URLSearchParams();
    if (geography.lat && geography.lng) {
      params.append('lat', geography.lat);
      params.append('lng', geography.lng);
    }
    const formattedStartDate = startDate.format('MM-DD-YYYY');
    const formattedEndDate = endDate.format('MM-DD-YYYY');
    if (formattedStartDate) {
      params.append('startDate', formattedStartDate);
    }
    if (formattedEndDate) {
      params.append('endDate', formattedEndDate);
    }
    if (numNights) {
      params.append('numNights', numNights);
    }
    if (awardCategory) {
      params.append('awardCategory', awardCategory);
    }  
    window.history.replaceState({}, '', `?${params.toString()}`);

    setIsLoading(true);

    try {
      const response = await axios.post(api_url + '/api/search', {
        geography,
        dateRange,
        numNights,
        awardCategory,
        session_token,
        isCustomer
      });
      setStays(response.data);
    } catch (error) {
      console.error('There was a problem with the axios operation:', error);
    }
    setIsLoading(false);
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center w-100">
        <div ref={geocoderContainer} />
        <input
          type="text"
          id="date-range"
          className="form-control mapboxgl-ctrl-geocoder mx-2"
          value={`${startDate.format('MM/DD/YYYY')} - ${endDate.format('MM/DD/YYYY')}`}  // Use state
        />
        <select
          id="length-of-stay"
          className="form-control mapboxgl-ctrl-geocoder mx-2"
        >
          <option value="1">1 night</option>
          <option value="2">2 nights</option>
          <option value="3">3 nights</option>
          <option value="4">4 nights</option>
          <option value="5">5 nights</option>
        </select>
        <select
          id="category"
          className="form-control mapboxgl-ctrl-geocoder mx-2"
          defaultValue="Any room"
        >
          <option value="">Any room</option>
          <option value="STANDARD">Standard</option>
          <option value="PREMIUM">Premium/Suite</option>
        </select>
        <div style={{ marginBottom: '35px', alignSelf: 'center' }}> 
          <button
            type="search"
            className="btn btn-primary mt-3 mx-2"  // Keeping your existing classes
            onClick={submitForm}
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Search'}
          </button>
        </div>
      </div>
      <div ref={mapContainer} className="map-container" />
    </div>
  );
};

export default SearchMap;