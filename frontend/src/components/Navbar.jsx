import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const dropRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) setDropdownOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    navigate('/');
  };

  const initials = user ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : '';

  return (
    <nav className="navbar">
      <div className="nav-inner">
        <Link to="/" className="logo" onClick={() => setMobileOpen(false)}>
          <span className="logo-icon">🚌</span>
          <span className="logo-text">Bus<span className="logo-accent">Go</span></span>
        </Link>

        <div className={`nav-links ${mobileOpen ? 'mobile-open' : ''}`}>
          <Link to="/" className="nav-link" onClick={() => setMobileOpen(false)}>Home</Link>
          <Link to="/search" className="nav-link" onClick={() => setMobileOpen(false)}>Search</Link>
          {user && <Link to="/bookings" className="nav-link" onClick={() => setMobileOpen(false)}>My Bookings</Link>}
          {user?.role === 'admin' && <Link to="/admin" className="nav-link" onClick={() => setMobileOpen(false)}>Admin</Link>}
        </div>

        <div className="nav-actions">
          {!user ? (
            <>
              <Link to="/login" className="btn btn-ghost">Log In</Link>
              <Link to="/register" className="btn btn-primary">Sign Up</Link>
            </>
          ) : (
            <div className="user-menu" ref={dropRef}>
              <button className="user-avatar" onClick={() => setDropdownOpen(p => !p)}>{initials}</button>
              {dropdownOpen && (
                <div className="user-dropdown">
                  <div className="dropdown-header">
                    <span className="dropdown-name">{user.name}</span>
                    <span className="dropdown-email">{user.email}</span>
                  </div>
                  <div className="dropdown-divider" />
                  <Link to="/bookings" className="dropdown-item" onClick={() => setDropdownOpen(false)}>My Bookings</Link>
                  <button className="dropdown-item dropdown-logout" onClick={handleLogout}>Log Out</button>
                </div>
              )}
            </div>
          )}
        </div>

        <button className="mobile-toggle" onClick={() => setMobileOpen(p => !p)}>
          <span /><span /><span />
        </button>
      </div>
    </nav>
  );
}
