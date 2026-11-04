import { useState, useEffect, useCallback } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { catalogAPI, bookingsAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import './SeatSelection.css';

export default function SeatSelection({ addToast }) {
  const { scheduleId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const schedule = location.state || null;
  const [seats, setSeats] = useState([]);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);

  const fetchSeats = useCallback(async () => {
    setLoading(true);
    try {
      const data = await catalogAPI.getSeatAvailability(scheduleId);
      setSeats(data);
    } catch {
      addToast('Failed to load seats.', 'error');
    } finally {
      setLoading(false);
    }
  }, [scheduleId, addToast]);

  useEffect(() => { fetchSeats(); }, [fetchSeats]);

  const toggleSeat = (seat) => {
    if (!seat.available) return;
    setSelected(prev =>
      prev.includes(seat.seat_id)
        ? prev.filter(id => id !== seat.seat_id)
        : [...prev, seat.seat_id]
    );
  };

  const fare = schedule ? parseFloat(schedule.fare) : 0;
  const total = selected.length * fare;

  const handleConfirm = async () => {
    if (!user) { navigate('/login'); return; }
    if (selected.length === 0) return;
    setBooking(true);
    try {
      const res = await bookingsAPI.create({ schedule_id: parseInt(scheduleId), seat_ids: selected });
      addToast('Booking confirmed! 🎉', 'success');
      navigate(`/bookings/${res.booking_id}`);
    } catch (err) {
      addToast(err.message, 'error');
    } finally {
      setBooking(false);
    }
  };

  const formatTime = (t) => {
    if (!t) return '';
    const [h, m] = t.split(':');
    const hr = parseInt(h, 10);
    return `${hr % 12 || 12}:${m} ${hr >= 12 ? 'PM' : 'AM'}`;
  };

  return (
    <div className="seats-page container page-padded">
      <button className="btn btn-ghost back-btn" onClick={() => navigate(-1)}>← Back to results</button>
      <h2 className="page-title">Select Your Seats</h2>

      {loading ? (
        <div className="loading-spinner"><div className="spinner" /></div>
      ) : (
        <div className="seats-layout">
          {/* Schedule Info */}
          <div className="schedule-info glass-card">
            <h3>Trip Details</h3>
            {schedule ? (
              <>
                <div className="info-row"><span className="info-label">Route</span><span className="info-value">{schedule.source} → {schedule.destination}</span></div>
                <div className="info-row"><span className="info-label">Bus</span><span className="info-value">{schedule.bus_number}</span></div>
                {schedule.bus_type && <div className="info-row"><span className="info-label">Type</span><span className="info-value">{schedule.bus_type}</span></div>}
                <div className="info-row"><span className="info-label">Date</span><span className="info-value">{schedule.travel_date}</span></div>
                <div className="info-row"><span className="info-label">Departure</span><span className="info-value">{formatTime(schedule.departure_time)}</span></div>
                <div className="info-row"><span className="info-label">Arrival</span><span className="info-value">{formatTime(schedule.arrival_time)}</span></div>
                <div className="info-row"><span className="info-label">Fare</span><span className="info-value fare-highlight">₹{fare}</span></div>
              </>
            ) : (
              <p className="muted">Schedule details unavailable.</p>
            )}
          </div>

          {/* Seat Map */}
          <div className="seat-map-container glass-card">
            <div className="seat-legend">
              <span className="legend-item"><span className="legend-box available" /> Available</span>
              <span className="legend-item"><span className="legend-box selected" /> Selected</span>
              <span className="legend-item"><span className="legend-box occupied" /> Occupied</span>
            </div>
            <div className="bus-frame">
              <div className="bus-steering">🛞 Driver</div>
              <div className="seat-grid">
                {seats.map(seat => (
                  <button
                    key={seat.seat_id}
                    className={`seat-btn ${!seat.available ? 'occupied' : ''} ${selected.includes(seat.seat_id) ? 'selected' : ''}`}
                    onClick={() => toggleSeat(seat)}
                    disabled={!seat.available}
                    title={`Seat ${seat.seat_number}${!seat.available ? ' (Booked)' : ''}`}
                  >
                    {seat.seat_number}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Booking Summary */}
          <div className="booking-summary glass-card">
            <h3>Booking Summary</h3>
            {selected.length === 0 ? (
              <p className="muted">Select seats to see the summary.</p>
            ) : (
              <>
                <div className="summary-row"><span>Selected Seats</span><span>{selected.length}</span></div>
                <div className="summary-row"><span>Fare per seat</span><span>₹{fare}</span></div>
                <div className="summary-row total"><span>Total</span><span className="total-value">₹{total.toFixed(2)}</span></div>
                <div className="selected-seats-chips">
                  {seats.filter(s => selected.includes(s.seat_id)).map(s => (
                    <span key={s.seat_id} className="seat-chip">Seat {s.seat_number}</span>
                  ))}
                </div>
              </>
            )}
            <button
              className="btn btn-primary btn-lg btn-block confirm-btn"
              disabled={selected.length === 0 || booking}
              onClick={handleConfirm}
            >
              {booking ? 'Booking…' : `Confirm & Pay ₹${total.toFixed(0)}`}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
