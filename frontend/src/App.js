import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import SearchPage from './components/SearchPage';
import ExplorePage from './components/ExplorePage';
import './App.css';
import logo from './logo.png';

function HomePage() {
  return <h1>Hello World</h1>;
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