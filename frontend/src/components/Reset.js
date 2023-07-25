import React, { useState, useEffect } from 'react';
import { Products } from '@stytch/vanilla-js';
import { StytchPasswordReset } from '@stytch/react';


const config = {
  passwordOptions: {
    loginExpirationMinutes: 30,
    loginRedirectURL: process.env.REACT_APP_TEST_REDIRECT_URL || "https://burnmypoints.com/authenticate",
    resetPasswordExpirationMinutes: 30,
    resetPasswordRedirectURL: 'http://localhost:3000/reset'
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
  const [passwordResetToken, setPasswordResetToken] = useState('');

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