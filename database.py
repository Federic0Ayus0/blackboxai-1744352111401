import sqlite3
from config import DATABASE_NAME, logger

def create_tables():
    """
    Creates all necessary tables for the invoice system.
    Uses context manager for proper resource management and includes error handling.
    """
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    reset_token TEXT
                )
            ''')
            
            # Create invoices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_number TEXT PRIMARY KEY,
                    customer TEXT,
                    issue_date TEXT,
                    due_date TEXT,
                    total_amount REAL,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create invoice_items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT,
                    item_name TEXT,
                    quantity INTEGER,
                    price REAL,
                    FOREIGN KEY (invoice_number) REFERENCES invoices(invoice_number)
                )
            ''')
            
            # Create quotations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotations (
                    quotation_number TEXT PRIMARY KEY,
                    customer TEXT,
                    issue_date TEXT,
                    expiry_date TEXT,
                    total_amount REAL,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create quotation_items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotation_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quotation_number TEXT,
                    item_name TEXT,
                    quantity INTEGER,
                    price REAL,
                    FOREIGN KEY (quotation_number) REFERENCES quotations(quotation_number)
                )
            ''')
            
            # Create stock table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock (
                    item_name TEXT PRIMARY KEY,
                    quantity INTEGER,
                    unit TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create discounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discounts (
                    name TEXT PRIMARY KEY,
                    percentage REAL,
                    fixed_amount REAL,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            conn.commit()
            logger.info("All database tables created successfully")
            
    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    create_tables()
