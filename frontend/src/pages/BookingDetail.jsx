import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { bookingsAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import './BookingDetail.css';

export default function BookingDetail({ addToast }) {
  const { bookingId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    (async () => {
      try {
        const data = await bookingsAPI.get(bookingId);
        setBooking(data);
      } catch {
        addToast('Booking not found.', 'error');
        navigate('/bookings');
      } finally {
        setLoading(false);
      }
    })();
  }, [bookingId, user, navigate, addToast]);

  const handleCancel = async () => {
    setCancelling(true);
    try {
      const data = await bookingsAPI.cancel(bookingId);
      setBooking(data);
      addToast('Booking cancelled successfully.', 'success');
    } catch (err) {
      addToast(err.message, 'error');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) return <div className="container page-padded"><div className="loading-spinner"><div className="spinner" /></div></div>;
  if (!booking) return null;

  const statusClass = `status-badge status-${booking.status}`;

  return (
    <div className="detail-page container page-padded">
      <button className="btn btn-ghost back-btn" onClick={() => navigate('/bookings')}>← Back to bookings</button>
      <h2 className="page-title">Booking Details</h2>

      <div className="booking-detail-card glass-card">
        <div className="detail-header">
          <h3>Booking #{booking.booking_id}</h3>
          <span className={statusClass}>{booking.status}</span>
        </div>

        <div className="detail-section">
          <h4>Booking Info</h4>
          <div className="detail-grid">
            <div className="detail-item"><label>Schedule ID</label><span>#{booking.schedule_id}</span></div>
            <div className="detail-item"><label>Booking Date</label><span>{new Date(booking.booking_date).toLocaleString()}</span></div>
            <div className="detail-item"><label>Total Amount</label><span className="amount-highlight">₹{parseFloat(booking.total_amount).toFixed(2)}</span></div>
          </div>
        </div>

        <div className="detail-section">
          <h4>Seats</h4>
          <div className="detail-seats">
            {booking.seats.map(s => (
              <span key={s.seat_id} className="detail-seat-chip">
                Seat #{s.seat_id} — ₹{parseFloat(s.ticket_price).toFixed(0)}
              </span>
            ))}
          </div>
        </div>

        <div className="detail-section">
          <h4>Payment</h4>
          <div className="detail-grid">
            <div className="detail-item"><label>Payment ID</label><span>#{booking.payment.payment_id}</span></div>
            <div className="detail-item"><label>Amount</label><span>₹{parseFloat(booking.payment.amount).toFixed(2)}</span></div>
            <div className="detail-item"><label>Method</label><span>{booking.payment.payment_method || 'Simulated'}</span></div>
            <div className="detail-item">
              <label>Status</label>
              <span className={`payment-status ps-${booking.payment.payment_status}`}>{booking.payment.payment_status}</span>
            </div>
          </div>
        </div>

        {booking.status === 'Confirmed' && (
          <button className="btn btn-danger btn-lg cancel-btn" onClick={handleCancel} disabled={cancelling}>
            {cancelling ? 'Cancelling…' : 'Cancel Booking'}
          </button>
        )}
      </div>
    </div>
  );
}
