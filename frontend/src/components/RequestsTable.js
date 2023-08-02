import React, { useEffect, useState } from 'react';
import DataTable from 'react-data-table-component';
import Tooltip from '@mui/material/Tooltip';
import Button from '@mui/material/Button';
import { styled } from '@mui/system';
import TextField from '@mui/material/TextField';
import Pagination from '@mui/material/Pagination';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import axios from 'axios';
import Cookies from 'js-cookie';
import { sort } from 'fast-sort';
import '../App.css';

const StyledSpan = styled('span')(({ theme, color }) => ({
  color: color,
}));

function RequestsTable({ isLoading, setIsLoading, isCustomer }) {
  const [filterText, setFilterText] = useState("");
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(
    localStorage.getItem('rowsPerPage') ? parseInt(localStorage.getItem('rowsPerPage')) : 10
  );
  const [requests, setRequests] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: null });
  const [isButtonLoading, setIsButtonLoading] = useState(false);
  const api_url = process.env.REACT_APP_TEST_API_URL || 'https://hotel-rewards-availability-api.onrender.com'
  
  useEffect(() => {
    setIsLoading(true);
  
    const fetchRequestsAndHotels = async () => {
      const session_token = Cookies.get('session_token');
      try {
        const [requestsResponse, hotelsResponse] = await Promise.all([
          axios.get(`${api_url}/api/requests?session_token=${session_token}`),
          axios.get(`${api_url}/api/stays?session_token=${session_token}`)
        ]);

        setRequests(hotelsResponse.data.map(hotel => {
          const request = requestsResponse.data.find(request => request.hotel_code === hotel.hotel_code);
          return {...hotel, requested: !!request};
        }));
      } catch (error) {
        console.error("Error fetching requests and hotels data:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchRequestsAndHotels();
  }, [setIsLoading]);
  
  const columns = [
    {
      id: 'hotel_name',
      name: 'Hotel', 
      selector: 'hotel_name', 
      sortable: true
    },
    {
      id: 'num_nights',
      name: '# of nights tracked',
      cell: row => (
        <Tooltip 
          title={
            row.num_night_monitored <= 61 
              ? "Only 60 days of availability from today can be viewed" 
              : "Pro users can see the full calendar for this hotel, normal users can see 60 days of availability from today"
          }
        >
          <StyledSpan color={row.num_night_monitored <= 61 ? "black" : "green"}>
            {row.num_night_monitored <= 61 ? "60 Days" : "Full Calendar"}
          </StyledSpan>
        </Tooltip>
      ),
      sortFunction: (rowA, rowB) => rowA.num_night_monitored - rowB.num_night_monitored,
    },
    {
      id: 'request',
      name: 'Request full calendar tracking', 
      cell: row => (
        isCustomer ? (
          <Button 
            variant="contained" 
            color="secondary" 
            style={{fontWeight: 'bold', fontSize: '0.8em'}}
            onClick={() => requestTracking(row)}
            disabled={isButtonLoading || row.requested || row.num_night_monitored > 61} // Button is disabled if loading or if request has been made for this row
          >
            {
              // Display different texts based on the state
              isButtonLoading 
                ? 'Loading...' 
                : row.num_night_monitored > 61
                  ? 'Tracking full calendar'
                  : row.requested 
                    ? 'Requested' 
                    : 'Request tracking'
            }
          </Button>
        ) : (
          <Button 
            variant="contained" 
            color="secondary"
            href={'https://buy.stripe.com/6oE8xe4ps4ly7fy4gi'} 
            // href={'https://buy.stripe.com/test_eVaeVvalGeIv30AbII'}
            style={{fontWeight: 'bold', fontSize: '0.8em'}}
            onClick={() => ""}
          >
            Upgrade to PRO
          </Button>
        )
      ) 
    }
  ];

  async function requestTracking(row) {
    setIsButtonLoading(true);
    const session_token = Cookies.get("session_token");
    
    const data = {
      hotel_id: row.hotel_id,
      hotel_code: row.hotel_code,
      session_token: session_token
    };
  
    try {
      const response = await fetch(api_url + '/api/request', {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      if (response.ok) {
        setRequests((prevRequests) =>
          prevRequests.map((item) =>
            item.hotel_id === row.hotel_id ? { ...item, requested: true } : item
          )
        );
      }
  
    } catch(error) {
      console.error(error);
    } finally {
      setIsButtonLoading(false);
    }
  }
    
  const sortedItems = sortConfig.key
    ? sort(requests).by([
        {
          [sortConfig.direction]: (request) =>
            sortConfig.key === "num_nights"
              ? request.num_night_monitored
              : request[sortConfig.key],
        },
      ])
    : requests;

  const filteredItems = sortedItems.filter(item =>
    columns.some(
      (column) =>
        item[column.selector] &&
        item[column.selector]
          .toString()
          .toLowerCase()
          .includes(filterText.toLowerCase())
    )
  );

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(event.target.value);
    setPage(1);
    localStorage.setItem('rowsPerPage', event.target.value);
  };

  const handleSort = (column, sortDirection) => {
    // If the column has a sortFunction, use it to sort the data
    if (column.sortFunction) {
      setRequests((oldRequests) =>
        [...oldRequests].sort((a, b) =>
          sortDirection === 'desc' ? column.sortFunction(b, a) : column.sortFunction(a, b)
        )
      );
    }
    setSortConfig({ key: column.selector, direction: sortDirection });
  };

  const paginatedItems = filteredItems.slice((page - 1) * rowsPerPage, page * rowsPerPage);
    
  return (
    <div>
      {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <h4>Loading...</h4>
          </div>
        ): (
        <div style={{ height: 'auto', width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.1em', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <FormControl variant="standard" sx={{ m: 1, minWidth: 80}}>
                <InputLabel id="rows-per-page-label">Rows</InputLabel>
                <Select
                  labelId="rows-per-page-label"
                  value={rowsPerPage}
                  onChange={handleChangeRowsPerPage}
                  displayEmpty
                  inputProps={{ 'aria-label': 'Without label'}}
                  sx={{ fontSize: '0.9em' }}
                >
                  <MenuItem value={10} sx={{ fontSize: '0.9em' }}>10</MenuItem>
                  <MenuItem value={20} sx={{ fontSize: '0.9em' }}>20</MenuItem>
                  <MenuItem value={50} sx={{ fontSize: '0.9em' }}>50</MenuItem>
                  <MenuItem value={100} sx={{ fontSize: '0.9em' }}>100</MenuItem>
                </Select>
              </FormControl>
              <Pagination
                count={Math.ceil(filteredItems.length / rowsPerPage)}
                page={page}
                onChange={handleChangePage}
              />
            </div>
            <div>
              <span style={{ marginRight: '0.5em' }}>Search:</span>
              <TextField 
                  sx={{ width: '200px', '& .MuiInputBase-input': { height: '0.2em' } }}
                  label="" 
                  variant="outlined"
                  value={filterText}
                  onChange={(e) => setFilterText(e.target.value)}
              />
            </div>
          </div>
          <DataTable
            data={paginatedItems}
            columns={columns}
            noHeader
            className="dataTables_wrapper"
            onSort={handleSort}
            sortServer
          />
        </div>
      )}
    </div>
  );
}

export default RequestsTable;