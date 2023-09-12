import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import 'react-data-table-component-extensions/dist/index.css';
import 'mapbox-gl/dist/mapbox-gl.css'
import { StytchProvider } from '@stytch/react';
import { StytchUIClient } from '@stytch/vanilla-js';

const token = process.env.REACT_APP_TEST_TOKEN || 'public-token-live-bdb99070-4e2b-4052-8a9a-0d99197ebe22'
const stytch = new StytchUIClient(token);
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <StytchProvider stytch={stytch}>
      <App />
    </StytchProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
