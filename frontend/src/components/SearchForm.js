import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import Select from 'react-select';
import Cookies from 'js-cookie';

// Function to format the date to 'yyyy-mm-dd' format
function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

function SearchForm({ setStays, isLoading, setIsLoading, isCustomer }) {
    const tomorrow = new Date(); //new Date() returns today's date
    const thirtyDaysLater = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1)
    thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 31);
    const [error, setError] = useState('');

    const rateFilterOptions = [
        { value: 'Standard', label: 'Standard' },
        { value: 'Premium', label: 'Premium' }
    ];
    const rateFilterDefaultOptions = [
        { value: 'Standard', label: 'Standard' },
    ];
    const [startDate, setStartDate] = useState(formatDate(tomorrow));
    const [endDate, setEndDate] = useState(formatDate(thirtyDaysLater));
    const [lengthOfStay, setLengthOfStay] = useState(3);
    const [city, setCity] = useState([{ value: 'New York', label: 'New York' }]);
    const [country, setCountry] = useState([{ value: 'United States', label: 'United States' }]);
    const [category, setCategory] = useState('');
    const [rateFilter, setRateFilter] = useState(rateFilterDefaultOptions);
    const [pointsBudget, setPointsBudget] = useState(0);
    const [cityOptions, setCityOptions] = useState([]);
    const [countryOptions, setCountryOptions] = useState([]);
    const [categoryOptions, setCategoryOptions] = useState([]);

    const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'

    // Fetch hotel names, cities, and countries on component mount
    useEffect(() => {
        Promise.all([
            axios.get(api_url + '/api/cities'),
            axios.get(api_url + '/api/countries'),
            axios.get(api_url + '/api/award_categories')
        ])
        .then(([citiesRes, countriesRes, categoriesRes]) => {
            setCityOptions(citiesRes.data.sort().map(city => ({ value: city, label: city })));
            setCountryOptions(countriesRes.data.sort().map(country => ({ value: country, label: country })));
            setCategoryOptions(categoriesRes.data.sort().map(category => ({ value: category, label: category })));
        })
        .catch(err => {
            console.log(err.message);
            console.log(err.request);
            console.log(err.response);
        });
    }, [api_url]);

    const submitForm = async (e) => {
        e.preventDefault();

        const sixtyDaysFromNow = new Date();
        sixtyDaysFromNow.setDate(sixtyDaysFromNow.getDate() + 60);
    
        console.log("Sixty days from now: ", sixtyDaysFromNow);
        console.log("Selected start date: ", new Date(startDate));
        console.log("Selected end date: ", new Date(endDate));
        
        if (!isCustomer && (
          new Date(startDate) > sixtyDaysFromNow || new Date(endDate) > sixtyDaysFromNow
        )) {
          console.log("Condition met, setting error");
          setStays([])
          setError("You can only search for stays up to 60 days out on the Free plan. Upgrade to the Pro plan to access 360 days of availabilities.");
          return;
        }
    
        setIsLoading(true);
        const cityArray = Array.isArray(city) ? city : [city];
        const countryArray = Array.isArray(country) ? country : [country];
        const categoryArray = Array.isArray(category) ? category : [category];
        const cityString = cityArray.map(c => c.value);
        const countryString = countryArray.map(c => c.value);
        const categoryString = categoryArray.map(ca => ca.value);
        const rateFilterString = rateFilter.map(rf => rf.value).join(',').trim(',');

        const session_token = Cookies.get('session_token')
    
        try {
            const response = await axios.post(api_url + '/api/consecutive_stays', {
                startDate,
                endDate,
                lengthOfStay,
                hotel: '',
                city: cityString,
                country: countryString,
                region: '',
                category: categoryString,
                rateFilter: rateFilterString,
                pointsBudget: pointsBudget,
                session_token: session_token
            });
            setError()
            setStays(response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);  // Always set loading to false at the end
        }
    };

    return (
        <>
            {/* <p>Start Date: {startDate}</p>
            <p>End Date: {endDate}</p>
            <p>Is Customer: {isCustomer.toString()}</p> */}
            {error && <p className="error">
                {error}{" "}
                <a href="https://buy.stripe.com/6oE8xe4ps4ly7fy4gi" target="_blank" rel="noreferrer">
                    Upgrade here.
                </a>
            </p>}
            <form onSubmit={submitForm} className="form-group">
                <div className="row">
                    <div className="col">
                        <label>Start Date:</label>
                        <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="form-control"/>
                    </div>
                    <div className="col">
                        <label>End Date:</label>
                        <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="form-control"/>
                    </div>
                    <div className="col">
                        <label>Number of Nights:</label>
                        <input type="number" value={lengthOfStay} onChange={(e) => setLengthOfStay(e.target.value)} className="form-control"/>
                    </div>
                    <div className="col">
                        <label>Max Points per Night:</label>
                        <input type="number" value={pointsBudget} onChange={(e) => setPointsBudget(e.target.value)} className="form-control"/>
                    </div>
                </div>
                <div className="row">
                    <div className="col">
                        <label>City:</label>
                        <Select
                            isMulti
                            options={cityOptions}
                            value={city}
                            onChange={setCity}
                        />
                    </div>
                    <div className="col">
                        <label>Country:</label>
                        <Select
                            isMulti 
                            options={countryOptions} 
                            value={country} 
                            onChange={setCountry}
                        />
                    </div>
                    <div className="col">
                        <label>Rate:</label>
                        <Select 
                            isMulti 
                            options={rateFilterOptions} 
                            value={rateFilter}
                            onChange={setRateFilter} 
                        />
                    </div>
                    <div className="col">
                        <label>Category:</label>
                        <Select
                            isMulti 
                            options={categoryOptions} 
                            value={category} 
                            onChange={setCategory}
                        />
                    </div>
                </div>
                <button type="search" className="btn btn-primary mt-3" disabled={isLoading}>
                    {isLoading ? 'Loading...' : 'Search'}
                </button>
            </form>
        </>
    );
}

export default SearchForm;