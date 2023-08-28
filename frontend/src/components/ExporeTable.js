import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import DataTable from 'react-data-table-component';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import { styled } from '@mui/system';
import TextField from '@mui/material/TextField';
import Pagination from '@mui/material/Pagination';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import CelebrationIcon from '@mui/icons-material/Celebration'; // Import the weekend icon https://mui.com/material-ui/material-icons/?query=weekend
import Cookies from 'js-cookie';
import '../App.css';

const CustomTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))({
  '& .MuiTooltip-tooltip': {
    backgroundColor: 'black',
    color: 'white',
  },
});

const columns = [
    {
      name: 'Date', 
      selector: 'check_in_date', 
      grow: '0.9', 
      sortable: true,
      cell: row => {
        const date = new Date(row.check_in_date);
        const day = date.getDay();
        const isWeekend = day === 4 || day === 5; // Friday or Saturday
        const weekendDay = day === 4 ? 'Friday' : 'Saturday';

        return (
          <CustomTooltip title={isWeekend ? `The Check-in Date for this stay is on ${weekendDay}!` : ''}>
            <div style={{ display: 'flex', alignItems: 'center', fontWeight: isWeekend ? 'bold' : 'normal', color: isWeekend ? '#9c27b0' : 'inherit' }}>
              {isWeekend && <CelebrationIcon style={{ fontSize: '1em', marginRight: '0.5em' }} />} 
              {date.toISOString().slice(0,10)}
            </div>
          </CustomTooltip>
        );
      }
    },
    { name: 'Last Checked', selector: 'last_checked_time', grow: '0.75', sortable: true , format: row => row.last_checked},
    {
      name: 'Hotel', 
      selector: 'hotel_name', 
      grow: '1.5', // like width, but allows columns to grow based on length of values
      sortable: true, 
      cell: row => (
        <CustomTooltip title={
          <React.Fragment>
            <div>Hotel: {row.hotel_name}</div>
            <div>Location: {row.hotel_city}, {row.hotel_province}, {row.hotel_country}</div>
            <div>Region: {row.hotel_region}</div>
            <div>Award Category: {row.award_category}</div>
          </React.Fragment>
        }>
          <Link to={`/hyatt/hotel/${row.hotel_code}`}>
              <div>{row.hotel_name}</div>
          </Link>
        </CustomTooltip>
      ),
    },
    // { name: 'City', selector: 'hotel_city', grow: '1', sortable: true },
    // { name: 'Region', selector: 'hotel_province', grow: '1', sortable: true },
    { name: 'Country', selector: 'hotel_country', grow: '1', sortable: true },
    {
      name: 'Standard', 
      selector: 'standard_rate', 
      grow: '1.5', 
      sortable: true, 
      cell: row => (
        <div className = "column-container">
          <div className="rate-container">
            <div className={`rate-block ${row.standard_rate > 0 ? 'green-background' : 'grey-background'}`}>
              {row.standard_rate > 0 ? `${parseInt(row.standard_rate).toLocaleString()} pts` : 'N/A'}
            </div>
            <div className={`rate-block ${row.standard_cash > 0 ? 'green-background' : 'grey-background'}`}>
              {row.standard_cash > 0 ? `${parseInt(row.standard_cash).toLocaleString()} ${row.currency_code}` : 'N/A'}
            </div>
          </div>
          <div className="point-block">
            {row.standard_cash_usd > 0 && row.standard_rate > 0 ? (row.standard_cash_usd / row.standard_rate * 100).toFixed(1) + "₵":'N/A'} per pt (USD)
          </div>
        </div>
      )
    },
    { 
        name: 'Premium', 
        selector: 'premium_rate', 
        grow: '1.5', 
        sortable: true,
        cell: row => (
          <div className='column-container'>
            <div className="rate-container">
              <div className={`rate-block ${row.premium_rate > 0 ? 'green-background' : 'grey-background'}`}>
                {row.premium_rate > 0 ? `${parseInt(row.premium_rate).toLocaleString()} pts` : 'N/A'}
              </div>
              <div className={`rate-block ${row.premium_cash > 0 ? 'green-background' : 'grey-background'}`}>
                {row.premium_cash > 0 ? `${parseInt(row.premium_cash).toLocaleString()} ${row.currency_code}` : 'N/A'}
              </div>
            </div>
            <div className="point-block">
              {row.premium_cash_usd > 0 && row.premium_rate > 0 ? (row.premium_cash_usd / row.premium_rate * 100).toFixed(1) + "₵":'N/A'} per pt (USD)
            </div>
          </div>
        )
    },
    {
        name: 'URL', 
        grow: '0.25', 
        cell: row => (
          <Button 
              variant="contained" 
              color="secondary" 
              href={row.booking_url} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{fontWeight: 'bold', fontSize: '0.8em'}} // Adjust the value as needed
              onClick={() => logEvent(row.booking_url)}
          >
            Book
          </Button>
        ) 
    }    
];  

function logEvent(url) {
  const session_token = Cookies.get("session_token");
  
  const data = {
    event_name: "explore_booking_click",
    event_details: url,
    session_token: session_token
  };

  fetch("https://burnmypoints.com/api/log_event", {  // Python API endpoint
    method: "POST",
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  }).catch(error => console.error('Error:', error));
}

function ExploreTable({ stays }) {
  const [filterText, setFilterText] = useState("");
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(
    localStorage.getItem('rowsPerPage') ? parseInt(localStorage.getItem('rowsPerPage')) : 10
  );
  const [sortState, setSortState] = useState([
    { column: { selector: 'check_in_date' }, sortDirection: 'asc' }
  ]);
  
  stays = stays.map(stay => ({
    ...stay,
    check_in_date: new Date(stay.check_in_date).toISOString().slice(0,10),
    last_checked_time: new Date(stay.last_checked_time), 
  }));

  const filteredItems = stays.filter(item =>
    columns.some(
      (column) =>
        item[column.selector] &&
        item[column.selector]
          .toString()
          .toLowerCase()
          .includes(filterText.toLowerCase())
    )
    || item.hotel_province.toLowerCase().includes(filterText.toLowerCase()) // Include the region in the search
    || item.hotel_city.toLowerCase().includes(filterText.toLowerCase()) // Include the city in the search
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
    setSortState(prevState => {
      let newState = [...prevState];
      const existingIndex = newState.findIndex(sort => sort.column.selector === column.selector);
  
      if (existingIndex !== -1) {
        newState.splice(existingIndex, 1);
      }
  
      newState.push({ column, sortDirection });
  
      // Limit the number of sorts to 2
      while (newState.length > 2) {
        newState.shift();
      }
  
      return newState;
    });
  };
  
  const sortedItems = [...filteredItems].sort((a, b) => {
    for (let i = sortState.length - 1; i >= 0; i--) {
      const { column, sortDirection } = sortState[i];
      if (a[column.selector] < b[column.selector]) return sortDirection === 'asc' ? -1 : 1;
      if (a[column.selector] > b[column.selector]) return sortDirection === 'asc' ? 1 : -1;
    }
  
    return 0;
  });
    
  return (
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
              sx={{ width: '200px', '& .MuiInputBase-input': { height: '0.2em' } }}  // Adjust the width as needed
              label="" 
              variant="outlined"
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
          />
        </div>
      </div>
      <DataTable
        data={sortedItems.slice((page - 1) * rowsPerPage, page * rowsPerPage)}
        columns={columns}
        noHeader
        className="dataTables_wrapper"
        onSort={handleSort}
        sortServer
      />
    </div>
  );
}

export default ExploreTable;