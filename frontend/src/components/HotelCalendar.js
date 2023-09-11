import React from 'react';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

// Custom Toolbar Component
const CustomToolbar = (toolbar) => {
  return (
    <div className="rbc-toolbar">
      <span className="rbc-btn-group">
        <button type="button" onClick={() => toolbar.onNavigate('PREV')}>←</button>
        <button type="button" onClick={() => toolbar.onNavigate('TODAY')}>Today</button>
        <button type="button" onClick={() => toolbar.onNavigate('NEXT')}>→</button>
      </span>
      <span className="rbc-toolbar-label">{toolbar.label}</span>
      <div style={{ float: 'right' }}>
        <span style={{
          backgroundColor: '#FFFFCC', padding: '10px',
          borderRadius: '5px', marginRight: '10px', color: '#333', fontWeight: 'bold'
        }}>Standard Rate</span>
        <span style={{
          backgroundColor: '#CC99FF', padding: '10px',
          borderRadius: '5px', color: '#333', fontWeight: 'bold'
        }}>Premium Rate</span>
      </div>
    </div>
  );
};

// The HotelCalendar component, now accepting stays as a prop
const HotelCalendar = ({ stays }) => {

  // Convert the stays object to the event list format expected by the Calendar component
  const myEventsList = [];

  stays.forEach(stay => {
    const checkInDate = moment(stay.check_in_date).toDate();
    const checkOutDate = moment(stay.check_in_date).toDate();
    const bookingUrl = stay.booking_url;

    // Handle standard rate
    if (stay.standard_rate > 0) {
      myEventsList.push({
        start: checkInDate,
        end: checkOutDate,
        title: stay.standard_rate.toLocaleString() + " pts",
        style: { backgroundColor: '#FFFFCC', color: '#333', textAlign: 'center', fontWeight: 'bold' },
        bookingUrl: bookingUrl
      });
    }

    // Handle premium rate
    if (stay.premium_rate > 0) {
      myEventsList.push({
        start: checkInDate,
        end: checkOutDate,
        title: stay.premium_rate.toLocaleString() + " pts",
        style: { backgroundColor: '#CC99FF', color: '#333', textAlign: 'center', fontWeight: 'bold' },
        bookingUrl: bookingUrl
      });
    }
  });

  // Event onClick handler
  const handleEventClick = (event) => {
    window.open(event.bookingUrl, '_blank');
  };

  return (
    <div style={{ height: '90vh' }}>
      <Calendar
        localizer={localizer}
        events={myEventsList}
        startAccessor="start"
        endAccessor="end"
        views={['month']}
        components={{
          toolbar: CustomToolbar
        }}
        eventPropGetter={event => ({ style: event.style })}
        onSelectEvent={handleEventClick}
      />
    </div>
  );
};

export default HotelCalendar;