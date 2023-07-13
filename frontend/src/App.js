import React, { useState } from 'react';
import Form from './components/Form';
import Table from './components/Table';
import './App.css';

function App() {
    const [stays, setStays] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleStaysUpdate = (newData) => {
        setStays(newData);
        setIsLoading(false);
    };

    return (
        <div className="app-container">
            <div className="header">
                <h1>Search</h1>
                <p>Instantly search for availability for hotel stays across all of our supported Hyatt hotels at once!</p>
            </div>
            <div className="form-container">
                <Form setStays={handleStaysUpdate} isLoading={isLoading} setIsLoading={setIsLoading} />
            </div>
            <div className="table-container">
                <Table stays={stays} />
            </div>
        </div>
    );
}

export default App;