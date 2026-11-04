import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminAPI } from '../api';
import './Admin.css';

export default function Admin({ addToast }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('buses');

  if (!user || user.role !== 'admin') {
    return (
      <div className="container page-padded">
        <div className="empty-state">
          <div className="empty-icon">🔒</div>
          <p>Administrator access required.</p>
          <button className="btn btn-primary" style={{ marginTop: 20 }} onClick={() => navigate('/')}>Go Home</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page container page-padded">
      <h2 className="page-title">Admin Panel</h2>
      <div className="admin-tabs">
        {[['buses', 'Bus'], ['routes', 'Route'], ['schedules', 'Schedule']].map(([key, label]) => (
          <button key={key} className={`tab-btn ${tab === key ? 'active' : ''}`} onClick={() => setTab(key)}>
            Add {label}
          </button>
        ))}
      </div>

      {tab === 'buses' && <BusForm addToast={addToast} />}
      {tab === 'routes' && <RouteForm addToast={addToast} />}
      {tab === 'schedules' && <ScheduleForm addToast={addToast} />}
    </div>
  );
}

function BusForm({ addToast }) {
  const [form, setForm] = useState({ bus_number: '', bus_type: '', total_seats: '' });
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault(); setLoading(true);
    try {
      const payload = { bus_number: form.bus_number, bus_type: form.bus_type || null, total_seats: parseInt(form.total_seats) };
      await adminAPI.createBus(payload);
      addToast('Bus added successfully!', 'success');
      setForm({ bus_number: '', bus_type: '', total_seats: '' });
    } catch (err) { addToast(err.message, 'error'); }
    finally { setLoading(false); }
  };

  return (
    <div className="admin-form glass-card">
      <h3>Register a New Bus</h3>
      <form onSubmit={submit}>
        <div className="form-group"><label>Bus Number</label><input required maxLength={30} value={form.bus_number} onChange={set('bus_number')} placeholder="e.g. DL-01-AB-1234" /></div>
        <div className="form-group"><label>Bus Type</label><input maxLength={50} value={form.bus_type} onChange={set('bus_type')} placeholder="e.g. AC Sleeper" /></div>
        <div className="form-group"><label>Total Seats</label><input type="number" required min={1} max={300} value={form.total_seats} onChange={set('total_seats')} placeholder="e.g. 40" /></div>
        <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>{loading ? 'Adding…' : 'Add Bus'}</button>
      </form>
    </div>
  );
}

function RouteForm({ addToast }) {
  const [form, setForm] = useState({ source: '', destination: '', distance: '' });
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault(); setLoading(true);
    try {
      const payload = { source: form.source, destination: form.destination, distance: form.distance ? parseFloat(form.distance) : null };
      await adminAPI.createRoute(payload);
      addToast('Route added successfully!', 'success');
      setForm({ source: '', destination: '', distance: '' });
    } catch (err) { addToast(err.message, 'error'); }
    finally { setLoading(false); }
  };

  return (
    <div className="admin-form glass-card">
      <h3>Create a New Route</h3>
      <form onSubmit={submit}>
        <div className="form-group"><label>Source</label><input required maxLength={100} value={form.source} onChange={set('source')} placeholder="e.g. Delhi" /></div>
        <div className="form-group"><label>Destination</label><input required maxLength={100} value={form.destination} onChange={set('destination')} placeholder="e.g. Mumbai" /></div>
        <div className="form-group"><label>Distance (km) — optional</label><input type="number" min={0} step="0.01" value={form.distance} onChange={set('distance')} placeholder="e.g. 1400" /></div>
        <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>{loading ? 'Adding…' : 'Add Route'}</button>
      </form>
    </div>
  );
}

function ScheduleForm({ addToast }) {
  const [form, setForm] = useState({ bus_id: '', route_id: '', travel_date: '', departure_time: '', arrival_time: '', fare: '' });
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault(); setLoading(true);
    try {
      const payload = {
        bus_id: parseInt(form.bus_id), route_id: parseInt(form.route_id),
        travel_date: form.travel_date, departure_time: form.departure_time + ':00',
        arrival_time: form.arrival_time + ':00', fare: parseFloat(form.fare),
      };
      await adminAPI.createSchedule(payload);
      addToast('Schedule added successfully!', 'success');
      setForm({ bus_id: '', route_id: '', travel_date: '', departure_time: '', arrival_time: '', fare: '' });
    } catch (err) { addToast(err.message, 'error'); }
    finally { setLoading(false); }
  };

  return (
    <div className="admin-form glass-card">
      <h3>Create a New Schedule</h3>
      <form onSubmit={submit}>
        <div className="form-group"><label>Bus ID</label><input type="number" required min={1} value={form.bus_id} onChange={set('bus_id')} placeholder="e.g. 1" /></div>
        <div className="form-group"><label>Route ID</label><input type="number" required min={1} value={form.route_id} onChange={set('route_id')} placeholder="e.g. 1" /></div>
        <div className="form-group"><label>Travel Date</label><input type="date" required value={form.travel_date} onChange={set('travel_date')} /></div>
        <div className="form-row">
          <div className="form-group"><label>Departure Time</label><input type="time" required value={form.departure_time} onChange={set('departure_time')} /></div>
          <div className="form-group"><label>Arrival Time</label><input type="time" required value={form.arrival_time} onChange={set('arrival_time')} /></div>
        </div>
        <div className="form-group"><label>Fare (₹)</label><input type="number" required min={0} step="0.01" value={form.fare} onChange={set('fare')} placeholder="e.g. 750" /></div>
        <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>{loading ? 'Adding…' : 'Add Schedule'}</button>
      </form>
    </div>
  );
}
