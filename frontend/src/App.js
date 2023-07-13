import React, { useState } from 'react';
import Form from './components/Form';
import Table from './components/Table';
import './App.css'; // make sure to import the css file

function App() {
    const [stays, setStays] = useState([]);

    return (
        <div className="app-container">
            <div className="form-container">
                <Form setStays={setStays} />
            </div>
            <div className="table-container">
                <Table stays={stays} />
            </div>
        </div>
    );
}

export default App;