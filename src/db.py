import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "joseph_perrier.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # wineries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wineries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        website_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        winery_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        product_url TEXT UNIQUE,
        description TEXT,
        datasheet_url TEXT,
        grape_varieties TEXT,
        operating_temperature TEXT,
        ageing_potential TEXT,
        aging TEXT,
        reserve_wines TEXT,
        dosage TEXT,
        crus_assembles TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (winery_id) REFERENCES wineries(id)
    );
    """)

    # media
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        media_type TEXT NOT NULL,
        media_url TEXT NOT NULL,
        source_page_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    conn.commit()
    conn.close()


def insert_winery(name, website_url=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO wineries (name, website_url)
    VALUES (?, ?)
    """, (name, website_url))

    conn.commit()
    winery_id = cursor.lastrowid
    conn.close()

    print(f"Inserted winery: {name}")
    return winery_id


def insert_product(winery_id, product_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO products (
        winery_id,
        name,
        product_url,
        description,
        datasheet_url,
        grape_varieties,
        operating_temperature,
        ageing_potential,
        aging,
        reserve_wines,
        dosage,
        crus_assembles
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        winery_id,
        product_data.get("name"),
        product_data.get("product_url"),
        product_data.get("description"),
        product_data.get("datasheet_url"),
        product_data.get("grape_varieties"),
        product_data.get("operating_temperature"),
        product_data.get("ageing_potential"),
        product_data.get("aging"),
        product_data.get("reserve_wines"),
        product_data.get("dosage"),
        product_data.get("crus_assembles")
    ))

    conn.commit()

    cursor.execute("""
    SELECT id FROM products WHERE product_url = ?
    """, (product_data.get("product_url"),))
    product_id = cursor.fetchone()[0]

    conn.close()

    print(f"Inserted product: {product_data.get('name')}")
    return product_id


def insert_media(product_id, media_type, media_url, source_page_url=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO media (product_id, media_type, media_url, source_page_url)
    VALUES (?, ?, ?, ?)
    """, (product_id, media_type, media_url, source_page_url))

    conn.commit()
    conn.close()

    print(f"Inserted media: {media_url}")