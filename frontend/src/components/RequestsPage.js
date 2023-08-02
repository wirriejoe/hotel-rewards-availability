import React, {useState, useContext} from "react";
import { UserContext } from './UserContext';
import RequestsTable from './RequestsTable';
import Login from './Login';

function RequestsPage({ isPro }) {
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated } = useContext(UserContext);
  const { isCustomer } = useContext(UserContext);

  return (
    isAuthenticated ? (
      <div>
        <div>
          <h1>Request</h1>
          <p>This page shows the hotels that are being tracked for availability. Availability won't show up on BurnMyPoints.com unless they are single night Standard or Premium awards. Tracking requests are processed within 24 hours. If you have any questions, feel free to message @snorlax on {' '}
            <a href="https://discord.gg/M6zexyPYk" target="_blank" rel="noreferrer">
              Discord!
            </a>
          </p>
        </div>
        <RequestsTable isLoading={isLoading} setIsLoading={setIsLoading} isCustomer={isCustomer} />
      </div>
    ) : (
      <Login/>
    )
  );
}

export default RequestsPage;