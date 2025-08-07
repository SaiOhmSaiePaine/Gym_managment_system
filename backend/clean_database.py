#!/usr/bin/env python3
"""
Clean Database Script - Remove all data while keeping table structure
This script will delete all records from all tables but preserve the schema
"""

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
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432'),
    'sslmode': os.getenv('DB_SSL_MODE', 'prefer')
}

def clean_database():
    """Clean all data from database tables while preserving structure"""
    print("🧹 Lost & Found Database Cleaner")
    print("=" * 40)
    print("⚠️  WARNING: This will delete ALL data from the database!")
    print("   Tables will be preserved, but all records will be removed.")
    print("")
    
    # Ask for confirmation
    confirm = input("Are you sure you want to continue? (type 'YES' to confirm): ")
    if confirm != 'YES':
        print("❌ Operation cancelled.")
        return False
    
    try:
        # Connect to database
        print("🔌 Connecting to PostgreSQL database...")
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        
        # Get all table names
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
        
        # Disable foreign key constraints temporarily
        print("🔓 Disabling foreign key constraints...")
        cursor.execute("SET session_replication_role = replica;")
        
        # Delete data from all tables
        deleted_counts = {}
        for table in tables:
            print(f"🗑️  Cleaning table: {table}")
            
            # Count records before deletion
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count_result = cursor.fetchone()
            count_before = count_result['count'] if isinstance(count_result, dict) else count_result[0]
            
            # Delete all records
            cursor.execute(f"DELETE FROM {table}")
            deleted_count = cursor.rowcount
            deleted_counts[table] = deleted_count
            
            # Reset auto-increment sequences if they exist
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                AND column_default LIKE 'nextval%'
            """)
            
            sequences = cursor.fetchall()
            for seq in sequences:
                sequence_name = f"{table}_{seq[0]}_seq"
                try:
                    cursor.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1")
                    print(f"   🔄 Reset sequence: {sequence_name}")
                except psycopg2.Error:
                    # Sequence might not exist, ignore
                    pass
            
            print(f"   ✅ Deleted {deleted_count} records from {table}")
        
        # Re-enable foreign key constraints
        print("🔒 Re-enabling foreign key constraints...")
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        # Commit all changes
        connection.commit()
        
        # Summary
        print("")
        print("🎉 Database cleaning completed successfully!")
        print("=" * 40)
        print("📊 Summary:")
        total_deleted = sum(deleted_counts.values())
        for table, count in deleted_counts.items():
            if count > 0:
                print(f"   {table}: {count} records deleted")
        print(f"📈 Total records deleted: {total_deleted}")
        print("")
        print("✅ All tables are now empty but structure is preserved")
        print("🔄 Auto-increment sequences have been reset")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return False

def verify_clean_database():
    """Verify that all tables are empty"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Get all table names
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        print("🔍 Verification Results:")
        print("-" * 25)
        all_empty = True
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count_result = cursor.fetchone()
            count = count_result['count'] if isinstance(count_result, dict) else count_result[0]
            status = "✅ Empty" if count == 0 else f"❌ {count} records"
            print(f"{table}: {status}")
            if count > 0:
                all_empty = False
        
        if all_empty:
            print("\n🎉 All tables are confirmed empty!")
        else:
            print("\n⚠️  Some tables still contain data")
        
        cursor.close()
        connection.close()
        
        return all_empty
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

if __name__ == "__main__":
    print("🗄️  Database Configuration:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print(f"   Port: {DB_CONFIG['port']}")
    print("")
    
    if clean_database():
        print("")
        verify_clean_database()
    else:
        print("❌ Database cleaning failed!") 