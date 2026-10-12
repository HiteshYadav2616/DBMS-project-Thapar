# Bus booking backend

FastAPI + SQLAlchemy backend for the bus reservation ER diagram. MySQL tables are
created from the SQLAlchemy models when the app starts; create the MySQL database
first.

## Run locally

1. Create a MySQL database named `bus_booking` (or update `DB_NAME`).
2. Copy `.env.example` to `.env`, set the database credentials, and set
   `SECRET_KEY` to a private random value. Generate one with
   `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
3. From this directory, install dependencies and start the API:

   ```powershell
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

   If you do not have a virtual environment yet, create one with
   `python -m venv .venv` first.
4. Open `http://127.0.0.1:8000/docs` for interactive API documentation.

The first user can be promoted to administrator directly in MySQL after
registering:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
```

Admin users create buses, routes, and schedules. Bus creation also creates
numbered seats (`1` through `total_seats`). Public registration always creates
a regular user; it cannot assign the admin role. Supported bus types are
`ac_seater`, `non_ac_seater`, `ac_sleeper`, and `non_ac_sleeper`.
Schedule timestamps are stored as UTC; timestamps with an offset are converted
to UTC, and timestamps without an offset are treated as UTC.

## Main endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Get a bearer access token |
| `GET` | `/auth/me` | Get the signed-in user |
| `POST` | `/admin/buses` | Add a bus and its seats (admin) |
| `POST` | `/admin/routes` | Add a route (admin) |
| `POST` | `/admin/schedules` | Add a schedule (admin) |
| `GET` | `/schedules` | Search by `source_city`, `destination_city`, and optional `travel_date` (`YYYY-MM-DD`) |
| `GET` | `/schedules/{schedule_id}/seats` | List seats and availability |
| `POST` | `/bookings` | Reserve seats and record a simulated successful payment |
| `GET` | `/bookings` | List the signed-in user's bookings |
| `GET` | `/bookings/{booking_id}` | Get a booking |
| `POST` | `/bookings/{booking_id}/cancel` | Cancel a confirmed booking |
| `GET` | `/health/db` | Check the MySQL connection |

Pass the login token as `Authorization: Bearer <token>`. Booking requests lock
the schedule row while checking seat availability and writing the booking,
booking-seat, and payment records in one transaction. Cancelled seats become
available again; the successful payment record is retained as a transaction
history entry. Payments are simulated and do not charge a real payment method.
