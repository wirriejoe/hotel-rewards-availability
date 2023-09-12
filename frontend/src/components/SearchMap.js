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

  useEffect(() => {
    $(function() {
      $('#date-range').daterangepicker({
        startDate: moment().startOf('hour').add(24, 'hour'),
        endDate: moment().startOf('hour').add(7, 'day'),
        locale: {
          format: 'MM/DD/YYYY'
        }
      }, function(start, end) {
        console.log("Start date: ", start.format('MM/DD/YYYY'));
        console.log("End date: ", end.format('MM/DD/YYYY'));
      });
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
  }, [lng, lat, zoom, stays]);

  const submitForm = async () => {
    const dateRange = document.getElementById('date-range').value;
    const numNights = document.getElementById('length-of-stay').value;
    const awardCategory = document.getElementById('category').value;

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
      console.log(response.data);

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