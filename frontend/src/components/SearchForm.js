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

function SearchForm({ setStays, isLoading, setIsLoading }) {
    const today = new Date();
    const thirtyDaysLater = new Date(today);
    thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 30);

    const rateFilterOptions = [
        { value: 'Standard', label: 'Standard' },
        { value: 'Premium', label: 'Premium' }
    ];
    
    const rateFilterDefaultOptions = [
        { value: 'Standard', label: 'Standard' },
        // { value: 'Premium', label: 'Premium' }
    ];

    const [startDate, setStartDate] = useState(formatDate(today));
    const [endDate, setEndDate] = useState(formatDate(thirtyDaysLater));
    const [lengthOfStay, setLengthOfStay] = useState(3);
    // const [hotel, setHotel] = useState('');
    const [city, setCity] = useState([{ value: 'New York', label: 'New York' }]);
    const [country, setCountry] = useState([{ value: 'United States', label: 'United States' }]);
    // const [region, setRegion] = useState([{ value: 'North America', label: 'North America' }]);
    const [category, setCategory] = useState('');
    const [rateFilter, setRateFilter] = useState(rateFilterDefaultOptions);
    const [pointsBudget, setPointsBudget] = useState(0);
    
    // const [hotelOptions, setHotelOptions] = useState([]);
    const [cityOptions, setCityOptions] = useState([]);
    const [countryOptions, setCountryOptions] = useState([]);
    // const [regionOptions, setRegionOptions] = useState([]);
    const [categoryOptions, setCategoryOptions] = useState([]);

    // Fetch hotel names, cities, and countries on component mount
    useEffect(() => {
        Promise.all([
            // axios.get('https://hotel-rewards-availability-api.onrender.com/api/hotels'),
            axios.get('https://hotel-rewards-availability-api.onrender.com/api/cities'),
            axios.get('https://hotel-rewards-availability-api.onrender.com/api/countries'),
            // axios.get('https://hotel-rewards-availability-api.onrender.com/api/regions'),
            axios.get('https://hotel-rewards-availability-api.onrender.com/api/award_categories')
        ])
        // .then(([hotelsRes, citiesRes, countriesRes, regionsRes, categoriesRes]) => {
        .then(([citiesRes, countriesRes, categoriesRes]) => {

            // setHotelOptions(hotelsRes.data.sort().map(hotel => ({ value: hotel, label: hotel })));
            setCityOptions(citiesRes.data.sort().map(city => ({ value: city, label: city })));
            setCountryOptions(countriesRes.data.sort().map(country => ({ value: country, label: country })));
            // setRegionOptions(regionsRes.data.sort().map(region => ({ value: region, label: region })));
            setCategoryOptions(categoriesRes.data.sort().map(category => ({ value: category, label: category })));
        })
        .catch(err => {
            console.log(err.message);
            console.log(err.request);
            console.log(err.response);
        });
    }, []);

    
    const submitForm = async (e) => {
        e.preventDefault();
        // setIsLoading(true);
        // const hotelArray = Array.isArray(hotel) ? hotel : [hotel];
        const cityArray = Array.isArray(city) ? city : [city];
        const countryArray = Array.isArray(country) ? country : [country];
        // const regionArray = Array.isArray(region) ? region : [region];
        const categoryArray = Array.isArray(category) ? category : [category];

        // const hotelString = hotelArray.map(h => h.value);
        const cityString = cityArray.map(c => c.value);
        const countryString = countryArray.map(c => c.value);
        // const regionString = regionArray.map(r => r.value);
        const categoryString = categoryArray.map(ca => ca.value);
        const rateFilterString = rateFilter.map(rf => rf.value).join(',').trim(',');

        const session_token = Cookies.get('session_token')
    
        console.log({
            startDate,
            endDate,
            lengthOfStay,
            // hotelString,
            cityString,
            countryString,
            // regionString,
            categoryString,
            rateFilterString,
            pointsBudget
        });
        try {
            const response = await axios.post('https://hotel-rewards-availability-api.onrender.com/api/consecutive_stays', {
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
            setStays(response.data);
        } catch (error) {
            console.error(error);
            setIsLoading(false);  // Make sure to set loading false in case of error
        }
    };

    return (
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
                {/* <div className="col">
                    <label>Hotel:</label>
                    <Select isMulti options={hotelOptions} onChange={setHotel} />
                </div> */}
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
                {/* <div className="col">
                    <label>Region:</label>
                    <Select
                        isMulti 
                        options={regionOptions} 
                        value={region} 
                        onChange={setRegion}
                    />
                </div> */}
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
    );
}

export default SearchForm;