import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { bookingsAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import './MyBookings.css';

export default function MyBookings({ addToast }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    (async () => {
      try {
        const data = await bookingsAPI.list();
        setBookings(data);
      } catch {
        addToast('Failed to load bookings.', 'error');
      } finally {
        setLoading(false);
      }
    })();
  }, [user, navigate, addToast]);

  const statusClass = (s) => `status-badge status-${s}`;

  if (loading) return <div className="container page-padded"><div className="loading-spinner"><div className="spinner" /></div></div>;

  return (
    <div className="bookings-page container page-padded">
      <h2 className="page-title">My Bookings</h2>
      {bookings.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🎫</div>
          <p>You have no bookings yet.</p>
          <button className="btn btn-primary" style={{ marginTop: 20 }} onClick={() => navigate('/search')}>Search Buses</button>
        </div>
      ) : (
        <div className="bookings-list">
          {bookings.map(b => (
            <div className="booking-card" key={b.booking_id} onClick={() => navigate(`/bookings/${b.booking_id}`)}>
              <div className="booking-left">
                <div className="booking-id">Booking #{b.booking_id}</div>
                <div className="booking-schedule-info">Schedule #{b.schedule_id}</div>
                <div className="booking-date">{new Date(b.booking_date).toLocaleString()}</div>
              </div>
              <div className="booking-right">
                <div className="booking-amount">₹{parseFloat(b.total_amount).toFixed(0)}</div>
                <span className={statusClass(b.status)}>{b.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
