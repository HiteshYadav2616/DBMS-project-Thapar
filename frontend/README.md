# BusGo — React Frontend

Modern React frontend for the Bus Travel Booking System API. Built with **Vite + React + React Router**.

## Features

- 🏠 **Home** — Hero section with instant search
- 🔍 **Search** — Find buses by source, destination & date
- 💺 **Seat Selection** — Interactive seat map with real-time availability
- 🎫 **My Bookings** — View all bookings with status badges
- 📋 **Booking Detail** — Full booking info with cancel option
- 🔐 **Auth** — Register, Login, auto token management
- 🛠️ **Admin Panel** — Add buses, routes, schedules (admin only)
- 🌙 **Dark Theme** — Premium glassmorphism UI

## Prerequisites

- **Node.js** 18+ and **npm**
- Backend API running at `http://127.0.0.1:8000` (see `backend/README.md`)

## Quick Start

```powershell
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the dev server
npm run dev
```

The app opens at **http://localhost:5173**.

## Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx              # Entry point (BrowserRouter + AuthProvider)
    ├── App.jsx               # Routes and toast system
    ├── api.js                # API layer (all backend endpoints)
    ├── index.css             # Global design tokens and base styles
    ├── context/
    │   └── AuthContext.jsx   # Auth state (JWT, user, login/logout)
    ├── components/
    │   ├── Navbar.jsx/.css   # Navigation bar with avatar dropdown
    │   └── Toast.jsx/.css    # Toast notification component
    └── pages/
        ├── Home.jsx/.css     # Landing page with hero + features
        ├── Search.jsx/.css   # Schedule search results
        ├── SeatSelection.jsx/.css  # Interactive seat picker
        ├── MyBookings.jsx/.css     # Booking list
        ├── BookingDetail.jsx/.css  # Single booking view + cancel
        ├── Admin.jsx/.css    # Admin forms (bus, route, schedule)
        ├── Login.jsx         # Login form
        ├── Register.jsx      # Registration form
        └── Auth.css          # Shared auth page styles
```

## API Configuration

The API base URL is set in `src/api.js`:

```js
const API_BASE = 'http://127.0.0.1:8000';
```

Change this if your backend runs on a different host/port.

## Notes

- The backend must have CORS enabled for the frontend origin (`http://localhost:5173`).
  If not already set up, add CORS middleware to the FastAPI backend:
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:5173"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- The first user must be promoted to admin via SQL to access the Admin panel.
- Payments are simulated — no real charges.
