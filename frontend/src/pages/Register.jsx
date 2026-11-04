import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function Register() {
  const { register, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', phone: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (key) => (e) => setForm(prev => ({ ...prev, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = { ...form, phone: form.phone || null };
      await register(payload);
      await login(form.email, form.password);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card glass-card">
        <h2>Create Account</h2>
        <p className="auth-subtitle">Join BusGo and start booking</p>
        {error && <div className="auth-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="regName">Full Name</label>
            <input id="regName" required maxLength={100} value={form.name} onChange={set('name')} placeholder="John Doe" />
          </div>
          <div className="form-group">
            <label htmlFor="regEmail">Email</label>
            <input id="regEmail" type="email" required value={form.email} onChange={set('email')} placeholder="you@example.com" />
          </div>
          <div className="form-group">
            <label htmlFor="regPhone">Phone (optional)</label>
            <input id="regPhone" type="tel" maxLength={15} value={form.phone} onChange={set('phone')} placeholder="+91 9876543210" />
          </div>
          <div className="form-group">
            <label htmlFor="regPassword">Password</label>
            <input id="regPassword" type="password" required minLength={8} value={form.password} onChange={set('password')} placeholder="Minimum 8 characters" />
          </div>
          <button type="submit" className="btn btn-primary btn-lg btn-block" disabled={loading}>
            {loading ? 'Creating…' : 'Create Account'}
          </button>
        </form>
        <p className="auth-footer">Already have an account? <Link to="/login">Log in</Link></p>
      </div>
    </div>
  );
}
