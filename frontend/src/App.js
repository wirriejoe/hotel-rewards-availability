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