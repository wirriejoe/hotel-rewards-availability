import React, { useState, useEffect, useContext } from "react";
import { useParams } from 'react-router-dom'; 
import axios from 'axios';
import HotelForm from "./HotelForm";
import ExploreTable from "./ExporeTable";
import { UserContext } from './UserContext';

function HotelPage() {
    const [stays, setStays] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const {hotelCode} = useParams();
    const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'
    const [hotelDetails, setHotelDetails] = useState(null); // Add this state
    const { isCustomer } = useContext(UserContext);

    const handleStaysUpdate = (newData) => {
      setStays(newData);
      setIsLoading(false);
    };

    useEffect(() => {
      const fetchData = async () => {
          try {
              const response = await axios.get(api_url + '/api/hotel_details/' + hotelCode);
              setHotelDetails(response.data);
          } catch (err) {
              console.log(err.message);
          }
      }
      fetchData();
    }, [api_url, hotelCode]);  // Include initialLoad in the dependencies.  )
    
    return (
      <div>
        {isLoading ? (
          <div></div>
        ) : (
          <div>
            <div className="header">
              <h2>Exploring {hotelDetails ? hotelDetails['hotel_name'] : ''}</h2>
              <h6>📅 Tracking availabilities until {hotelDetails ? hotelDetails['pro_request'] ? new Date(new Date().setDate(new Date().getDate() + 360)).toISOString().split('T')[0] + " (360 days)": new Date(new Date().setDate(new Date().getDate() + 60)).toISOString().split('T')[0] + " (60 days). Request Full Calendar tracking " : ''}{hotelDetails ? hotelDetails['pro_request'] ? '' : <a href="https://burnmypoints.com/request">here</a> : ''}.</h6>
              <h6 style={{ whiteSpace: "pre" }}>{hotelDetails ? hotelDetails['pro_request'] ? "✅ One Night Stays    ✅ Multi-Night Stays " : "✅ One Night Stays    ❌ Multi-Night Stays " : ''}</h6>
              <div style={{
                height: "200px", 
                overflow: "hidden", 
                display: "flex", 
                alignItems: "center"
              }}>
                <img 
                  src={hotelDetails ? hotelDetails['image'] : ''} 
                  alt={hotelDetails ? hotelDetails['hotel_name'] : ''} 
                  style={{
                    objectFit: "cover",
                    minHeight: "100%",
                    minWidth: "100%",
                    position: "relative",
                    left: "50%",
                    transform: "translateX(-50%)"
                  }}
                />
              </div>
            </div>
            <div className="form-container">
              <HotelForm setStays={handleStaysUpdate} isLoading={isLoading} setIsLoading={setIsLoading} isCustomer = {isCustomer} />
            </div>
            <div className="table-container">
              <ExploreTable stays={stays} />
            </div>
          </div>
        )}
      </div>
    );
  }

export default HotelPage;