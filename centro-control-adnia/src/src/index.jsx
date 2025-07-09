import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import MainApp from './MainApp';
import { GoogleOAuthProvider } from '@react-oauth/google';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId="432675833697-2nbtvjr7k1srm6uh6ojmqtari1k285sk.apps.googleusercontent.com">
      <MainApp />
    </GoogleOAuthProvider>
  </React.StrictMode>
);