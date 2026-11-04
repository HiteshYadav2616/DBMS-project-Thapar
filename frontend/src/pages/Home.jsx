import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

export default function Home() {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [date, setDate] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (!source.trim() || !destination.trim()) return;
    const params = new URLSearchParams({ source: source.trim(), destination: destination.trim() });
    if (date) params.set('travel_date', date);
    navigate(`/search?${params}`);
  };

  const swap = () => { setSource(destination); setDestination(source); };

  return (
    <div className="home-page">
      {/* Hero */}
      <section className="hero">
        <div className="hero-bg" />
        <div className="hero-content">
          <h1 className="hero-title">
            Travel Smarter.<br />
            <span className="gradient-text">Book Faster.</span>
          </h1>
          <p className="hero-subtitle">Search hundreds of routes, pick your perfect seat, and book in seconds — all in one place.</p>

          <form className="hero-search-card glass-card" onSubmit={handleSearch}>
            <div className="search-row">
              <div className="search-field">
                <label htmlFor="heroSource">From</label>
                <input id="heroSource" value={source} onChange={e => setSource(e.target.value)} placeholder="e.g. Delhi" autoComplete="off" />
              </div>
              <button type="button" className="swap-btn" onClick={swap} title="Swap">⇄</button>
              <div className="search-field">
                <label htmlFor="heroDest">To</label>
                <input id="heroDest" value={destination} onChange={e => setDestination(e.target.value)} placeholder="e.g. Mumbai" autoComplete="off" />
              </div>
              <div className="search-field">
                <label htmlFor="heroDate">Date</label>
                <input id="heroDate" type="date" value={date} onChange={e => setDate(e.target.value)} />
              </div>
              <button type="submit" className="btn btn-primary btn-lg search-go">Search Buses</button>
            </div>
          </form>
        </div>

        <div className="hero-decor">
          <div className="floating-circle c1" />
          <div className="floating-circle c2" />
          <div className="floating-circle c3" />
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Why Choose <span className="gradient-text">BusGo</span></h2>
          <div className="features-grid">
            {[
              { icon: '🔍', title: 'Smart Search', desc: 'Find the perfect bus in seconds with route and date filters.' },
              { icon: '💺', title: 'Pick Your Seat', desc: 'Interactive seat map lets you choose exactly where you sit.' },
              { icon: '⚡', title: 'Instant Booking', desc: 'Confirm your ticket in one click — no waiting, no hassle.' },
              { icon: '🛡️', title: 'Easy Cancellation', desc: 'Cancel confirmed bookings anytime from your dashboard.' },
            ].map(f => (
              <div className="feature-card glass-card" key={f.title}>
                <div className="feature-icon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
