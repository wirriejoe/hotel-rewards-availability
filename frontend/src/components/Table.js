import React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';

const columns = [
    { field: 'date_range_start', headerName: 'Check In Date', sortable: true, flex: 6 },
    { field: 'date_range_end', headerName: 'Check Out Date', sortable: true, flex: 6 },
    { field: 'last_checked', headerName: 'Last Checked', sortable: true, flex: 6 },
    {
        field: 'hotel_name', 
        headerName: 'Hotel Name', 
        sortable: true, 
        flex: 16,
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
        field: 'hotel_country', 
        headerName: 'Country', 
        sortable: true, 
        flex: 8,
        renderCell: (params) => (
          <Tooltip title={params.value}>
            <div>{params.value}</div>
          </Tooltip>
        )
    }, 
    {
        field: 'hotel_region', 
        headerName: 'Region', 
        sortable: true, 
        flex: 8,
        renderCell: (params) => (
          <Tooltip title={params.value}>
            <div>{params.value}</div>
          </Tooltip>
        )
    }, 
    {
        field: 'award_category', 
        headerName: 'Category', 
        sortable: true, 
        flex: 8,
        renderCell: (params) => (
          <Tooltip title={params.value}>
            <div>{params.value}</div>
          </Tooltip>
        )
    }, 
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

function Table({ stays }) {

  stays = stays.map(stay => ({
    ...stay,
    date_range_start: new Date(stay.date_range_start).toISOString().slice(0,10),
    date_range_end: new Date(stay.date_range_end).toISOString().slice(0,10)
  }));

  return (
    <div style={{ height: 'auto', width: '100%' }}>
      <DataGrid
        rows={stays}
        columns={columns}
        getRowId={(row) => row.booking_url} // Specify the 'booking_url' as unique identifier
        pageSize={100}
        rowsPerPageOptions={[10, 20, 50, 100]}
        // enableColumnMenu
        disableColumnMenu
      />
    </div>
  );
}

export default Table;