import React, { useEffect, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate} from 'react-router-dom';
import { Navbar, Nav, Dropdown } from 'react-bootstrap';
import axios from 'axios';
import Cookies from 'js-cookie';
import HomePage from './components/HomePage';
import SearchPage from './components/SearchPage';
import ExplorePage from './components/ExplorePage';
import RequestsPage from './components/RequestsPage';
import HotelPage from './components/HotelPage';
import Login from './components/Login';
import Reset from './components/Reset';
import Authenticate from './components/Authenticate';
import { UserContext, UserContextProvider } from './components/UserContext';
import './App.css';
import logo from './logo.png';

const ExternalRedirect = ({ to }) => {
    useEffect(() => {
      window.location.href = to;
    }, [to]);
  
    return null;
  };  

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
                  <Navbar.Collapse id="basic-navbar-nav" className="justify-content-between">
                      <Nav>
                          <Nav.Link as={Link} to="/search">Search</Nav.Link>
                          <Dropdown as={Nav.Item}>
                            <Dropdown.Toggle as={Nav.Link}>Discover</Dropdown.Toggle>
                            <Dropdown.Menu>
                                <Dropdown.Item as={Link} to="/hyatt/explore">World of Hyatt</Dropdown.Item>
                                <Dropdown.Item as={Link} to="/hilton/explore">Hilton Honors</Dropdown.Item>
                                <Dropdown.Item as={Link} to="/ihg/explore">IHG One Rewards</Dropdown.Item>
                            </Dropdown.Menu>
                        </Dropdown>
                          <Nav.Link as={Link} to="/request">Request</Nav.Link> 
                          <Nav.Link as={Link} to="/alerts">Create Alert</Nav.Link> 
                      </Nav>
                      <Nav>
                          <NavigationLinks />
                      </Nav>
                  </Navbar.Collapse>
              </Navbar>
              <div className='app-container'>
                  <Routes>
                      <Route path="/search" element={<SearchPage />} />
                      <Route path="/explore" element={<ExplorePage />} />
                      <Route path="/request" element={<RequestsPage />} />
                      <Route path="/:hotelName/explore" element={<ExplorePage />} />
                      <Route path="/:hotelName/hotel/:hotelCode" element={<HotelPage />} />
                      <Route path="/alerts" element={<ExternalRedirect to="https://apps.burnmypoints.com/embedded/public/160eb83d-fa97-4014-9b5b-4dafd7c6ee4f"/>} />
                      <Route path="/login" element={<Login />} />
                      <Route path="/reset" element={<Reset />} />
                      <Route path="/authenticate" element={<Authenticate />} />
                      <Route path="/" element={<HomePage />} />
                  </Routes>
              </div>
          </Router>
      </UserContextProvider>
  );
}

function NavigationLinks() {
  const { setIsCustomer, isAuthenticated, setIsAuthenticated } = useContext(UserContext);
  const navigate = useNavigate();
  const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com';

  const handleLogout = async () => {
        try {
            const session_token = Cookies.get('session_token');
            const data = {
                session_token: session_token
            };
            const response = await axios.post(api_url + '/api/logout', data);

            if (response.data.message === 'Logged out successfully.') {
                Cookies.remove('session_token');
                Cookies.remove('session_jwt');
                Cookies.remove('stytch_session')
                Cookies.remove('stytch_session_jwt')
                setIsAuthenticated(false);  // Reset the user context
                setIsCustomer(false);
                navigate('/');  // Redirect the user to home page
                window.location.reload();  // Force a page reload
            } else {
                console.error(response.data.error);
            }
        } catch (error) {
            console.error('Failed to log out.', error);
        }
  };

  if (isAuthenticated) {
        return (
            <>
                <Nav.Link onClick={handleLogout}>
                    🔚 Logout
                </Nav.Link>
            </>
        );
  } else {
        return (
            <>
                <Nav.Link as={Link} to="/login">👤 Login</Nav.Link>
            </>
        );
  }
}

export default App;