import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import Cookies from 'js-cookie';

export const UserContext = React.createContext();

const socket = io(process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com');  // Replace with your server address

export const UserContextProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const authStatus = localStorage.getItem('isAuthenticated');
    return authStatus === 'true' ? true : false;
  });

  const [isCustomer, setIsCustomer] = useState(() => {
    const customerStatus = localStorage.getItem('isCustomer');
    return customerStatus === 'true' ? true : false;
  });
  const session_token = Cookies.get('session_token');

  useEffect(() => {
    localStorage.setItem('isAuthenticated', isAuthenticated.toString());
  }, [isAuthenticated]);

  useEffect(() => {
    localStorage.setItem('isCustomer', isCustomer.toString());
  }, [isCustomer]);

  useEffect(() => {
    // Establish the connection
    socket.on('connected', data => {
      // Emit 'get_status' event with a user ID
      socket.emit('get_status', { session_token: session_token });
    });

    // Handle 'customer_status' event
    socket.on('customer_status', data => {
      setIsCustomer(data.customer_status);
    });

    return () => {
      socket.off('connect');
      socket.off('customer_status');
    };
  }, [isCustomer, session_token]);

  return (
    <UserContext.Provider value={{ isAuthenticated, setIsAuthenticated, isCustomer, setIsCustomer }}>
      {children}
    </UserContext.Provider>
  );
};
