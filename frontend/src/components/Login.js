// login.jsx
import React from 'react';
import { StytchLogin } from '@stytch/react';

const Login = () => {
  const redirectURL = process.env.REACT_APP_TEST_REDIRECT_URL || "https://burnmypoints.com/authenticate"
  console.log(process.env.REACT_APP_TEST_REDIRECT_URL)
  console.log(redirectURL)

  const config = {
    "products": [
      "oauth",
      "emailMagicLinks"
    ],
    "emailMagicLinksOptions": {
      "loginRedirectURL": redirectURL,
      "loginExpirationMinutes": 30,
      "signupRedirectURL": redirectURL,
      "signupExpirationMinutes": 30
    },
    "oauthOptions": {
      "providers": [
        {
          "type": "google"
        }
      ],
      "loginRedirectURL": redirectURL,
      "signupRedirectURL": redirectURL
    },
  };
    const styles = {
    "container": {
      "backgroundColor": "#FFFFFF",
      "borderColor": "#ADBCC5",
      "borderRadius": "8px",
      "width": "500px"
    },
    "colors": {
      "primary": "#19303D",
      "secondary": "#5C727D",
      "success": "#0C5A56",
      "error": "#8B1214"
    },
    "buttons": {
      "primary": {
        "backgroundColor": "#19303D",
        "textColor": "#FFFFFF",
        "borderColor": "#19303D",
        "borderRadius": "4px"
      },
      "secondary": {
        "backgroundColor": "#FFFFFF",
        "textColor": "#19303D",
        "borderColor": "#19303D",
        "borderRadius": "4px"
      }
    },
    "fontFamily": "Tahoma",
    "hideHeaderText": false,
    "logo": {
      "logoImageUrl": ""
    }
  }  

const containerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  height: '80vh', // This will make the container take the full height of the viewport
};
                            
  return (
    <div style={containerStyle}>
      <StytchLogin config={config} styles={styles} />
    </div>
  );
}
              
export default Login;