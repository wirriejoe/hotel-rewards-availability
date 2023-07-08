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
            { data: 'Premium' },
            {
                data: 'Booking',
                render: function(data, type, row) {
                    return '<a href="' + data + '" class="btn btn-primary" target="_blank">Book Now</a>';
                }
             }
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
            { data: 'premium_rate' },
            {
                data: 'booking_url',
                render: function(data, type, row) {
                    return '<a href="' + data + '" class="btn btn-primary" target="_blank">Book Now</a>';
                }
            }
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
            const processedRecords = records.map(record => ({
                'Date': new Date(record.check_in_date).toISOString().split('T')[0],
                'Last Checked': record.last_checked,
                'Hotel': record.hotel_name,
                'City': record.hotel_city,
                'Country': record.hotel_country,
                'Standard': Math.round(record.standard_rate),
                'Premium': Math.round(record.premium_rate),
                'Booking': record.booking_url
            }));
            console.log("Processed Records:", processedRecords);

            // Add data to table
            table.clear().rows.add(processedRecords).draw();
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
                hotel_city: record.hotel_city,
                // hotel_country: record.hotel_country[0],
                standard_rate: Math.round(record.standard_rate), // Round standard_rate
                premium_rate: Math.round(record.premium_rate), // Round premium_rate
                booking_url: record.booking_url
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