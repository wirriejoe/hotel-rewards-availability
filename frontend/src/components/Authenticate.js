import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function Authenticate() {
  const query = useQuery();
  const token = query.get("token");
  const token_type = query.get("stytch_token_type");
  const [message, setMessage] = useState("Authenticating...");
  const [error, setError] = useState(null);

  useEffect(() => {
    // Send a request to your server to authenticate the token
    fetch(`http://localhost:3001/api/authenticate?token=${token}&token_type=${token_type}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.message === 'User authenticated successfully.') {
          setMessage("Authenticated successfully! Redirecting to home...");
          // Redirect to the home page after a delay
          setTimeout(() => {
            window.location.href = "/";
          }, 2000);
        } else {
            setError(data.error);
            setMessage("Failed to authenticate.");
        }
      });
  }, [token]);

  return (
    <div>
      <h2>{message}</h2>
      {error && <p>Error: {error}</p>}
    </div>
  );
}

export default Authenticate;