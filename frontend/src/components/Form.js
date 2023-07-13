import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import Select from 'react-select';

const rateFilterOptions = [
    { value: 'Standard', label: 'Standard' },
    { value: 'Premium', label: 'Premium' }
];

const rateFilterDefaultOptions = [
    { value: 'Standard', label: 'Standard' },
    { value: 'Premium', label: 'Premium' }
];

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

function Form({ setStays }) {
    const today = new Date();
    const thirtyDaysLater = new Date(today);
    thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 30);

    const [startDate, setStartDate] = useState(formatDate(today));
    const [endDate, setEndDate] = useState(formatDate(thirtyDaysLater));
    const [lengthOfStay, setLengthOfStay] = useState(3);
    const [hotel, setHotel] = useState('');
    const [city, setCity] = useState('');
    const [country, setCountry] = useState('');
    const [rateFilter, setRateFilter] = useState(rateFilterDefaultOptions);
    const [pointsBudget, setPointsBudget] = useState(0);
    
    const hotelOptions = [];
    const cityOptions = [];
    const countryOptions = [];    

    // Fetch hotel names, cities, and countries on component mount
    useEffect(() => {
        axios.get('http://localhost:3000/api/hotels')
            .then(res => {
                const sortedHotels = res.data.sort();
                sortedHotels.forEach(hotel => {
                    hotelOptions.push({ value: hotel, label: hotel });
                });
            })
            .catch(err => console.log(err));
    
        axios.get('http://localhost:3000/api/cities')
            .then(res => {
                const sortedCities = res.data.sort();
                sortedCities.forEach(city => {
                    cityOptions.push({ value: city, label: city });
                });
            })
            .catch(err => console.log(err));
    
        axios.get('http://localhost:3000/api/countries')
            .then(res => {
                const sortedCountries = res.data.sort();
                sortedCountries.forEach(country => {
                    countryOptions.push({ value: country, label: country });
                });
            })
            .catch(err => console.log(err));
    }, []);
    
    const submitForm = async (e) => {
        e.preventDefault();
        const hotelArray = Array.isArray(hotel) ? hotel : [hotel];
        const cityArray = Array.isArray(city) ? city : [city];
        const countryArray = Array.isArray(country) ? country : [country];    

        const hotelString = hotelArray.map(h => h.value);
        const cityString = cityArray.map(c => c.value);
        const countryString = countryArray.map(c => c.value);
        const rateFilterString = rateFilter.map(rf => rf.value).join(',').trim(',');
    
        console.log({
            startDate,
            endDate,
            lengthOfStay,
            hotelString,
            cityString,
            countryString,
            rateFilterString,
            pointsBudget
        });
        const response = await axios.post('http://localhost:3000/api/consecutive_stays', {
            startDate,
            endDate,
            lengthOfStay,
            hotel: hotelString,
            city: cityString,
            country: countryString,
            rateFilter: rateFilterString,
            pointsBudget
        });
        setStays(response.data);
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
                    <label>Rate:</label>
                    <Select 
                        isMulti 
                        options={rateFilterOptions} 
                        value={rateFilter}
                        onChange={setRateFilter} 
                    />
                </div>
            </div>
            <div className="row">
                <div className="col">
                    <label>Max Points per Night:</label>
                    <input type="number" value={pointsBudget} onChange={(e) => setPointsBudget(e.target.value)} className="form-control"/>
                </div>
                <div className="col">
                    <label>Hotel:</label>
                    <Select isMulti options={hotelOptions} onChange={setHotel} />
                </div>
                <div className="col">
                    <label>City:</label>
                    <Select isMulti options={cityOptions} onChange={setCity} />
                </div>
                <div className="col">
                    <label>Country:</label>
                    <Select isMulti options={countryOptions} onChange={setCountry} />
                </div>
            </div>
            <button type="search" className="btn btn-primary mt-3">Search</button>
        </form>
    );
}

export default Form;