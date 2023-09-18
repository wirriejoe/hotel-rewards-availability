import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import Select, { components } from 'react-select';
import Cookies from 'js-cookie';

const Option = (props) => {
    return (
        <div>
            <components.Option {...props}>
                <input
                    type="checkbox"
                    checked={props.isSelected}
                    onChange={() => null}
                />{" "}
                <label>{props.label}</label>
            </components.Option>
        </div>
    );
};

function usePrevious(value) {
    const ref = useRef();
    useEffect(() => {
        ref.current = value;
    });
    return ref.current;
}

function ExploreForm({ setStays, isLoading, setIsLoading, isCustomer, hotelName }) {
    const [awardCategory, setAwardCategory] = useState([]);
    const [awardCategoryOptions, setAwardCategoryOptions] = useState([]);
    const [brand, setBrand] = useState([])
    const [brandInitialized, setBrandInitialized] = useState(false);
    useEffect(() => {
        setBrand([{
            value: hotelName === 'hyatt' ? 'Park Hyatt' : hotelName === 'hilton' ? 'Waldorf Astoria Hotels & Resorts' : hotelName === 'ihg' ? 'InterContinental Hotels & Resorts' : '',
            label: hotelName === 'hyatt' ? 'Park Hyatt' : hotelName === 'hilton' ? 'Waldorf Astoria Hotels & Resorts' : hotelName === 'ihg' ? 'InterContinental Hotels & Resorts' : ''
          }]);
          setBrandInitialized(true); 
      }, [hotelName]);
    const [brandOptions, setBrandOptions] = useState([]);
    // const [errorMessage, setErrorMessage] = useState(null);
    const [initialLoad, setInitialLoad] = useState(true);

    const [country, setCountry] = useState(
        { value: '', label: 'Any country'}
    );
    const [pointsPerNight, setPointsPerNight] = useState(
        { value: '', label: 'Any points cost'}
    );
    const [centsPerPoint, setCentsPerPoint] = useState(
        { value: '', label: 'Any ¢ per pt'}
    );

    const [numNights, setNumNights] = useState(
        { value: 1, label: '1 night'}
    );

    const [countryOptions, setCountryOptions] = useState([]);
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
        { value: 1, label: '1 night'},
        { value: 2, label: '2 nights'},
        { value: 3, label: '3 nights'},
        { value: 4, label: '4 nights'},
        { value: 5, label: '5 nights'},
    ]; 

    const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'

    const prevAwardCategory = usePrevious(awardCategory);
    const prevBrand = usePrevious(brand);
    const prevCountry = usePrevious(country);
    const prevPointsPerNight = usePrevious(pointsPerNight);
    const prevCentsPerPoint = usePrevious(centsPerPoint);
    const prevNumNights = usePrevious(numNights);
    const prevHotelName = usePrevious(hotelName)

    const submitForm = useCallback(async () => {
        // if ((awardCategory.length < 1 && brand == '') || awardCategory.length > 3 || brand.length > 3) {
        //     setErrorMessage('Please select at least one brand or one award category, and no more than three options per category.');
        //     return;
        // }
        // setErrorMessage(null);  // Clear any previous error message

        const awardCategoryArray = Array.isArray(awardCategory) ? awardCategory : [awardCategory];
        const brandArray = Array.isArray(brand) ? brand : [brand];

        const awardCategoryString = awardCategoryArray.map(category => category.value);
        const brandString = brandArray.map(brand => brand.value);

        const session_token = Cookies.get('session_token')

        try {
            const response = await axios.post(api_url + '/api/explore', {
                hotel: hotelName,
                award_category: awardCategoryString,
                brand: brandString,
                country: country.value,
                points_budget: pointsPerNight.value,
                cents_per_point: centsPerPoint.value,
                num_nights: numNights.value,
                session_token: session_token,
                isCustomer: isCustomer
            });
            setStays(response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }, [awardCategory, brand, country, pointsPerNight, centsPerPoint, numNights, setIsLoading, setStays, api_url, isCustomer, hotelName]);

    const fetchData = async () => {
        try {
            const [categoriesRes, brandsRes, countriesRes] = await Promise.all([
                axios.get(api_url + `/api/award_categories?hotel=${hotelName}`),
                axios.get(api_url + `/api/brands?hotel=${hotelName}`),
                axios.get(api_url + `/api/countries?hotel=${hotelName}`),
            ]);

            setAwardCategoryOptions([...categoriesRes.data.sort().map(category => ({ value: category, label: category }))]);
            setBrandOptions([
                { value: '', label: 'Any brand' },
                ...brandsRes.data.sort().map(brand => ({ value: brand, label: brand }))
              ]);
            setCountryOptions([
                { value: '', label: 'Any country' },
                ...countriesRes.data.sort().map(country => ({ value: country, label: country }))
              ]);
        } catch (err) {
            console.log(err.message);
            console.log(err.request);
            console.log(err.response);
        }
    }

    // Call submitForm whenever awardCategory or brand changes
    useEffect(() => {
        if (initialLoad && brandInitialized) {
            setIsLoading(true);
            fetchData();
            submitForm();
            setInitialLoad(false);
        }
        else if (!initialLoad && !isLoading && brandInitialized && (prevAwardCategory !== awardCategory || prevBrand !== brand || prevCountry !== country || prevPointsPerNight !== pointsPerNight || prevCentsPerPoint !== centsPerPoint || prevNumNights !== numNights || prevHotelName !== hotelName)) {
            setIsLoading(true);
            submitForm();
        }
    }, [prevAwardCategory, prevBrand, prevCountry, prevPointsPerNight, prevCentsPerPoint, prevNumNights, prevHotelName, awardCategory, brand, country, pointsPerNight, centsPerPoint, numNights, hotelName, submitForm, initialLoad]);  // Include previous and current states, and submitForm in the dependencies.

    const handleAwardCategoryChange = (selectedOptions) => {setAwardCategory(selectedOptions)};
    const handleBrandChange = (selectedOptions) => {setBrand(selectedOptions)};
    const handleCountryChange = (selectedOption) => setCountry(selectedOption);
    const handlePointsPerNightChange = (selectedOption) => setPointsPerNight(selectedOption);
    const handleCentsPerPointChange = (selectedOption) => setCentsPerPoint(selectedOption);
    const handleNumNightsChange = (selectedOption) => setNumNights(selectedOption);

    return (
        <div className="form-group">
            <div className="row">
                <div className="col-md-2">
                    <label>Number of nights:</label>
                    <Select
                        options={numNightsOptions} 
                        value={numNights}
                        onChange={handleNumNightsChange}
                        maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                    />
                </div>
                <div className="col-md-2">
                    <label>Brand:</label>
                    <Select
                        options={brandOptions} 
                        value={brand}
                        onChange={handleBrandChange}
                        // isMulti
                        // closeMenuOnSelect={false}
                        hideSelectedOptions={false}
                        // components={{ Option }}
                        maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                    />
                </div>
                {hotelName === "hyatt" && (
                    <div className="col-md-2">
                        <label>Award Category:</label>
                        <Select
                            options={awardCategoryOptions} 
                            value={awardCategory}
                            onChange={handleAwardCategoryChange}
                            isMulti
                            hideSelectedOptions={false}
                            components={{ Option }}
                            maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                        />
                    </div>
                )}
                <div className="col-md-2">
                    <label>Country:</label>
                    <Select
                        options={countryOptions} 
                        value={country}
                        onChange={handleCountryChange}
                        maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                    />
                </div>
                <div className="col-md-2">
                    <label>Max Points per Night:</label>
                    <Select
                        options={pointsPerNightOptions} 
                        value={pointsPerNight}
                        onChange={handlePointsPerNightChange}
                        maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                    />
                </div>
                {/* <div className="col-md-2">
                    <label>Day of Week:</label>
                    <Select
                        options={weekendOptions} 
                        value={weekend}
                        onChange={handleWeekendChange}
                    />
                </div> */}
                <div className="col-md-2">
                    <label>¢ per Point:</label>
                    <Select
                        options={centsPerPointOptions} 
                        value={centsPerPoint}
                        onChange={handleCentsPerPointChange}
                        maxMenuHeight={window.innerHeight * 0.3}  // Adjust this value to your liking
                    />
                </div>
            </div>
            {/* {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>} */}
        </div>
    );      
}

export default ExploreForm;