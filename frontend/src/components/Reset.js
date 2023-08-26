import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { Products } from '@stytch/vanilla-js';
import { StytchPasswordReset, useStytchUser } from '@stytch/react';
import Cookies from 'js-cookie';

const config = {
  passwordOptions: {
    loginExpirationMinutes: 30,
    loginRedirectURL: process.env.REACT_APP_TEST_REDIRECT_URL || "https://burnmypoints.com/authenticate",
    resetPasswordExpirationMinutes: 30,
    resetPasswordRedirectURL: process.env.REACT_APP_TEST_RESET_URL || 'https://burnmypoints/reset'
  },
  products: [
    Products.passwords,
  ],
};

const containerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '80vh', // This will make the container take the full height of the viewport
  };

const Reset = () => {
  const { user } = useStytchUser();
  const [passwordResetToken, setPasswordResetToken] = useState('');
  
  let navigate = useNavigate();

  if (user) {
    navigate(`/authenticate?token=${Cookies.get('stytch_session')}&stytch_token_type=password_resets`)
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    setPasswordResetToken(token ?? '');
  }, []);

  return (
    <div style={containerStyle}>
      <StytchPasswordReset
        config={config}
        passwordResetToken={passwordResetToken}
      />
    </div>
  );
};

export default Reset;