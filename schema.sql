CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_items TEXT,
    total_price REAL,
    status TEXT DEFAULT 'Przyjęte',
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE dish_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    dish_name TEXT,
    rating INTEGER,
    comment TEXT,
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

CREATE TABLE restaurant_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    delivery_time_rating INTEGER,
    service_rating INTEGER,
    food_quality_rating INTEGER,
    value_for_money_rating INTEGER,
    comment TEXT,
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

ALTER TABLE orders ADD COLUMN customer_name TEXT;
ALTER TABLE orders ADD COLUMN customer_phone TEXT;
ALTER TABLE orders ADD COLUMN customer_address TEXT;
ALTER TABLE orders ADD COLUMN customer_preferences TEXT;
