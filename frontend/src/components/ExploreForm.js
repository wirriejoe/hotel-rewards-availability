import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import Select from 'react-select';
import Cookies from 'js-cookie';

function ExploreForm({ setStays, isLoading, setIsLoading }) {
    const [awardCategory, setAwardCategory] = useState([{ value: '7', label: '7' }, { value: '8', label: '8' }]);
    const [awardCategoryOptions, setAwardCategoryOptions] = useState([]);
    const [brand, setBrand] = useState([{ value: 'Park Hyatt', label: 'Park Hyatt' }]);
    const [brandOptions, setBrandOptions] = useState([]);
    const [errorMessage, setErrorMessage] = useState(null);

    const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'

    // Fetch award categories and brands on component mount
    useEffect(() => {
        Promise.all([
            axios.get(api_url + '/api/award_categories'),
            axios.get(api_url + '/api/brands')
        ])
        .then(([categoriesRes, brandsRes]) => {
            setAwardCategoryOptions([...categoriesRes.data.sort().map(category => ({ value: category, label: category }))]);
            setBrandOptions(brandsRes.data.sort().map(brand => ({ value: brand, label: brand })));
        })
        .catch(err => {
            console.log(err.message);
            console.log(err.request);
            console.log(err.response);
        });
    }, [api_url]);

    const sortSelectedOptions = (selectedOptions, options) => {
        return selectedOptions.sort((a, b) => {
            return options.indexOf(a) - options.indexOf(b);
        });
    };

    const handleAwardCategoryChange = (selectedOptions) => {
        const sortedOptions = sortSelectedOptions(selectedOptions, awardCategoryOptions);
        setAwardCategory(sortedOptions);
    };

    const handleBrandChange = (selectedOptions) => {
        const sortedOptions = sortSelectedOptions(selectedOptions, brandOptions);
        setBrand(sortedOptions);
    };

    const submitForm = async (e) => {
        e.preventDefault();

        // Validation
        if (awardCategory.length < 1 || brand.length < 1 || awardCategory.length > 3 || brand.length > 3) {
            setErrorMessage('Please select at least one brand and one category, and no more than three options per category.');
            return;
        }

        setIsLoading(true);
        setErrorMessage(null);  // Clear any previous error message

        const awardCategoryArray = Array.isArray(awardCategory) ? awardCategory : [awardCategory];
        const brandArray = Array.isArray(brand) ? brand : [brand];

        const awardCategoryString = awardCategoryArray.map(category => category.value);
        const brandString = brandArray.map(brand => brand.value);

        const session_token = Cookies.get('session_token')

        try {
            const response = await axios.post(api_url + '/api/explore', {
                award_category: awardCategoryString,
                brand: brandString,
                session_token: session_token
            });
            setStays(response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={submitForm} className="form-group">
            <div className="row">
                <div className="col-md-4">
                    <label>Award Category:</label>
                    <Select
                        options={awardCategoryOptions} 
                        value={awardCategory}
                        onChange={handleAwardCategoryChange}
                        isMulti
                    />
                </div>
                <div className="col-md-4">
                    <label>Brand:</label>
                    <Select
                        options={brandOptions} 
                        value={brand}
                        onChange={handleBrandChange}
                        isMulti
                    />
                </div>
                <div className="col-md-4 d-flex align-items-end">
                    <button type="submit" className="btn btn-primary w-100" disabled={isLoading}>
                        {isLoading ? 'Loading...' : 'Explore'}
                    </button>
                </div>
            </div>
            {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
        </form>
    );      
}

export default ExploreForm;