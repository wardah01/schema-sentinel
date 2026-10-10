CREATE TABLE users (
    id INT,
    name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    phone INT,
    city VARCHAR(255)
);

CREATE TABLE rides (
    ride_id INT,
    user_name VARCHAR(255),
    user_phone INT,
    driver_name VARCHAR(255),
    pickup VARCHAR(255),
    dropoff VARCHAR(255),
    fare FLOAT,
    status VARCHAR(255),
    created_at VARCHAR(255)
);

CREATE TABLE payments (
    payment_id INT,
    ride_id INT,
    card_number VARCHAR(255),
    amount FLOAT
);