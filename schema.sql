CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_name TEXT,
    item_description TEXT,
    item_price REAL,
    status TEXT DEFAULT 'Przyjęte',
    FOREIGN KEY (user_id) REFERENCES users (id)
);
