"""
Script to create a sample SQLite database for testing the Data Dictionary Generator.

This database includes:
- Multiple related tables
- Various data types
- Primary keys, foreign keys, unique constraints
- Indexes
- Sample data with realistic values
"""

import sqlite3
from datetime import datetime, timedelta
import random

def create_sample_database(db_path='sample-database.db'):
    """Create a sample SQLite database with multiple tables and relationships"""

    # Remove existing database if present
    import os
    if os.path.exists(db_path):
        os.remove(db_path)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create schema
    cursor.executescript("""
    -- Users table
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE,
        phone_number TEXT,
        account_balance REAL DEFAULT 0.0,
        is_active BOOLEAN DEFAULT 1,
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME,
        profile_picture BLOB
    );

    -- Create index on email for faster lookups
    CREATE INDEX idx_users_email ON users(email);
    CREATE INDEX idx_users_active ON users(is_active);

    -- Products table
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        stock_quantity INTEGER DEFAULT 0,
        sku TEXT UNIQUE NOT NULL,
        manufacturer TEXT,
        weight_kg REAL,
        is_available BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX idx_products_category ON products(category);
    CREATE INDEX idx_products_sku ON products(sku);

    -- Orders table
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10, 2) NOT NULL,
        tax_amount DECIMAL(10, 2) DEFAULT 0.0,
        shipping_cost DECIMAL(10, 2) DEFAULT 0.0,
        status TEXT DEFAULT 'pending',
        shipping_address TEXT,
        billing_address TEXT,
        payment_method TEXT,
        tracking_number TEXT,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );

    CREATE INDEX idx_orders_user ON orders(user_id);
    CREATE INDEX idx_orders_status ON orders(status);
    CREATE INDEX idx_orders_date ON orders(order_date);

    -- Order Items table (many-to-many relationship)
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        discount_percentage REAL DEFAULT 0.0,
        subtotal DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
    );

    CREATE INDEX idx_order_items_order ON order_items(order_id);
    CREATE INDEX idx_order_items_product ON order_items(product_id);

    -- Reviews table
    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        review_title TEXT,
        review_text TEXT,
        review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        helpful_count INTEGER DEFAULT 0,
        verified_purchase BOOLEAN DEFAULT 0,
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        UNIQUE (product_id, user_id)
    );

    CREATE INDEX idx_reviews_product ON reviews(product_id);
    CREATE INDEX idx_reviews_user ON reviews(user_id);
    CREATE INDEX idx_reviews_rating ON reviews(rating);
    """)

    print("✓ Database schema created")

    # Insert sample data

    # Sample users
    users_data = [
        ('john_doe', 'john.doe@example.com', 'John', 'Doe', '1985-03-15', '+1-555-0101', 1250.50, 1),
        ('jane_smith', 'jane.smith@example.com', 'Jane', 'Smith', '1990-07-22', '+1-555-0102', 3420.75, 1),
        ('bob_johnson', 'bob.j@example.com', 'Bob', 'Johnson', '1978-11-30', '+1-555-0103', 890.25, 1),
        ('alice_williams', 'alice.w@example.com', 'Alice', 'Williams', '1995-01-08', '+1-555-0104', 2100.00, 1),
        ('charlie_brown', 'charlie.b@example.com', 'Charlie', 'Brown', '1988-09-14', None, 450.00, 1),
        ('diana_prince', 'diana.p@example.com', 'Diana', 'Prince', '1992-05-20', '+1-555-0106', 5200.00, 1),
        ('eve_anderson', 'eve.a@example.com', 'Eve', 'Anderson', '1983-12-03', '+1-555-0107', 0.0, 0),
        ('frank_miller', 'frank.m@example.com', 'Frank', 'Miller', '1998-04-25', '+1-555-0108', 780.50, 1),
    ]

    cursor.executemany("""
        INSERT INTO users (username, email, first_name, last_name, date_of_birth, phone_number, account_balance, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)

    print(f"✓ Inserted {len(users_data)} users")

    # Sample products
    products_data = [
        ('Wireless Mouse', 'Ergonomic wireless mouse with USB receiver', 'Electronics', 29.99, 150, 'WM-001', 'TechCorp', 0.12, 1),
        ('Mechanical Keyboard', 'RGB backlit mechanical keyboard', 'Electronics', 89.99, 75, 'KB-002', 'TechCorp', 0.85, 1),
        ('USB-C Cable', '6ft braided USB-C charging cable', 'Accessories', 12.99, 500, 'CBL-003', 'CableCo', 0.05, 1),
        ('Laptop Stand', 'Adjustable aluminum laptop stand', 'Accessories', 45.00, 200, 'LS-004', 'OfficeGear', 0.65, 1),
        ('Webcam HD', '1080p HD webcam with microphone', 'Electronics', 59.99, 120, 'WC-005', 'TechCorp', 0.18, 1),
        ('Desk Lamp', 'LED desk lamp with adjustable brightness', 'Office', 34.99, 180, 'DL-006', 'LightWorks', 0.45, 1),
        ('Notebook Set', 'Pack of 3 ruled notebooks', 'Office', 9.99, 350, 'NB-007', 'PaperCo', 0.30, 1),
        ('Wireless Headphones', 'Noise-cancelling over-ear headphones', 'Electronics', 149.99, 60, 'HP-008', 'AudioMax', 0.25, 1),
        ('Phone Stand', 'Adjustable phone holder', 'Accessories', 14.99, 400, 'PS-009', 'OfficeGear', 0.08, 1),
        ('Monitor 27"', '4K UHD 27-inch monitor', 'Electronics', 399.99, 30, 'MON-010', 'DisplayPro', 5.20, 1),
    ]

    cursor.executemany("""
        INSERT INTO products (product_name, description, category, price, stock_quantity, sku, manufacturer, weight_kg, is_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products_data)

    print(f"✓ Inserted {len(products_data)} products")

    # Sample orders
    base_date = datetime.now() - timedelta(days=90)
    orders_data = []

    for i in range(20):
        user_id = random.randint(1, 8)
        order_date = base_date + timedelta(days=random.randint(0, 90))
        total = round(random.uniform(20, 500), 2)
        tax = round(total * 0.08, 2)
        shipping = round(random.uniform(5, 15), 2) if total < 100 else 0.0
        status = random.choice(['pending', 'processing', 'shipped', 'delivered', 'delivered'])
        payment = random.choice(['credit_card', 'debit_card', 'paypal', 'apple_pay'])

        orders_data.append((
            user_id,
            order_date.strftime('%Y-%m-%d %H:%M:%S'),
            total,
            tax,
            shipping,
            status,
            f"{random.randint(100, 999)} Main St, City, ST {random.randint(10000, 99999)}",
            f"{random.randint(100, 999)} Main St, City, ST {random.randint(10000, 99999)}",
            payment,
            f"TRK{random.randint(100000, 999999)}" if status in ['shipped', 'delivered'] else None
        ))

    cursor.executemany("""
        INSERT INTO orders (user_id, order_date, total_amount, tax_amount, shipping_cost, status,
                           shipping_address, billing_address, payment_method, tracking_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders_data)

    print(f"✓ Inserted {len(orders_data)} orders")

    # Sample order items
    order_items_data = []
    for order_id in range(1, 21):
        num_items = random.randint(1, 4)
        products_in_order = random.sample(range(1, 11), num_items)

        for product_id in products_in_order:
            quantity = random.randint(1, 3)
            # Get product price
            cursor.execute("SELECT price FROM products WHERE product_id = ?", (product_id,))
            unit_price = cursor.fetchone()[0]
            discount = random.choice([0, 0, 0, 5, 10, 15])  # Most items have no discount
            subtotal = round(unit_price * quantity * (1 - discount/100), 2)

            order_items_data.append((
                order_id,
                product_id,
                quantity,
                unit_price,
                discount,
                subtotal
            ))

    cursor.executemany("""
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_percentage, subtotal)
        VALUES (?, ?, ?, ?, ?, ?)
    """, order_items_data)

    print(f"✓ Inserted {len(order_items_data)} order items")

    # Sample reviews
    reviews_data = [
        (1, 1, 5, 'Excellent mouse!', 'Very comfortable and responsive. Great for gaming and work.', 15, 1),
        (2, 2, 4, 'Great keyboard', 'Love the mechanical feel, but a bit loud for office use.', 8, 1),
        (3, 1, 5, 'Best purchase ever', 'This mouse changed my life. Highly recommend!', 23, 1),
        (8, 3, 5, 'Perfect headphones', 'Sound quality is amazing. Noise cancellation works great.', 31, 1),
        (4, 4, 3, 'Good but overpriced', 'Does the job but I think $45 is too much for a laptop stand.', 5, 1),
        (1, 5, 4, 'Very good webcam', 'Clear image quality. Works well for video calls.', 12, 1),
        (5, 2, 5, 'Love it!', 'Best keyboard I have ever used. RGB is beautiful.', 18, 1),
        (10, 6, 5, 'Stunning display', '4K is incredible. Great for photo editing.', 27, 1),
        (2, 3, 2, 'Not for me', 'Cable frays easily. Expected better quality.', 3, 1),
        (7, 4, 4, 'Solid stand', 'Very sturdy and adjustable. Does what it says.', 9, 1),
    ]

    cursor.executemany("""
        INSERT INTO reviews (product_id, user_id, rating, review_title, review_text, helpful_count, verified_purchase)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, reviews_data)

    print(f"✓ Inserted {len(reviews_data)} reviews")

    # Commit and close
    conn.commit()
    conn.close()

    print(f"\n✅ Sample database created successfully: {db_path}")
    print(f"\nDatabase Statistics:")
    print(f"  - 5 tables (users, products, orders, order_items, reviews)")
    print(f"  - {len(users_data)} users")
    print(f"  - {len(products_data)} products")
    print(f"  - {len(orders_data)} orders")
    print(f"  - {len(order_items_data)} order items")
    print(f"  - {len(reviews_data)} reviews")
    print(f"  - Multiple foreign key relationships")
    print(f"  - Various constraints (UNIQUE, NOT NULL, CHECK)")
    print(f"  - Multiple indexes for performance")
    print(f"\nYou can now upload this file to test the SQLite parser!")

if __name__ == '__main__':
    create_sample_database()
