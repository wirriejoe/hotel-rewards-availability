import React, { useState, useEffect, useRef } from 'react';
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

function ExploreForm({ setStays, isLoading, setIsLoading }) {
    const [awardCategory, setAwardCategory] = useState([{ value: '7', label: '7' }, { value: '8', label: '8' }]);
    const [awardCategoryOptions, setAwardCategoryOptions] = useState([]);
    const [brand, setBrand] = useState([{ value: 'Park Hyatt', label: 'Park Hyatt' }]);
    const [brandOptions, setBrandOptions] = useState([]);
    const [errorMessage, setErrorMessage] = useState(null);

    const prevAwardCategory = useRef(awardCategory);
    const prevBrand = useRef(brand);

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

    const handleMenuClose = () => {
        const submitForm = async () => {
            // Validation
            if (awardCategory.length < 1 || brand.length < 1 || awardCategory.length > 3 || brand.length > 3) {
                setErrorMessage('Please select at least one brand and one category, and no more than three options per category.');
                return;
            }

            // Check if the values have changed
            if (JSON.stringify(prevAwardCategory.current) === JSON.stringify(awardCategory) && JSON.stringify(prevBrand.current) === JSON.stringify(brand)) {
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

        if (awardCategory.length > 0 && brand.length > 0) {
            submitForm();
        }

        // Update the previous values
        prevAwardCategory.current = awardCategory;
        prevBrand.current = brand;
    };

    return (
        <div className="form-group">
            {isLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                    <h4>Loading...</h4>
                </div>
            ) : (
                <>
                    <div className="row">
                        <div className="col-md-6">
                            <label>Award Category:</label>
                            <Select
                                options={awardCategoryOptions} 
                                value={awardCategory}
                                onChange={handleAwardCategoryChange}
                                onMenuClose={handleMenuClose}
                                isMulti
                                closeMenuOnSelect={false}
                                hideSelectedOptions={false}
                                components={{ Option }}
                                maxMenuHeight={150}  // Adjust this value to your liking
                            />
                        </div>
                        <div className="col-md-6">
                            <label>Brand:</label>
                            <Select
                                options={brandOptions} 
                                value={brand}
                                onChange={handleBrandChange}
                                onMenuClose={handleMenuClose}
                                isMulti
                                closeMenuOnSelect={false}
                                hideSelectedOptions={false}
                                components={{ Option }}
                                maxMenuHeight={150}  // Adjust this value to your liking
                            />
                        </div>
                    </div>
                    {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
                </>
            )}
        </div>
    );      
}

export default ExploreForm;