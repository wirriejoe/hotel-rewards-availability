import React, { useState } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import { styled } from '@mui/system';
import TextField from '@mui/material/TextField';

const CustomTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))({
  '& .MuiTooltip-tooltip': {
    backgroundColor: 'black',
    color: 'white',
  },
});

const columns = [
    { field: 'date_range_start', headerName: 'Check In', sortable: true, flex: 6 },
    { field: 'date_range_end', headerName: 'Check Out', sortable: true, flex: 6 },
    { field: 'last_checked', headerName: 'Last Checked', sortable: true, flex: 8 },
    {
      field: 'hotel_name', 
      headerName: 'Hotel', 
      sortable: true, 
      flex: 12,
      renderCell: (params) => {
        const { row } = params;
        return (
          <CustomTooltip title={
            <React.Fragment>
              <div>Hotel: {row.hotel_name}</div>
              <div>Location: {row.hotel_city}, {row.hotel_province}, {row.hotel_country}</div>
              <div>Region: {row.hotel_region}</div>
              <div>Award Category: {row.award_category}</div>
            </React.Fragment>
          }>
            <div>{params.value}</div>
          </CustomTooltip>
        );
      },
    },
    {
        field: 'award_category', 
        headerName: 'Category', 
        sortable: true, 
        flex: 6,
        renderCell: (params) => (
          <Tooltip title={params.value}>
            <div>{params.value}</div>
          </Tooltip>
        )
    }, 
    {
        field: 'hotel_city', 
        headerName: 'City', 
        sortable: true, 
        flex: 8,
        renderCell: (params) => (
          <Tooltip title={params.value}>
            <div>{params.value}</div>
          </Tooltip>
        )
    },
    {
        field: 'hotel_province', 
        headerName: 'State/Province', 
        sortable: true, 
        flex: 8,
        renderCell: (params) => (
          <Tooltip title={params.value}>
            <div>{params.value}</div>
          </Tooltip>
        )
    },
    // {
    //     field: 'hotel_country', 
    //     headerName: 'Country', 
    //     sortable: true, 
    //     flex: 8,
    //     renderCell: (params) => (
    //       <Tooltip title={params.value}>
    //         <div>{params.value}</div>
    //       </Tooltip>
    //     )
    // }, 
    // {
    //     field: 'hotel_region', 
    //     headerName: 'Region', 
    //     sortable: true, 
    //     flex: 8,
    //     renderCell: (params) => (
    //       <Tooltip title={params.value}>
    //         <div>{params.value}</div>
    //       </Tooltip>
    //     )
    // }, 
    {
        field: 'standard_rate', 
        headerName: 'Standard', 
        sortable: true, 
        flex: 6,
        renderCell: (params) => (
            params.value > 0 ?
            <div style={{backgroundColor: 'green', color: 'white', padding: '5px', borderRadius: '5px', fontWeight: 'bold', fontSize: '0.9em'}}>
                {`${parseInt(params.value).toLocaleString()} pts`}
            </div>
            :
            <div style={{backgroundColor: 'grey', color: 'white', padding: '5px', borderRadius: '5px', fontWeight: 'bold', fontSize: '0.8em'}}>
                {'Not Available'}
            </div>
        )
    },
    { 
        field: 'premium_rate', 
        headerName: 'Premium', 
        sortable: true, 
        flex: 6,
        renderCell: (params) => (
            params.value > 0 ?
            <div style={{backgroundColor: 'green', color: 'white', padding: '5px', borderRadius: '5px', fontWeight: 'bold', fontSize: '0.9em'}}>
                {`${parseInt(params.value).toLocaleString()} pts`}
            </div>
            :
            <div style={{backgroundColor: 'grey', color: 'white', padding: '5px', borderRadius: '5px', fontWeight: 'bold', fontSize: '0.8em'}}>
                {'Not Available'}
            </div>
        )
    },
    {
        field: 'booking_url', 
        headerName: 'Info', 
        flex: 6, 
        renderCell: (params) => (
          <Button 
              variant="contained" 
              color="secondary" 
              href={params.value} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{fontWeight: 'bold', fontSize: '0.8em'}} // Adjust the value as needed
          >
            Book
          </Button>
        ) 
    }    
];  

function SearchTable({ stays }) {
  const [search, setSearch] = useState("");  // new state variable
  
  stays = stays.map(stay => ({
    ...stay,
    date_range_start: new Date(stay.date_range_start).toISOString().slice(0,10),
    date_range_end: new Date(stay.date_range_end).toISOString().slice(0,10)
  }));

  // filter rows based on search text
  const filteredStays = stays.filter(stay =>
    Object.keys(stay).some(
      (key) =>
        stay[key]
          .toString()
          .toLowerCase()
          .includes(search.toLowerCase())
    )
  );

  return (
    <div style={{ height: 'auto', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1em', alignItems: 'center' }}>
          <span style={{ marginRight: '0.5em' }}>Search:</span>
          <TextField 
              sx={{ width: '15%', '& .MuiInputBase-input': { height: '0.2em' } }}  // Adjust the width to make the search box shorter
              label="" 
              variant="outlined"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
          />
      </div>
      <DataGrid
        rows={filteredStays}  // use filteredStays
        columns={columns}
        getRowId={(row) => row.booking_url}
        pageSize={100}
        rowsPerPageOptions={[10, 20, 50, 100]}
        disableColumnMenu
      />
    </div>
  );
}

export default SearchTable;