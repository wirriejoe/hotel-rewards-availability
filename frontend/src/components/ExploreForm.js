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

function ExploreForm({ setStays, isLoading, setIsLoading, isCustomer }) {
    const [awardCategory, setAwardCategory] = useState([
        { value: '7', label: '7' }, 
        { value: '8', label: '8' }
    ]);
    const [awardCategoryOptions, setAwardCategoryOptions] = useState([]);
    const [brand, setBrand] = useState([
        { value: 'Park Hyatt', label: 'Park Hyatt' }
    ]);
    const [brandOptions, setBrandOptions] = useState([]);
    const [errorMessage, setErrorMessage] = useState(null);
    const [initialLoad, setInitialLoad] = useState(true);

    const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'

    const prevAwardCategory = usePrevious(awardCategory);
    const prevBrand = usePrevious(brand);

    const submitForm = useCallback(async () => {
        if ((awardCategory.length < 1 && brand.length < 1) || awardCategory.length > 3 || brand.length > 3) {
            setErrorMessage('Please select at least one brand or one award category, and no more than three options per category.');
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
                session_token: session_token,
                isCustomer: isCustomer
            });
            setStays(response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }, [awardCategory, brand, setIsLoading, setStays, api_url, isCustomer]);

    // Fetch award categories and brands on component mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [categoriesRes, brandsRes] = await Promise.all([
                    axios.get(api_url + '/api/award_categories'),
                    axios.get(api_url + '/api/brands')
                ]);

                setAwardCategoryOptions([...categoriesRes.data.sort().map(category => ({ value: category, label: category }))]);
                setBrandOptions(brandsRes.data.sort().map(brand => ({ value: brand, label: brand })));

                // Call submitForm after initial load.
                if (initialLoad) {
                    submitForm();
                    setInitialLoad(false);
                }
            } catch (err) {
                console.log(err.message);
                console.log(err.request);
                console.log(err.response);
            }
        }

        fetchData();
    }, [submitForm, api_url, initialLoad]);  // Include initialLoad in the dependencies.

    // Call submitForm whenever awardCategory or brand changes
    useEffect(() => {
        if (!initialLoad && (prevAwardCategory !== awardCategory || prevBrand !== brand)) {
            submitForm();
        }
    }, [prevAwardCategory, prevBrand, awardCategory, brand, submitForm, initialLoad]);  // Include previous and current states, and submitForm in the dependencies.

    const handleAwardCategoryChange = (selectedOptions) => {
        setAwardCategory(selectedOptions);
    };

    const handleBrandChange = (selectedOptions) => {
        setBrand(selectedOptions);
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