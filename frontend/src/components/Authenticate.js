import React, { useState, useEffect, useContext } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { UserContext } from "./UserContext";
import Cookies from 'js-cookie';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function Authenticate() {
  // Access the authentication state and the function to set it
  const { isAuthenticated, setIsAuthenticated } = useContext(UserContext);
  const query = useQuery();
  const token = query.get("token");
  const token_type = query.get("stytch_token_type");
  const [message, setMessage] = useState("Authenticating...");
  const [error, setError] = useState(null);
  const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'
  let navigate = useNavigate();

  useEffect(() => {
    // Send a request to your server to authenticate the token
    fetch(`${api_url}/api/authenticate?token=${token}&token_type=${token_type}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.message === 'User authenticated successfully.') {
          // Update the authentication state
          setIsAuthenticated(true);
          
          // Save the session token and JWT in cookies
          Cookies.set('session_token', data.session_token, { secure: true, sameSite: 'lax' });
          Cookies.set('session_jwt', data.session_jwt, { secure: true, sameSite: 'lax' });
      
          setMessage("Authenticated successfully! Redirecting to home...");
          // Redirect to the home page after a delay
          setTimeout(() => {
            navigate("/"); 
          }, 0);
        } else {          
          setError(data.error);
          setMessage("Failed to authenticate.");
        }
      });
  }, [token, token_type, navigate, setIsAuthenticated, api_url]); // Make sure to include setIsAuthenticated in the dependency array

  useEffect(() => {
    console.log(isAuthenticated);
  }, [isAuthenticated]);  

  return (
    <div>
      <h2>{message}</h2>
      {error && <p>Error: {error}</p>}
    </div>
  );
}

export default Authenticate;