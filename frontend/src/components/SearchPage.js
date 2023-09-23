import React, { useState, useContext } from 'react';
// import SearchForm from './SearchForm';
import SearchTable from './SearchTable';
import SearchMap from './SearchMap';  // <-- Make sure to import this
import { UserContext } from './UserContext';
// import Login from './Login';

function SearchPage() {
  const [stays, setStays] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { isCustomer } = useContext(UserContext);

  // const handleStaysUpdate = (newData) => {
  //   setStays(newData);
  //   setIsLoading(false);
  // };

  return (
    // isAuthenticated ? (
      <div>
        <div className="header">
          <h1>Search</h1>
          <p>Instantly search for availability for hotel stays across all of our supported Hyatt hotels at once!</p>
        </div>
        <div className="map-container">
          <SearchMap stays={stays} setStays={setStays} isLoading={isLoading} setIsLoading={setIsLoading} isCustomer={isCustomer} />  {/* <-- Add this line */}
        </div>
        {/* <div className="form-container">
          <SearchForm setStays={handleStaysUpdate} isLoading={isLoading} setIsLoading={setIsLoading} isCustomer={isCustomer} />
        </div> */}
        <div className="table-container">
          <SearchTable stays={stays} />
        </div>
      </div>
    // ) : (
    //   <Login />
    // )
  );
}

export default SearchPage;