import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import Select from 'react-select';

function ExploreForm({ setStays, isLoading, setIsLoading }) {
    const [search, setSearch] = useState("");
    const [awardCategory, setAwardCategory] = useState({ value: '8', label: '8' });
    const [awardCategoryOptions, setAwardCategoryOptions] = useState([]);
    const [brand, setBrand] = useState("");
    const [brandOptions, setBrandOptions] = useState([]);

    // Fetch award categories and brands on component mount
    useEffect(() => {
        Promise.all([
            axios.get('https://hotel-rewards-availability-api.onrender.com/api/award_categories'),
            axios.get('https://hotel-rewards-availability-api.onrender.com/api/brands')
        ])
        .then(([categoriesRes, brandsRes]) => {
            setAwardCategoryOptions(categoriesRes.data.sort().map(category => ({ value: category, label: category })));
            setBrandOptions(brandsRes.data.sort().map(brand => ({ value: brand, label: brand })));
        })
        .catch(err => {
            console.log(err.message);
            console.log(err.request);
            console.log(err.response);
        });
    }, []);

    const submitForm = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        
        console.log({
            award_category: [awardCategory.value],
            brand: [brand.value]
        });
        
        const searchData = {
            award_category: [awardCategory.value],
            brand: [brand.value]
        };

        try {
            const response = await axios.post('https://hotel-rewards-availability-api.onrender.com/api/explore', searchData);
            setStays(response.data);
            setIsLoading(false);
        } catch (error) {
            console.error(error);
            setIsLoading(false);  // Make sure to set loading false in case of error
        }
    };

    return (
        <form onSubmit={submitForm} className="form-group">
            <div className="row">
                <div className="col">
                    <label>Award Category:</label>
                    <Select
                        options={awardCategoryOptions} 
                        value={awardCategory}
                        onChange={setAwardCategory}
                    />
                </div>
                <div className="col">
                    <label>Brand:</label>
                    <Select
                        options={brandOptions} 
                        value={brand}
                        onChange={setBrand}
                    />
                </div>
                <div className="col">
                    <label>Search:</label>
                    <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} className="form-control" placeholder="Search..." />
                </div>
            </div>
            <button type="search" className="btn btn-primary mt-3" disabled={isLoading}>
                {isLoading ? 'Loading...' : 'Search'}
            </button>
        </form>
    );
}

export default ExploreForm;