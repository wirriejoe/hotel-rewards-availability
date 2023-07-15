import React, {useState} from "react";
import ExploreForm from "./ExploreForm";
import ExploreTable from "./ExporeTable";

function ExplorePage() {
    const [stays, setStays] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
  
    const handleStaysUpdate = (newData) => {
      setStays(newData);
      setIsLoading(false);
    };
  
    return (
      <div className="app-container">
        <div className="header">
          <h1>Explore</h1>
          <p>Explore hotel stays across award category and brand for supported Hyatt hotels over the next 60 days!</p>
        </div>
        <div className="form-container">
          <ExploreForm setStays={handleStaysUpdate} isLoading={isLoading} setIsLoading={setIsLoading} />
        </div>
        <div className="table-container">
          <ExploreTable stays={stays} />
        </div>
      </div>
    );
  }

export default ExplorePage;