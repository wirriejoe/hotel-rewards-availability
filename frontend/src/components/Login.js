import React, { useEffect, useContext } from 'react';
import { useNavigate } from "react-router-dom";
import { StytchLogin, useStytchSession } from '@stytch/react';
import { UserContext } from "./UserContext";
import Cookies from 'js-cookie';

const Login = () => {
  const redirectURL = process.env.REACT_APP_TEST_REDIRECT_URL || "https://burnmypoints.com/authenticate"
  const resetURL = process.env.REACT_APP_TEST_RESET_URL || "https://burnmypoints.com/reset"
  const { session } = useStytchSession();
  const { setIsAuthenticated } = useContext(UserContext);
  let navigate = useNavigate();

  useEffect(() => {
    if (session) {
      console.log('Successfully logged in!');
      // console.log(session)
      setIsAuthenticated(true);
      Cookies.set('session_token', Cookies.get('stytch_session'), { secure: true, sameSite: 'lax' });
      setTimeout(() => {
        navigate("/"); 
      }, 0);
    }
  }, [session, navigate, setIsAuthenticated]);

  const config = {
    "products": [
      "oauth",
      "emailMagicLinks",
      "passwords"
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
    "passwordOptions": {
      "loginRedirectURL": redirectURL,
      "resetPasswordRedirectURL": resetURL
    }
    
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