$(document).ready(function() {
    // Initialize first DataTable
    const table = $('#search-table').DataTable({
        columns: [
            { data: 'Date' },
            { data: 'Last Checked' },
            { data: 'Hotel' },
            { data: 'City' },
            { data: 'Country' },
            { data: 'Standard' },
            { data: 'Premium' }
        ]
    });

    // Initialize second DataTable
    const consecutiveStaysTable = $('#consecutive-stays-table').DataTable({
        columns: [
            { data: 'date_range_start' },
            { data: 'date_range_end' },
            { data: 'last_checked' },
            { data: 'hotel_name' },
            { data: 'hotel_city' },
            // { data: 'hotel_country' },
            { data: 'standard_rate' },
            { data: 'premium_rate' }
        ]
    });

    $('#search-form').submit(function(e) {
        e.preventDefault();

        // Get form data
        const data = {
            startDate: $('#start-date').val(),
            endDate: $('#end-date').val(),
            hotel: $('#hotel').val(),
            city: $('#city').val()
        };
        
        console.log("Form data:", data);

        // Send a POST request to the server
        fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            console.log("Response:", response);
            return response.json();
        })
        .then(records => {
            console.log("Records:", records);
            
            // Add data to table
            table.clear().rows.add(records).draw();
        });

    });

    $('#consecutive-stays-form').submit(function(e) {
        e.preventDefault();

        // Get form data
        const data = {
            startDate: $('#cs-start-date').val(),
            endDate: $('#cs-end-date').val(),
            lengthOfStay: $('#cs-length-of-stay').val(),
            hotel: $('#cs-hotel').val(),
            city: $('#cs-city').val(),
            country: $('#cs-country').val(),
            rateFilter: $('#cs-rate-filter').val(),
            pointsBudget: $('#cs-points-budget').val(),
        };

        console.log("Consecutive stays form data:", data);

        // Send a POST request to the server
        fetch('/api/consecutive_stays', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            console.log("Response:", response);
            return response.json();
        })
        .then(records => {
            console.log("Consecutive stays records:", records);
            const processedRecords = records.map(record => ({
                ...record,
                date_range_start: new Date(record.date_range_start).toISOString().split('T')[0],
                date_range_end: new Date(record.date_range_end).toISOString().split('T')[0],
                hotel_city: record.hotel_city[0],
                // hotel_country: record.hotel_country[0],
                standard_rate: Math.round(record.standard_rate), // Round standard_rate
                premium_rate: Math.round(record.premium_rate) // Round premium_rate
            }));

            consecutiveStaysTable.clear();
            consecutiveStaysTable.rows.add(processedRecords);
            consecutiveStaysTable.columns.adjust().draw();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});