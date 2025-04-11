import sqlite3
from werkzeug.security import generate_password_hash
from config import DATABASE_NAME

def create_test_user():
    """Create a test user for development purposes"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Create test user
        test_email = 'test@example.com'
        test_password = 'testpassword123'
        password_hash = generate_password_hash(test_password)
        
        cursor.execute("""
            INSERT OR REPLACE INTO users (email, password_hash)
            VALUES (?, ?)
        """, (test_email, password_hash))
        
        conn.commit()
        print(f"Test user created successfully with email: {test_email}")
        
    except sqlite3.Error as e:
        print(f"Database error occurred: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_user()
