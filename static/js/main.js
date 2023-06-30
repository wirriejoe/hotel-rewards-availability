$(document).ready(function() {
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

    $('#search-form').submit(function(e) {
        e.preventDefault();

        // Get form data
        const data = {
            startDate: $('#start-date').val(),
            endDate: $('#end-date').val(),
            hotel: $('#hotel').val(),
            city: $('#city').val()
        };
        
        console.log("Form data:", data);  // log form data

        // Send a POST request to the server
        fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            console.log("Response:", response);  // log response
            return response.json();
        })
        .then(records => {
            console.log("Records:", records);  // log records
            
            // Flatten Hotel, City, and Country arrays before adding to table
            const flattenedRecords = records.map(record => ({
                ...record
                // Hotel: record.Hotel,
                // City: record.City,
                // Country: record.Country,
            }));
            
            table.clear();
            table.rows.add(flattenedRecords);
            table.draw();
        });
    });
});