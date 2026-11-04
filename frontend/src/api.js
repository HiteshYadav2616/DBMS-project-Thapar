const API_BASE = import.meta.env.VITE_API_BASE ?? '';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const msg = typeof body.detail === 'string' ? body.detail : body.detail?.message || res.statusText;
    throw new Error(msg);
  }
  return res.json();
}

/* ── Auth ── */
export const authAPI = {
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/auth/me'),
};

/* ── Schedules / Catalog ── */
export const catalogAPI = {
  searchSchedules: (source, destination, travelDate) => {
    const params = new URLSearchParams({ source, destination });
    if (travelDate) params.set('travel_date', travelDate);
    return request(`/schedules?${params}`);
  },
  getSeatAvailability: (scheduleId) => request(`/schedules/${scheduleId}/seats`),
};

/* ── Bookings ── */
export const bookingsAPI = {
  create: (data) => request('/bookings', { method: 'POST', body: JSON.stringify(data) }),
  list: () => request('/bookings'),
  get: (id) => request(`/bookings/${id}`),
  cancel: (id) => request(`/bookings/${id}/cancel`, { method: 'POST' }),
};

/* ── Admin ── */
export const adminAPI = {
  createBus: (data) => request('/admin/buses', { method: 'POST', body: JSON.stringify(data) }),
  createRoute: (data) => request('/admin/routes', { method: 'POST', body: JSON.stringify(data) }),
  createSchedule: (data) => request('/admin/schedules', { method: 'POST', body: JSON.stringify(data) }),
};
