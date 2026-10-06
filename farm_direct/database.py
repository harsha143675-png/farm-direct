import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "farm_direct.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table (Farmers and Consumers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL CHECK(role IN ('farmer', 'consumer')),
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        state TEXT,
        district TEXT,
        city_village TEXT NOT NULL,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Crops table (Posted by Farmers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        crop_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        unit TEXT NOT NULL DEFAULT 'kg',
        quantity REAL NOT NULL,
        harvest_date TEXT,
        description TEXT,
        image_emoji TEXT DEFAULT '🌾',
        location TEXT NOT NULL,
        estimated_market_price REAL,
        status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available', 'sold_out')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Demands table (Posted by Consumers looking for crops)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS demands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        consumer_id INTEGER NOT NULL,
        crop_name TEXT NOT NULL,
        category TEXT NOT NULL,
        target_price REAL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL DEFAULT 'kg',
        location TEXT NOT NULL,
        notes TEXT,
        status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'fulfilled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (consumer_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Inquiries table (Direct connections/messages between Consumer and Farmer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER NOT NULL,
        consumer_id INTEGER NOT NULL,
        farmer_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        contact_phone TEXT NOT NULL,
        quantity_needed REAL,
        status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new', 'contacted', 'completed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (crop_id) REFERENCES crops (id) ON DELETE CASCADE,
        FOREIGN KEY (consumer_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (farmer_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Pre-seed default data if database is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_default_data(conn)

    conn.close()

def seed_default_data(conn):
    cursor = conn.cursor()
    pwd = generate_password_hash("password123")

    # Sample Farmers
    farmers = [
        ("farmer", "Ramesh Patel", "9876543210", "ramesh@farmer.com", pwd, "Gujarat", "Anand", "Borsad Village", "Near Canal Road"),
        ("farmer", "Suresh Kumar", "9812345678", "suresh@farmer.com", pwd, "Punjab", "Ludhiana", "Khanna Village", "Farm Gate #4"),
        ("farmer", "Anitha Devi", "9898989898", "anitha@farmer.com", pwd, "Karnataka", "Mandya", "Srirangapatna", "Green Acres Plot 12"),
        ("farmer", "Mohammad Rafiq", "9765432109", "rafiq@farmer.com", pwd, "Maharashtra", "Nashik", "Dindori", "Vineyard Valley")
    ]
    cursor.executemany("""
        INSERT INTO users (role, name, phone, email, password_hash, state, district, city_village, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, farmers)

    # Sample Consumers
    consumers = [
        ("consumer", "Pooja Sharma", "9123456780", "pooja@consumer.com", pwd, "Gujarat", "Ahmedabad", "Bodakdev", "B-203 Sunrise Residency"),
        ("consumer", "Amit Verma", "9234567891", "amit@consumer.com", pwd, "Karnataka", "Bengaluru", "Indiranagar", "12th Main Road, 4th Cross")
    ]
    cursor.executemany("""
        INSERT INTO users (role, name, phone, email, password_hash, state, district, city_village, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, consumers)

    # Sample Crops (Eliminating mediator savings: Direct Price vs Market/Retail Price)
    crops = [
        (1, "Organic Vine Tomatoes", "Vegetables", 25.0, "kg", 800.0, "2026-09-15", "Naturally grown red tomatoes, picked directly from our vine. Crisp and chemical-free.", "🍅", "Borsad, Anand (Gujarat)", 45.0, "available"),
        (1, "Fresh Green Chillies", "Vegetables", 35.0, "kg", 200.0, "2026-09-14", "Spicy G4 variety green chillies. Fresh harvest.", "🌶️", "Borsad, Anand (Gujarat)", 65.0, "available"),
        (2, "Premium Basmati Rice (Sharbati)", "Grains", 60.0, "kg", 2500.0, "2026-09-10", "Aromatic aged long grain basmati rice directly from Punjab fields. No polishing or adulteration.", "🌾", "Khanna, Ludhiana (Punjab)", 95.0, "available"),
        (2, "Golden Harvest Wheat (Sharbati)", "Grains", 28.0, "kg", 4000.0, "2026-09-08", "Cleaned, sun-dried nutritious golden wheat grains for fresh flour.", "🍞", "Khanna, Ludhiana (Punjab)", 42.0, "available"),
        (3, "Organic Cavendish Bananas", "Fruits", 30.0, "dozen", 400.0, "2026-09-16", "Naturally ripened without carbide. Sweet and nutrient rich.", "🍌", "Srirangapatna, Mandya (Karnataka)", 55.0, "available"),
        (3, "Fresh Farm Coconut", "Fruits", 25.0, "piece", 600.0, "2026-09-15", "Sweet water and thick tender coconut meat fresh from our plantation.", "🥥", "Srirangapatna, Mandya (Karnataka)", 45.0, "available"),
        (4, "Sweet Table Grapes (Thompson)", "Fruits", 70.0, "kg", 1200.0, "2026-09-12", "Crispy, juicy, seedless grapes directly from Nashik vineyard.", "🍇", "Dindori, Nashik (Maharashtra)", 120.0, "available"),
        (4, "Nashik Red Onions", "Vegetables", 22.0, "kg", 3000.0, "2026-09-13", "Medium to large size pungent fresh red onions. Stays fresh for months.", "🧅", "Dindori, Nashik (Maharashtra)", 40.0, "available")
    ]
    cursor.executemany("""
        INSERT INTO crops (farmer_id, crop_name, category, price, unit, quantity, harvest_date, description, image_emoji, location, estimated_market_price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, crops)

    # Sample Demands posted by consumers
    demands = [
        (5, "Alphonso / Kesar Mangoes", "Fruits", 150.0, 20.0, "kg", "Bodakdev, Ahmedabad", "Looking for naturally ripened sweet mangoes directly from farmer.", "active"),
        (6, "Pure Raw Organic Honey", "Spices & Others", 450.0, 5.0, "kg", "Indiranagar, Bengaluru", "Unprocessed single-origin raw bee honey.", "active"),
        (5, "Organic Potatoes (Pukhraj/Jyoti)", "Vegetables", 18.0, 50.0, "kg", "Bodakdev, Ahmedabad", "Need 50kg bag for family consumption directly from farmer.", "active")
    ]
    cursor.executemany("""
        INSERT INTO demands (consumer_id, crop_name, category, target_price, quantity, unit, location, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, demands)

    conn.commit()

# Helper queries
def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def create_user(role, name, phone, email, password, state, district, city_village, address):
    conn = get_db_connection()
    pwd_hash = generate_password_hash(password)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (role, name, phone, email, password_hash, state, district, city_village, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (role, name, phone, email, pwd_hash, state, district, city_village, address))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_all_crops(search_query="", category="", location_query=""):
    conn = get_db_connection()
    query = """
        SELECT c.*, u.name as farmer_name, u.phone as farmer_phone, u.district as farmer_district, u.state as farmer_state
        FROM crops c
        JOIN users u ON c.farmer_id = u.id
        WHERE c.status = 'available'
    """
    params = []

    if search_query:
        query += " AND (c.crop_name LIKE ? OR c.description LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if category:
        query += " AND c.category = ?"
        params.append(category)

    if location_query:
        query += " AND (c.location LIKE ? OR u.district LIKE ? OR u.state LIKE ?)"
        params.extend([f"%{location_query}%", f"%{location_query}%", f"%{location_query}%"])

    query += " ORDER BY c.created_at DESC"
    crops = conn.execute(query, params).fetchall()
    conn.close()
    return crops

def get_crop_by_id(crop_id):
    conn = get_db_connection()
    crop = conn.execute("""
        SELECT c.*, u.name as farmer_name, u.phone as farmer_phone, u.email as farmer_email,
               u.city_village as farmer_village, u.district as farmer_district, u.state as farmer_state,
               u.address as farmer_address
        FROM crops c
        JOIN users u ON c.farmer_id = u.id
        WHERE c.id = ?
    """, (crop_id,)).fetchone()
    conn.close()
    return crop

def add_crop(farmer_id, crop_name, category, price, unit, quantity, harvest_date, description, location, market_price, emoji):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO crops (farmer_id, crop_name, category, price, unit, quantity, harvest_date, description, location, estimated_market_price, image_emoji)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (farmer_id, crop_name, category, price, unit, quantity, harvest_date, description, location, market_price, emoji))
    crop_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return crop_id

def get_farmer_crops(farmer_id):
    conn = get_db_connection()
    crops = conn.execute("SELECT * FROM crops WHERE farmer_id = ? ORDER BY created_at DESC", (farmer_id,)).fetchall()
    conn.close()
    return crops

def update_crop_status(crop_id, farmer_id, status):
    conn = get_db_connection()
    conn.execute("UPDATE crops SET status = ? WHERE id = ? AND farmer_id = ?", (status, crop_id, farmer_id))
    conn.commit()
    conn.close()

def delete_crop(crop_id, farmer_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM crops WHERE id = ? AND farmer_id = ?", (crop_id, farmer_id))
    conn.commit()
    conn.close()

def add_demand(consumer_id, crop_name, category, target_price, quantity, unit, location, notes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO demands (consumer_id, crop_name, category, target_price, quantity, unit, location, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (consumer_id, crop_name, category, target_price, quantity, unit, location, notes))
    demand_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return demand_id

def get_all_demands(location=""):
    conn = get_db_connection()
    query = """
        SELECT d.*, u.name as consumer_name, u.phone as consumer_phone, u.district as consumer_district
        FROM demands d
        JOIN users u ON d.consumer_id = u.id
        WHERE d.status = 'active'
    """
    params = []
    if location:
        query += " AND (d.location LIKE ? OR u.district LIKE ?)"
        params.extend([f"%{location}%", f"%{location}%"])
    query += " ORDER BY d.created_at DESC"
    demands = conn.execute(query, params).fetchall()
    conn.close()
    return demands

def get_consumer_demands(consumer_id):
    conn = get_db_connection()
    demands = conn.execute("SELECT * FROM demands WHERE consumer_id = ? ORDER BY created_at DESC", (consumer_id,)).fetchall()
    conn.close()
    return demands

def add_inquiry(crop_id, consumer_id, farmer_id, message, contact_phone, quantity_needed):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inquiries (crop_id, consumer_id, farmer_id, message, contact_phone, quantity_needed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (crop_id, consumer_id, farmer_id, message, contact_phone, quantity_needed))
    inquiry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inquiry_id

def get_farmer_inquiries(farmer_id):
    conn = get_db_connection()
    inquiries = conn.execute("""
        SELECT i.*, c.crop_name, c.price, c.unit, u.name as consumer_name, u.city_village as consumer_location
        FROM inquiries i
        JOIN crops c ON i.crop_id = c.id
        JOIN users u ON i.consumer_id = u.id
        WHERE i.farmer_id = ?
        ORDER BY i.created_at DESC
    """, (farmer_id,)).fetchall()
    conn.close()
    return inquiries

def get_consumer_inquiries(consumer_id):
    conn = get_db_connection()
    inquiries = conn.execute("""
        SELECT i.*, c.crop_name, c.price, c.unit, c.location as crop_location, u.name as farmer_name, u.phone as farmer_phone
        FROM inquiries i
        JOIN crops c ON i.crop_id = c.id
        JOIN users u ON i.farmer_id = u.id
        WHERE i.consumer_id = ?
        ORDER BY i.created_at DESC
    """, (consumer_id,)).fetchall()
    conn.close()
    return inquiries

def get_stats():
    conn = get_db_connection()
    total_farmers = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'farmer'").fetchone()[0]
    total_consumers = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'consumer'").fetchone()[0]
    active_crops = conn.execute("SELECT COUNT(*) FROM crops WHERE status = 'available'").fetchone()[0]
    active_demands = conn.execute("SELECT COUNT(*) FROM demands WHERE status = 'active'").fetchone()[0]
    conn.close()
    return {
        "farmers": total_farmers,
        "consumers": total_consumers,
        "crops": active_crops,
        "demands": active_demands
    }
