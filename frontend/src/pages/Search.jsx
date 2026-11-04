import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { catalogAPI } from '../api';
import './Search.css';

export default function Search() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const [source, setSource] = useState(params.get('source') || '');
  const [destination, setDestination] = useState(params.get('destination') || '');
  const [date, setDate] = useState(params.get('travel_date') || '');
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const s = params.get('source'), d = params.get('destination');
    if (s && d) {
      setSource(s); setDestination(d);
      setDate(params.get('travel_date') || '');
      doSearch(s, d, params.get('travel_date') || '');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.toString()]);

  const doSearch = async (src, dest, dt) => {
    setLoading(true);
    try {
      const data = await catalogAPI.searchSchedules(src, dest, dt || null);
      setResults(data);
      setSearched(true);
    } catch {
      setResults([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!source.trim() || !destination.trim()) return;
    const p = new URLSearchParams({ source: source.trim(), destination: destination.trim() });
    if (date) p.set('travel_date', date);
    navigate(`/search?${p}`);
  };

  const swap = () => { setSource(destination); setDestination(source); };

  const formatTime = (t) => {
    if (!t) return '';
    const [h, m] = t.split(':');
    const hr = parseInt(h, 10);
    const ampm = hr >= 12 ? 'PM' : 'AM';
    return `${hr % 12 || 12}:${m} ${ampm}`;
  };

  return (
    <div className="search-page container page-padded">
      <h2 className="page-title">Search Buses</h2>

      <form className="search-bar-inline glass-card" onSubmit={handleSubmit}>
        <div className="search-row">
          <div className="search-field">
            <label>From</label>
            <input value={source} onChange={e => setSource(e.target.value)} placeholder="Source city" />
          </div>
          <button type="button" className="swap-btn" onClick={swap}>⇄</button>
          <div className="search-field">
            <label>To</label>
            <input value={destination} onChange={e => setDestination(e.target.value)} placeholder="Destination city" />
          </div>
          <div className="search-field">
            <label>Date</label>
            <input type="date" value={date} onChange={e => setDate(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary">Search</button>
        </div>
      </form>

      {loading && <div className="loading-spinner"><div className="spinner" /></div>}

      {!loading && searched && results.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🚌</div>
          <p>No buses found for this route. Try different cities or dates.</p>
        </div>
      )}

      {!loading && !searched && (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <p>Enter a source and destination to find available buses.</p>
        </div>
      )}

      <div className="results-list">
        {results.map(s => (
          <div className="result-card" key={s.schedule_id} onClick={() => navigate(`/seats/${s.schedule_id}`, { state: s })}>
            <div className="result-route">
              <div className="result-cities">
                <span>{s.source}</span>
                <span className="result-arrow">→</span>
                <span>{s.destination}</span>
              </div>
              <div className="result-meta">
                <span>🚌 {s.bus_number}{s.bus_type ? ` • ${s.bus_type}` : ''}</span>
                <span>📅 {s.travel_date}</span>
                <span>🕐 {formatTime(s.departure_time)} — {formatTime(s.arrival_time)}</span>
              </div>
            </div>
            <div className="result-price">
              <div className="price-value">₹{parseFloat(s.fare).toFixed(0)}</div>
              <div className="price-label">per seat</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
