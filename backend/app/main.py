from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine
from app.routers import auth, bookings, catalog


app = FastAPI(title="Bus Travel Booking System API", version="1.0.0")

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(bookings.router)


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Bus Travel Booking System API is running"}


@app.get("/health/db")
def database_health() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Check server and configuration.",
        ) from error

    return {"status": "connected", "database": "MySQL"}
