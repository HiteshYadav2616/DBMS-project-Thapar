
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15),
    password_hash VARCHAR(255) NOT NULL
);

-- 2. Buses table
CREATE TABLE Buses (
    bus_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_number VARCHAR(30) NOT NULL UNIQUE,
    bus_type VARCHAR(50),
    total_seats INT NOT NULL
);

-- 3. Routes table
CREATE TABLE Routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    distance DECIMAL(8,2),
    CHECK (distance IS NULL OR distance >= 0),
    CHECK (source <> destination)
);

-- 4. Schedules table
CREATE TABLE Schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id INT NOT NULL,
    route_id INT NOT NULL,
    travel_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES Buses(bus_id),
    FOREIGN KEY (route_id) REFERENCES Routes(route_id),
    CHECK (fare >= 0)
);

-- 5. Seats table
CREATE TABLE Seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES Buses(bus_id),
    UNIQUE (bus_id, seat_number)
);

-- 6. Bookings table
CREATE TABLE Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    booking_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedules(schedule_id),
    CHECK (total_amount >= 0),
    CHECK (status IN ('Pending', 'Confirmed', 'Cancelled'))
);

-- 7. Booking_Seats table
CREATE TABLE Booking_Seats (
    booking_id INT NOT NULL,
    seat_id INT NOT NULL,
    ticket_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (booking_id, seat_id),
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
    FOREIGN KEY (seat_id) REFERENCES Seats(seat_id),
    CHECK (ticket_price >= 0)
);

-- 8. Payments table
CREATE TABLE Payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(30),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
    CHECK (amount >= 0),
    CHECK (payment_status IN ('Pending', 'Successful', 'Failed', 'Refunded'))
);

-- Verify that all tables have been created
SHOW TABLES;