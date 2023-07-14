import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import SearchForm from './components/SearchForm';
import SearchTable from './components/SearchTable';
import ExploreForm from './components/ExploreForm';
import ExploreTable from './components/ExporeTable';
import './App.css';
import logo from './logo.png';

function SearchPage() {
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
        <SearchForm setStays={handleStaysUpdate} isLoading={isLoading} setIsLoading={setIsLoading} />
      </div>
      <div className="table-container">
        <SearchTable stays={stays} />
      </div>
    </div>
  );
}

function HomePage() {
  return <h1>Hello World</h1>;
}

function ExplorePage() {
  const [stays, setStays] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleStaysUpdate = (newData) => {
    setStays(newData);
    setIsLoading(false);
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>Explore</h1>
        <p>Explore hotel stays across award category and brand of supported Hyatt hotels over the next 60 days!</p>
      </div>
      <div className="form-container">
        <ExploreForm setStays={handleStaysUpdate} isLoading={isLoading} setIsLoading={setIsLoading} />
      </div>
      <div className="table-container">
        <ExploreTable stays={stays} />
      </div>
    </div>
  );
}

function App() {
    return (
      <Router>
        <Navbar bg="light" expand="lg" className="navbar-custom">
          <Navbar.Brand as={Link} to="/">
            <img
              src={logo}
              width="30"
              height="30"
              className="d-inline-block align-top"
              alt="BurnMyPoints logo"
            />
            BurnMyPoints
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mr-auto">
              <Nav.Link as={Link} to="/search">Search</Nav.Link>
              <Nav.Link as={Link} to="/explore">Explore</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Navbar>
  
        <Routes>
          <Route path="/search" element={<SearchPage />} />
          <Route path="/explore" element={<ExplorePage />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
      </Router>
    );
  }
  
  export default App;  