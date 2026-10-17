# Bus booking backend

FastAPI + SQLAlchemy backend for the bus reservation schema. Create the database
and tables from the supplied SQL schema before running the API. The application
does not create or alter tables on startup.

## Run locally

1. Create a MySQL database named `bus_booking` (or update `DB_NAME`).
2. Copy `.env.example` to `.env`, set the database credentials, and set
   `SECRET_KEY` to a private random value. Generate one with
   `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
3. From this directory, install dependencies and apply the explicit migration.
   It adds the `role` column used by admin-only endpoints to the existing
   `Users` table:

   ```powershell
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

   If you do not have a virtual environment yet, create one with
   `python -m venv .venv` first.
4. Check `http://127.0.0.1:8000/` for API status,
   `http://127.0.0.1:8000/health/db` for database connectivity, and
   `http://127.0.0.1:8000/docs` for interactive API documentation.

The first user can be promoted to administrator directly in MySQL after
registering:

```sql
UPDATE Users SET role = 'admin' WHERE email = 'your-email@example.com';
```

Admin users create buses, routes, and schedules. Bus creation also creates
numbered seats (`1` through `total_seats`). Public registration always creates
a regular user; it cannot assign the admin role. The SQL schema stores
`travel_date` separately from `departure_time` and `arrival_time`; schedule
times are timezone-naive UTC values. An arrival time earlier than its departure
time can represent an overnight trip.

## Main endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Get a bearer access token |
| `GET` | `/auth/me` | Get the signed-in user |
| `POST` | `/admin/buses` | Add a bus and its seats (admin) |
| `POST` | `/admin/routes` | Add a route (admin) |
| `POST` | `/admin/schedules` | Add a schedule (admin) |
| `GET` | `/schedules` | Search by `source`, `destination`, and optional `travel_date` (`YYYY-MM-DD`) |
| `GET` | `/schedules/{schedule_id}/seats` | List seats and availability |
| `POST` | `/bookings` | Reserve seats and record a simulated successful payment |
| `GET` | `/bookings` | List the signed-in user's bookings |
| `GET` | `/bookings/{booking_id}` | Get a booking |
| `POST` | `/bookings/{booking_id}/cancel` | Cancel a confirmed booking |
| `GET` | `/health/db` | Check the MySQL connection |

Pass the login token as `Authorization: Bearer <token>`. Booking requests lock
the schedule row while checking seat availability and writing the booking,
booking-seat, and payment records in one transaction. The booking-seat table
uses `(booking_id, seat_id)` as its primary key; the API checks availability by
joining bookings to their schedules because it has no schedule column of its
own. The schedule lock serializes simultaneous booking requests for that
schedule. Cancelled seats become available again; the successful payment
record is retained as a transaction history entry. Payments are simulated and
do not charge a real payment method.

Use Alembic for future database changes: create revisions with
`alembic revision --autogenerate -m "description"` and apply them with
`alembic upgrade head`. Review generated revisions before applying them.
