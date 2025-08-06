"""
PostgreSQL Database Configuration and Connection Management
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'lost_found_campus'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': os.getenv('DB_PORT', '5432'),
    'sslmode': os.getenv('DB_SSL_MODE', 'prefer')
}

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to PostgreSQL database")
            return True
        except psycopg2.Error as e:
            print(f"❌ Error connecting to PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔒 Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            try:
                return self.cursor.fetchall()
            except psycopg2.ProgrammingError:
                # No results to fetch (e.g., CREATE TABLE, INSERT)
                return []
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Query error: {e}")
            raise e
    
    def execute_insert(self, query, params=None):
        """Execute insert and return the inserted record"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Insert error: {e}")
            raise e

def create_database_tables():
    """Create all database tables"""
    db = DatabaseManager()
    if not db.connect():
        return False
    
    try:
        # Create users table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create categories table
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create items table
        create_items_table = """
        CREATE TABLE IF NOT EXISTS items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(500) NOT NULL,
            description TEXT,
            category_id INTEGER REFERENCES categories(id),
            category VARCHAR(100), -- Keep for backward compatibility
            status VARCHAR(50) NOT NULL CHECK (status IN ('lost', 'found', 'returned', 'claimed')),
            location_found VARCHAR(500),
            location VARCHAR(500), -- Alternative location field
            date_found DATE,
            image_url TEXT,
            user_id UUID REFERENCES users(id),
            contact_info TEXT,
            custody_status VARCHAR(50) CHECK (custody_status IN ('kept_by_finder', 'handed_to_one_stop', 'left_where_found')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create items_images table for multiple images per item
        create_images_table = """
        CREATE TABLE IF NOT EXISTS item_images (
            id SERIAL PRIMARY KEY,
            item_id UUID REFERENCES items(id) ON DELETE CASCADE,
            image_url TEXT NOT NULL,
            image_type VARCHAR(50) DEFAULT 'photo',
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create claims table for tracking item claims
        create_claims_table = """
        CREATE TABLE IF NOT EXISTS claims (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            item_id UUID REFERENCES items(id) ON DELETE CASCADE,
            claimant_id UUID REFERENCES users(id),
            claimant_name VARCHAR(255),
            claimant_email VARCHAR(255),
            claimant_phone VARCHAR(50),
            claim_description TEXT,
            verification_questions TEXT, -- JSON field for verification questions
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'denied', 'verified')),
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create notifications table
        create_notifications_table = """
        CREATE TABLE IF NOT EXISTS notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            item_id UUID REFERENCES items(id) ON DELETE CASCADE,
            type VARCHAR(100) NOT NULL, -- 'item_found', 'claim_approved', etc.
            title VARCHAR(255) NOT NULL,
            message TEXT,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create audit_logs table for tracking changes
        create_audit_table = """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            table_name VARCHAR(100) NOT NULL,
            record_id VARCHAR(255) NOT NULL,
            action VARCHAR(50) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
            old_values JSONB,
            new_values JSONB,
            changed_by UUID REFERENCES users(id),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute table creation
        tables = [
            ("users", create_users_table),
            ("categories", create_categories_table),
            ("items", create_items_table),
            ("item_images", create_images_table),
            ("claims", create_claims_table),
            ("notifications", create_notifications_table),
            ("audit_logs", create_audit_table)
        ]
        
        for table_name, query in tables:
            print(f"📝 Creating {table_name} table...")
            db.execute_query(query)
        
        # Insert default categories
        default_categories = [
            ('electronics', 'Electronic devices like phones, laptops, tablets'),
            ('books', 'Textbooks, notebooks, and reading materials'),
            ('accessories', 'Personal accessories like jewelry, bags, keys'),
            ('clothing', 'Clothing items and wearables'),
            ('other', 'Items that do not fit in other categories')
        ]
        
        print("📝 Inserting default categories...")
        for name, description in default_categories:
            insert_category = """
            INSERT INTO categories (name, description) 
            VALUES (%s, %s) 
            ON CONFLICT (name) DO NOTHING;
            """
            db.execute_query(insert_category, (name, description))
        
        print("✅ All database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    finally:
        db.disconnect()

def migrate_json_to_postgresql():
    """Migrate data from JSON files to PostgreSQL"""
    db = DatabaseManager()
    if not db.connect():
        return False
    
    try:
        # Migrate users
        print("📦 Migrating users...")
        with open('user_db.json', 'r') as f:
            users = json.load(f)
        
        for user in users:
            insert_user = """
            INSERT INTO users (id, name, email, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
            """
            # Convert string ID to UUID format if needed
            if user['id'].count('-') == 4:
                user_id = user['id']
            else:
                # Generate a proper UUID for simple string IDs
                import uuid
                user_id = str(uuid.uuid4())
            created_at = user.get('created_at', datetime.now().isoformat())
            
            db.execute_query(insert_user, (
                user_id,
                user['name'],
                user['email'],
                user['password_hash'],
                created_at
            ))
        
        # Migrate items
        print("📦 Migrating items...")
        with open('lost_found_db.json', 'r') as f:
            items = json.load(f)
        
        for item in items:
            insert_item = """
            INSERT INTO items (
                id, title, description, category, status, location_found, 
                location, date_found, image_url, 
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            
            # Convert string ID to UUID format if needed
            if item['id'].count('-') == 4:
                item_id = item['id']
            else:
                # Generate a proper UUID for simple string IDs
                import uuid
                item_id = str(uuid.uuid4())
            
            db.execute_query(insert_item, (
                item_id,
                item['title'],
                item['description'],
                item['category'],
                item['status'],
                item.get('location_found'),
                item.get('location'),
                item.get('date_found'),
                item.get('image_url'),
                item.get('created_at', datetime.now().isoformat()),
                item.get('updated_at', datetime.now().isoformat())
            ))
        
        print("✅ Data migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    print("🗄️  Setting up PostgreSQL database...")
    
    if create_database_tables():
        print("🔄 Starting data migration...")
        migrate_json_to_postgresql()
        print("🎉 Database setup complete!")
    else:
        print("❌ Database setup failed!") 