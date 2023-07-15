import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import Select from 'react-select';

function ExploreForm({ setStays, isLoading, setIsLoading }) {
    const [awardCategory, setAwardCategory] = useState({ value: '8', label: '8' });
    const [awardCategoryOptions, setAwardCategoryOptions] = useState([]);
    const [brand, setBrand] = useState("");
    const [brandOptions, setBrandOptions] = useState([]);

    // Fetch award categories and brands on component mount
    useEffect(() => {
        Promise.all([
            axios.get('https://hotel-rewards-availability-api.onrender.com/api/award_categories', {
                withCredentials: true
            }),
            axios.get('https://hotel-rewards-availability-api.onrender.com/api/brands', {
                withCredentials: true
            })
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

    // Note: setIsLoading and setStays are omitted from the deps array intentionally.
    // This is safe here because they're guaranteed to be stable and won't cause re-renders.
    const fetchData = useCallback(async () => {
        setIsLoading(true);

        const searchData = {
            award_category: [awardCategory.value],
            brand: [brand.value],
            withCredentials: true
        };

        try {
            const response = await axios.post('https://hotel-rewards-availability-api.onrender.com/api/explore', searchData);
            setStays(response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [awardCategory, brand]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="form-group">
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
            </div>
        </div>
    );
}

export default ExploreForm;