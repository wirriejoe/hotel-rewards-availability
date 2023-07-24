import React from 'react';
import { Link } from 'react-router-dom';
import '../App.css';
import AccorLogo from '../hotels/Accor.png';  
import HiltonLogo from '../hotels/Hilton.png';  
import HyattLogo from '../hotels/Hyatt.png';  
import IHGLogo from '../hotels/IHG.png';  
import MarriottLogo from '../hotels/Marriott.png';  
import WyndhamLogo from '../hotels/Wyndham.png'; 

function HomePage() {

  // Define hotels and their status
  const hotels = [
    { name: "Hyatt", logo: HyattLogo, status: "supported" },
    { name: "Accor", logo: AccorLogo, status: "coming_soon" },
    { name: "Hilton", logo: HiltonLogo, status: "coming_soon" },
    { name: "IHG", logo: IHGLogo, status: "coming_soon" },
    { name: "Marriott", logo: MarriottLogo, status: "coming_soon" },
    { name: "Wyndham", logo: WyndhamLogo, status: "coming_soon" },
  ];

  const features = [
    {title: "Lightning fast ⚡︎", description: "No more waiting. We constantly check hotel awards, so you see results immediately."},
    {title: "Easy search 😅", description: "No more guessing dates, cities, and unavailable hotels. We built the hotel search tool we wish a hotel did."},
    {title: "Explore awards 🌐", description: "Explore brands and categories for the best deals. Sort by standard or premium rates and find the best options."},
    {title: "Unlimited alerts 🔔 (Coming Soon)", description: "No more repetitive searches. Create alerts to be notified when the best seats are released."},
    {title: "Discord community 🤝", description: 
      <span>
      <a href="https://discord.gg/M6zexyPYk" target="_blank" rel="noreferrer">
        Join our Discord
      </a>
      {' '}community to talk about travel, request new features, or just come hang out.
    </span>
    },
    {title: "Booking links 🔗", description: "Save time and jump directly into the booking flow on the hotel website to lock in your rate."},
    {title: "Fresh results 🤩", description: "Results update regularly with the latest award availability from hotel websites. No more checking each rate one at a time."},
    {title: "Deals tracker 🤑 (Coming Soon)", description: "Compare point redemptions with cash rates to find the best bang for your buck every time."},
];

  // Handle logo click
  const handleLogoClick = (hotel) => {
      if (hotel.status === "supported") {
          console.log(`Clicked on ${hotel.name}`);
          // Navigate to a page or perform an action based on the clicked hotel
      }
  };

  const [hoveredHotel, setHoveredHotel] = React.useState(null);

  return (
    <div>
      <div className="home-container">
        <h2>Discover the best hotels for your points.</h2>
        <p>BurnMyPoints is the fastest search engine for hotel awards. Explore availability across entire award categories or brands and search with instant results to find the best hotels for your points.</p>
        <Link to='/explore' className='btn btn-primary btn-lg btn-space' role='button'>
            🌐 Discover
        </Link>
        <Link to='/search' className='btn btn-secondary btn-lg' role='button'>
            🔍 Search
        </Link>
      </div>

      <div class="alert alert-info">
        <strong>BETA! </strong>
        BurnMyPoints currently scans next 60 days of award availability for Hyatt. Extended availability and more hotels coming soon! Join the conversation in our <a href="https://discord.gg/M6zexyPYk">Discord</a>.
        <strong> Disclaimer:</strong> BurnMyPoints is not partnered or affiliated with Seats.aero.
      </div>

      <div className= "home-container">
        <h2>Highlights</h2>
        <div className="features-container">
          {features.map((feature, index) => (
            <div className="feature" key={index}>
              <h5>{feature.title}</h5>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="home-container"> {/* New Section */}
        <h2>Supported reward programs</h2>
        <p>The hotel rewards programs we currently support and will support soon in the coming weeks! Come tell us on Discord what program we should add next.{' '}
        <a href="https://discord.gg/M6zexyPYk" target="_blank" rel="noreferrer">
          Join here 👈🏻
        </a>
        </p>

        <div className="brands-container">
          {hotels.map((hotel) => (
            <div 
              className={`hotel-logo ${hotel.status === "supported" ? "active" : "inactive"}`}
              onMouseEnter={() => setHoveredHotel(hotel.name)}
              onMouseLeave={() => setHoveredHotel(null)}
            >
              <img
                key={hotel.name}
                src={hotel.logo}
                alt={hotel.name}
                onClick={() => handleLogoClick(hotel)}
              />
              {hoveredHotel === hotel.name && (
                <div className="overlay">
                  {hotel.status === "supported" ? "Available" : "Coming Soon"}
                </div>
              )}
            </div>
          ))} 
        </div>
      </div>
    </div>
  );
}

export default HomePage;