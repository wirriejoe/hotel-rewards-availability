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
    { name: "Hilton", logo: HiltonLogo, status: "supported" },
    { name: "IHG", logo: IHGLogo, status: "supported" },
    { name: "Marriott", logo: MarriottLogo, status: "coming_soon" },
    { name: "Wyndham", logo: WyndhamLogo, status: "coming_soon" },
    { name: "Accor", logo: AccorLogo, status: "coming_soon" },
  ];

  // const features = [
  //   {title: "Lightning fast ⚡︎", description: "No more waiting. We constantly check hotel awards, so you see results immediately."},
  //   {title: "Easy search 😅", description: "No more guessing dates, cities, and unavailable hotels. We built the hotel search tool we wish a hotel did."},
  //   {title: "Explore awards 🌐", description: "Explore brands and categories for the best deals. Sort by standard or premium rates and find the best options."},
  //   {title: "Unlimited alerts 🔔", description: "No more repetitive searches. Create alerts to be notified when the best stays are released."},
  //   {title: "Discord community 🤝", description: 
  //     <span>
  //     <a href="https://discord.gg/CJwvNuRZgu" target="_blank" rel="noreferrer">
  //       Join our Discord
  //     </a>
  //     {' '}community to talk about travel, request new features, or just come hang out.
  //   </span>
  //   },
  //   {title: "Booking links 🔗", description: "Save time and jump directly into the booking flow on the hotel website to lock in your rate."},
  //   {title: "Fresh results 🤩", description: "Results update regularly with the latest award availability from hotel websites. No more checking each rate one at a time."},
  //   {title: "Cents per point (CCP) 🤑", description: "Compare point redemptions with cash rates to find the best bang for your buck every time."},
  // ];

  const featureHighlights = [
    {
      title: "Results in seconds 🗺",
      description: "Daily refreshes, so you can search live awards in seconds."
    },
    {
      title: "10c per point stays 💎",
      description: "Search by cents per point (CCP) to find amazing deals wherever you go."
    },
    {
      title: "Multi-night stays 🏘️",
      description: "Hidden multi-night awards for hard-to-find hotels like Alila Ventana Big Sur."
    },
    {
      title: "Real-time alerts 🕵🏻",
      description: "Setup unlimited alerts. Be the first to know when awards are available."
    },
  ];

  const featureCTAs = [
    {route: '/search', label: '🔍 Search'},
    {route: '/hyatt/explore', label: '🌐 Discover'},
    {route: '/hyatt/hotel/sjcal', label: '🔥 Explore'},
    {route: '/alerts', label: '🔔 Create Alert'}
    // Add more if needed
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
        <h1>Spend 50% less points on your next hotel</h1>
        <p>BurnMyPoints is the fastest search engine for hotel awards. <b>We dig through millions of hotel awards, so you don't have to.</b></p>
        <div style={{
            display: "flex",
            justifyContent: "center",  // Center horizontally
            alignItems: "center",      // Center vertically
            padding: "1%"            // Padding above and below
          }}>
            <div style={{
              position: "relative",
              width: "65%",           // Full width of its container
              paddingBottom: "35%", // 16:9 Aspect Ratio
            }}>
              <iframe 
                src="https://www.loom.com/embed/ab57bd375fff4bcf84ea957e23cbb41d?sid=3c3031e1-b9ff-4308-8589-d9c829e9338f"
                webkitallowfullscreen 
                frameBorder="0"
                mozallowfullscreen 
                allowfullscreen 
                style={{
                  position: "absolute",
                  top: "0",
                  left: "0",
                  width: "100%",
                  height: "100%"
                }}
              ></iframe>
            </div>
          </div>
        {/* <Link to='/explore' className='btn btn-primary btn-lg btn-space' role='button'>
            🌐 Discover
        </Link>
        <Link to='/search' className='btn btn-secondary btn-lg' role='button'>
            🔍 Search
        </Link> */}
        <div class="alert alert-info">
          <b>🎉 BurnMyPoints now supports World of Hyatt, Hilton Honors, and IHG One Rewards!</b> Search across thousands of hotels for up to 360 days in the future. Join the conversation at <a href="https://discord.gg/CJwvNuRZgu">Discord</a>.
          <br/>
        </div>
      </div>
      <div className="home-container">
        <h1 style={{textAlign: "left"}}>Highlights</h1> {/* Align the title to the left */}
        <div className="features-container">
          {featureHighlights.map((feature, index) => (
            <div className="feature" key={index} style={{textAlign: "left"}}>
              <h5>{feature.title}</h5>
              <p>{feature.description}</p>
              {/* Check if the CTA object and its 'route' property exist */}
              {featureCTAs[index]?.route && 
                <Link to={featureCTAs[index].route} className='btn btn-primary' role='button'>
                  {featureCTAs[index].label}
                </Link>
              }
            </div>
          ))}
        </div>
      </div>

      <div className="home-container"> {/* New Section */}
        <h1>Supported reward programs</h1>
        <p>The hotel rewards programs we currently support and will support soon in the coming weeks! Come tell us on Discord what program we should add next.{' '}
        <a href="https://discord.gg/CJwvNuRZgu" target="_blank" rel="noreferrer">
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