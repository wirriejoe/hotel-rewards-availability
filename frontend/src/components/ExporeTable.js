import React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import { styled } from '@mui/system';

const CustomTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))({
  '& .MuiTooltip-tooltip': {
    backgroundColor: 'black',
    color: 'white',
  },
});

const columns = [
    { field: 'check_in_date', headerName: 'Date', sortable: true, flex: 6 },
    { field: 'last_checked', headerName: 'Last Checked', sortable: true, flex: 6 },
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
              <div>{row.hotel_name}</div>
              <div>{row.hotel_city}, {row.hotel_country}, {row.hotel_region}</div>
              <div>Award Category: {row.award_category}</div>
            </React.Fragment>
          }>
            <div>{params.value}</div>
          </CustomTooltip>
        );
      },
    },
    { field: 'brand', headerName: 'Brand', sortable: true, flex: 6 },
    { field: 'award_category', headerName: 'Award Category', sortable: true, flex: 6 },
    {
        field: 'standard_rate', 
        headerName: 'Standard Rate', 
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
        headerName: 'Premium Rate', 
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
        headerName: 'Booking URL', 
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

function ExploreTable({ stays }) {
  stays = stays.map(stay => ({
    ...stay,
    check_in_date: new Date(stay.check_in_date).toISOString().slice(0,10),
  }));

  return (
    <div style={{ height: 'auto', width: '100%' }}>
      <DataGrid
        rows={stays}
        columns={columns}
        getRowId={(row) => row.stay_id}
        pageSize={100}
        rowsPerPageOptions={[10, 20, 50, 100]}
        disableColumnMenu
      />
    </div>
  );
}

export default ExploreTable;