import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom'; 
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import Select from 'react-select';
import queryString from 'query-string';

function usePrevious(value) {
    const ref = useRef();
    useEffect(() => {
        ref.current = value;
    });
    return ref.current;
}

function HotelForm({ initialLoad, setInitialLoad, setStays, isLoading, setIsLoading, isCustomer }) {
    const [errorMessage, setErrorMessage] = useState(null);
    const [pointsPerNight, setPointsPerNight] = useState(
        { value: '', label: 'Any points cost'}
    );
    const [weekend, setWeekend] = useState(
        { value: 'false', label: 'Any day'}
    );
    const [centsPerPoint, setCentsPerPoint] = useState(
        { value: '', label: 'Any ¢ per pt'}
    );
    const [numNights, setNumNights] = useState(
        { value: 1, label: '1 night'}
    );
    const pointsPerNightOptions = [
        { value: '', label: 'Any points cost' },
        { value: '5000', label: 'Under 5,000 points' },
        { value: '10000', label: 'Under 10,000 points' },
        { value: '20000', label: 'Under 20,000 points' },
        { value: '30000', label: 'Under 30,000 points' },
        { value: '40000', label: 'Under 40,000 points' },
        { value: '50000', label: 'Under 50,000 points' },
        { value: '60000', label: 'Under 60,000 points' },
        { value: '80000', label: 'Under 80,000 points' },
        { value: '100000', label: 'Under 100,000 points' },
    ];
    const weekendOptions = [
        { value: 'false', label: 'Any day' },
        { value: 'true', label: 'Weekend only' },
    ];
    const centsPerPointOptions = [
        { value: '', label: 'Any ¢ per pt' },
        { value: '0.0075', label: 'Over 0.75¢ per pt' },
        { value: '0.01', label: 'Over 1¢ per pt' },
        { value: '0.015', label: 'Over 1.5¢ per pt' },
        { value: '0.02', label: 'Over 2¢ per pt' },
        { value: '0.025', label: 'Over 2.5¢ per pt' },
        { value: '0.03', label: 'Over 3¢ per pt' },
        { value: '0.04', label: 'Over 4¢ per pt' },
        { value: '0.05', label: 'Over 5¢ per pt' },
        { value: '0.1', label: 'Over 10¢ per pt' },
    ]; 
    const numNightsOptions = [
        { value: '1', label: '1 night'},
        { value: '2', label: '2 nights'},
        { value: '3', label: '3 nights'},
        { value: '4', label: '4 nights'},
        { value: '5', label: '5 nights'},
    ]; 

    const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'

    const prevPointsPerNight = usePrevious(pointsPerNight);
    const prevWeekend = usePrevious(weekend);
    const prevCentsPerPoint = usePrevious(centsPerPoint);
    const prevNumNights = usePrevious(numNights);

    const {hotelName, hotelCode} = useParams(); // Get hotel name from URL

    const initializeFormFromURL = () => {
    //    console.log("Initialize Form loading")
        const parsed = queryString.parse(window.location.search);
        if (Object.keys(parsed).length > 0) {
            // Parse the parameters and set the state
            if (parsed.pointsPerNight) {
                setPointsPerNight({ value: parsed.pointsPerNight, label: `Under ${parsed.pointsPerNight} points` });
            }
            if (parsed.weekend) {
                const label = parsed.weekend === 'true' ? 'Weekend only' : 'Any day';
                setWeekend({ value: parsed.weekend, label: label });
            }
            if (parsed.cpp) {  // Assuming URL parameter for centsPerPoint is "cpp"
                setCentsPerPoint({ value: parsed.cpp, label: `Over ${parseFloat(parsed.cpp) * 100}¢ per pt` });
            }
            if (parsed.numNights) {
                setNumNights({ value: parsed.numNights, label: `${parsed.numNights} ${parsed.numNights > 1 ? 'nights' : 'night'}` })
            }       
        }
    }

    const submitForm = useCallback(async () => {
        setErrorMessage(null);  // Clear any previous error message

        const payload = {
            hotel_name: hotelName,
            hotel_code: hotelCode,
            num_nights: numNights.value,
            points_budget: pointsPerNight.value,
            is_weekend: weekend.value,
            cents_per_point: centsPerPoint.value,
            isCustomer: isCustomer
          };
        
        const queryObj = {
            pointsPerNight: pointsPerNight.value,
            weekend: weekend.value,
            cpp: centsPerPoint.value,
            numNights: numNights.value
        };

        if (!initialLoad) {  // Only push new state if it's not the initial load
            const filteredQueryObj = Object.fromEntries(Object.entries(queryObj).filter(([_, value]) => value && value.length > 0));
            // console.log('Filtered Query Object:', filteredQueryObj);
            const queryStr = queryString.stringify(filteredQueryObj);
            // console.log('Query String:', queryStr);
            window.history.replaceState({}, '', '?' + queryStr);
        }    
      
        try {
            const response = await axios.post(api_url + '/api/hotel', payload);
            setStays(response.data);
        } catch (error) {
            console.error(error);
        }
    }, [pointsPerNight, weekend, centsPerPoint, numNights, hotelName, hotelCode, isCustomer, setStays, api_url, initialLoad]);

    useEffect(() => {
        if (initialLoad) {
            initializeFormFromURL();
            setIsLoading(true);
            setInitialLoad(false);
            submitForm();
            setIsLoading(false)
        } else if (!initialLoad && !isLoading && (prevPointsPerNight !== pointsPerNight || prevWeekend !== weekend || prevCentsPerPoint !== centsPerPoint || prevNumNights !== numNights)) {
            setIsLoading(true);
            submitForm();
            setIsLoading(false);
        }
    }, [prevPointsPerNight, prevWeekend, prevCentsPerPoint, prevNumNights, pointsPerNight, weekend, centsPerPoint, numNights, submitForm, initialLoad, isLoading, setIsLoading, setInitialLoad]);

    const handlePointsPerNightChange = (selectedOption) => setPointsPerNight(selectedOption);
    const handleWeekendChange = (selectedOption) => setWeekend(selectedOption);
    const handleCentsPerPointChange = (selectedOption) => setCentsPerPoint(selectedOption);
    const handleNumNights = (selectedOption) => setNumNights(selectedOption);

    return (
        <div className="form-group">
                <div className="row">
                    <div className="col-md-3">
                        <label>Max Points per Night:</label>
                        <Select
                            options={pointsPerNightOptions} 
                            value={pointsPerNight}
                            onChange={handlePointsPerNightChange}
                            maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                            styles={{ menu: (provided) => ({ ...provided, zIndex: 10 }) }}  
                        />
                    </div>
                    <div className="col-md-3">
                        <label>Day of Week:</label>
                        <Select
                            options={weekendOptions} 
                            value={weekend}
                            onChange={handleWeekendChange}
                            styles={{ menu: (provided) => ({ ...provided, zIndex: 10 }) }}  
                        />
                    </div>
                    <div className="col-md-3">
                        <label>¢ per Point:</label>
                        <Select
                            options={centsPerPointOptions} 
                            value={centsPerPoint}
                            onChange={handleCentsPerPointChange}
                            maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                            styles={{ menu: (provided) => ({ ...provided, zIndex: 10 }) }}  
                        />
                    </div>
                    <div className="col-md-3">
                        <label>Number of nights:</label>
                        <Select
                            options={numNightsOptions} 
                            value={numNights}
                            onChange={handleNumNights}
                            maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                            styles={{ menu: (provided) => ({ ...provided, zIndex: 10 }) }}  
                        />
                    </div>
                </div>
                {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
        </div>
    );      
}

export default HotelForm;