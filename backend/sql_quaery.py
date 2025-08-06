#!/usr/bin/env python3
"""
Smart Database Setup - Only creates CLEAN tables if needed
NO JSON MIGRATION - Fresh start approach

IMPORTANT: This script does NOT load any data from JSON files.
It only creates empty tables and default categories.
All user data will come from the application interface.
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
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

def create_clean_tables():
    """Create fresh, empty tables without any JSON migration"""
    print("🔧 Creating fresh database tables...")
    
    try:
        # Connect to database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Create tables SQL - CLEAN VERSIONS
        tables_sql = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                is_admin BOOLEAN DEFAULT FALSE,
                is_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255),
                reset_token VARCHAR(255),
                reset_token_expires TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Categories table
            """
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Items table
            """
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                location_found VARCHAR(255),
                date_found DATE,
                time_found TIME,
                status VARCHAR(50) DEFAULT 'available',
                finder_id INTEGER REFERENCES users(id),
                claimed_by INTEGER REFERENCES users(id),
                claim_date TIMESTAMP,
                verification_questions TEXT,
                image_urls TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Claims table
            """
            CREATE TABLE IF NOT EXISTS claims (
                id SERIAL PRIMARY KEY,
                item_id INTEGER REFERENCES items(id),
                claimant_id INTEGER REFERENCES users(id),
                status VARCHAR(50) DEFAULT 'pending',
                verification_answers TEXT,
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            );
            """
        ]
        
        # Execute table creation
        for sql in tables_sql:
            cursor.execute(sql)
        
        # Insert default categories ONLY
        cursor.execute("""
            INSERT INTO categories (name, description) VALUES
            ('electronics', 'Electronic devices like phones, laptops, tablets'),
            ('books', 'Textbooks, notebooks, and reading materials'),
            ('accessories', 'Personal accessories like jewelry, bags, keys'),
            ('clothing', 'Clothing items and personal wear'),
            ('documents', 'IDs, cards, and important documents'),
            ('other', 'Other miscellaneous items')
            ON CONFLICT (name) DO NOTHING;
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Clean database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def smart_database_setup():
    """Setup database intelligently - only create if needed, NO JSON MIGRATION"""
    print("🗄️  Smart Database Setup (Clean Start)")
    print("=" * 35)
    
    try:
        # Connect to check existing tables
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Check existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['users', 'items', 'categories', 'claims']
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"🔧 Creating missing tables: {', '.join(missing_tables)}")
            cursor.close()
            connection.close()
            return create_clean_tables()
        else:
            # Show current data counts
            try:
                cursor.execute('SELECT COUNT(*) FROM items')
                item_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM users')
                user_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM categories')
                category_count = cursor.fetchone()[0]
                
                print("✅ Database already configured")
                print(f"   📱 Items: {item_count}")
                print(f"   👥 Users: {user_count}")
                print(f"   📂 Categories: {category_count}")
                print("   ⏭️  Skipping table creation")
                print("   🚫 NO JSON files loaded (clean start)")
                
            except Exception as e:
                print(f"⚠️  Tables exist but couldn't read counts: {e}")
                print("   🔧 This might be a schema issue - recreating tables...")
                cursor.close()
                connection.close()
                return create_clean_tables()
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        print("🔧 Attempting to create tables anyway...")
        return create_clean_tables()

if __name__ == "__main__":
    success = smart_database_setup()
    sys.exit(0 if success else 1)
