import { useState, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Toast from './components/Toast';
import Home from './pages/Home';
import Search from './pages/Search';
import SeatSelection from './pages/SeatSelection';
import MyBookings from './pages/MyBookings';
import BookingDetail from './pages/BookingDetail';
import Admin from './pages/Admin';
import Login from './pages/Login';
import Register from './pages/Register';

export default function App() {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const removeToast = (id) => setToasts(prev => prev.filter(t => t.id !== id));

  return (
    <>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/seats/:scheduleId" element={<SeatSelection addToast={addToast} />} />
          <Route path="/bookings" element={<MyBookings addToast={addToast} />} />
          <Route path="/bookings/:bookingId" element={<BookingDetail addToast={addToast} />} />
          <Route path="/admin" element={<Admin addToast={addToast} />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </main>

      {/* Toast container */}
      <div id="toast-container">
        {toasts.map(t => (
          <Toast key={t.id} message={t.message} type={t.type} onClose={() => removeToast(t.id)} />
        ))}
      </div>
    </>
  );
}
