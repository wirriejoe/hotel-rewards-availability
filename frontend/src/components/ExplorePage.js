import React, {useState, useContext} from "react";
import ExploreForm from "./ExploreForm";
import ExploreTable from "./ExporeTable";
import { UserContext } from './UserContext';
import { useParams } from 'react-router-dom'; 
import Login from './Login';

function ExplorePage() {
    const [stays, setStays] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const { isAuthenticated, isCustomer } = useContext(UserContext);
    const {hotelName} = useParams();

    // const handleStaysUpdate = (newData) => {
    //   setStays(newData);
    //   setIsLoading(false);
    // };
  
    return (
      isAuthenticated ? (
        <div>
          <div className="header">
            <h1>Discover</h1>
            {
              isCustomer ? 
                <p>
                  Discover hotel stays across award category and brand for supported {hotelName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')} hotels!
                </p>
                :
                <p>
                  Discover hotel stays across award category and brand for supported {hotelName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')} hotels! Free plan can see 60 days of availabilities.{" "}
                  <a href="https://buy.stripe.com/6oE8xe4ps4ly7fy4gi" target="_blank" rel="noreferrer">
                    Upgrade to Pro plan to see 360 days of availabilities.
                  </a>
                </p>  
            }
          </div>
          <div className="form-container">
            <ExploreForm key={hotelName} setStays={setStays} isLoading={isLoading} setIsLoading={setIsLoading} isCustomer = {isCustomer} hotelName = {hotelName} />
          </div>
          <div className="table-container">
            {isLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                    <h5>Loading</h5>
                </div>
            ) : (
                <>
                <ExploreTable stays={stays} isLoading={isLoading} />
                </>
                )}
          </div>
        </div>
      ) : (
        <Login />
      )
    );
}

export default ExplorePage;