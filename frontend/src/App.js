import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Navbar, Nav } from 'react-bootstrap';
import axios from 'axios';
import Cookies from 'js-cookie';
import SearchPage from './components/SearchPage';
import ExplorePage from './components/ExplorePage';
import Login from './components/Login';
import Authenticate from './components/Authenticate';
import { UserContext, UserContextProvider } from './components/UserContext';
import './App.css';
import logo from './logo.png';

function HomePage() {
  return <h1>Hello World</h1>;
}

function App() {
    return (
      <UserContextProvider>
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
                <NavigationLinks />
              </Nav>
            </Navbar.Collapse>
          </Navbar>

          <Routes>
            <Route path="/search" element={<SearchPage />} />
            <Route path="/explore" element={<ExplorePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/authenticate" element={<Authenticate />} />
            <Route path="/" element={<HomePage />} />
          </Routes>
        </Router>
      </UserContextProvider>
    );
  }
  
  function NavigationLinks() {
    const { isAuthenticated, setIsAuthenticated } = useContext(UserContext);
    const navigate = useNavigate()

    const handleLogout = async () => {
      try {
        const session_token = Cookies.get('session_token');
        console.log(session_token)
        const response = await axios.post('http://localhost:3001/api/logout', { session_token }, {
          withCredentials: true
        });
        if (response.data.message === 'Logged out successfully.') {
          Cookies.remove('session_token');
          Cookies.remove('session_jwt');
          setIsAuthenticated(false);  // Reset the user context
          navigate('/');  // Redirect the user to home page
        } else {
          console.error(response.data.error);
        }
      } catch (error) {
        console.error('Failed to log out.', error);
      }
    }    
    
    if (isAuthenticated) {
      return (
        <>
          <Nav.Link as={Link} to="/search">Search</Nav.Link>
          <Nav.Link as={Link} to="/explore">Explore</Nav.Link>
          <Nav.Link onClick={handleLogout}>Logout</Nav.Link>
        </>
      );
    } else {
      return (
        <>
          <Nav.Link as={Link} to="/login">Login</Nav.Link>
        </>
      );
    }
  }

  export default App;  