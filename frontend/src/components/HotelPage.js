import React, { useState, useEffect, useContext } from "react";
import { useParams } from 'react-router-dom'; 
import axios from 'axios';
import HotelForm from "./HotelForm";
import ExploreTable from "./ExporeTable";
import { UserContext } from './UserContext';
import HotelCalendar from './HotelCalendar';

function HotelPage() {
    const [stays, setStays] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [initialLoad, setInitialLoad] = useState(true);
    const [view, setView] = useState("Calendar"); 
    const {hotelCode} = useParams();
    const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'
    const [hotelDetails, setHotelDetails] = useState(null); // Add this state
    const { isCustomer } = useContext(UserContext);

    const toggleStyles = {
      selected: {
        backgroundColor: '#800080',
        color: 'white',
        border: 'none',
        minWidth: '10vw',
        padding: '5px',
        borderRadius: '5px',
        marginRight: '-1px',
        fontWeight: 'bold'
      },
      unselected: {
        backgroundColor: '#e6e6f9',
        color: '#333333',
        border: 'none',
        minWidth: '10vw',
        padding: '5px',
        borderRadius: '5px',
        marginRight: '-1px',
        fontWeight: 'bold'
      }
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
    }, [api_url, hotelCode]);
    
    return (
      <div>
        {isLoading ? (
          <h4>Loading</h4>
        ) : (
          <div>
            <div className="header" >
              <div className="header-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                <h2 style={{alignItems: 'left'}}>Exploring {hotelDetails ? hotelDetails['hotel_name'] : ''}</h2>
                <div >
                  <button style={view === "Calendar" ? toggleStyles.selected : toggleStyles.unselected} onClick={() => setView("Calendar")}>
                    Calendar
                  </button>
                  <button style={view === "Table" ? toggleStyles.selected : toggleStyles.unselected} onClick={() => setView("Table")}>
                    Table
                  </button>
                </div>
              </div>
              <h6>📅 Tracking availabilities until {hotelDetails ? hotelDetails['pro_request'] ? new Date(new Date().setDate(new Date().getDate() + 360)).toISOString().split('T')[0] + " (360 days)": new Date(new Date().setDate(new Date().getDate() + 60)).toISOString().split('T')[0] + " (60 days). Request Full Calendar tracking " : ''}{hotelDetails ? hotelDetails['pro_request'] ? '' : <a href="https://burnmypoints.com/request">here</a> : ''}.</h6>
              <h6 style={{ whiteSpace: "pre" }}>{hotelDetails ? hotelDetails['pro_request'] ? "✅ One Night Stays    ✅ Multi-Night Stays " : "✅ One Night Stays    ❌ Multi-Night Stays " : ''}</h6>
              {/* <div style={{
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
              </div> */}
            </div>
            <div className="form-container">
              <HotelForm setStays={setStays} initialLoad={initialLoad} setInitialLoad={setInitialLoad} isLoading={isLoading} setIsLoading={setIsLoading} isCustomer = {isCustomer} />
            </div>
            <div className="content-container">
              {view === "Calendar" ? (
                <div className="calendar-container">
                  <HotelCalendar stays={stays} />
                </div>
              ) : (
                <div className="table-container">
                  <ExploreTable stays={stays} />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

export default HotelPage;