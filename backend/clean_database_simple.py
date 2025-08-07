#!/usr/bin/env python3
"""
Simple Database Cleaner - Remove all data while keeping table structure
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_database():
    """Clean all data from database tables"""
    print("🧹 Cleaning Lost & Found Database")
    print("=" * 40)
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT'),
            sslmode='require'
        )
        cursor = conn.cursor()
        
        print(f"✅ Connected to: {os.getenv('DB_NAME')}")
        
        # Define tables in dependency order (children first, parents last)
        tables_to_clean = [
            'audit_logs',
            'notifications', 
            'item_images',
            'claims',
            'items',
            'users'
            # Keep categories table with default data
        ]
        
        print("🗑️  Deleting data from tables...")
        
        total_deleted = 0
        for table in tables_to_clean:
            try:
                # Count records first
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Delete all records
                    cursor.execute(f"DELETE FROM {table}")
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    print(f"   ✅ {table}: {deleted} records deleted")
                else:
                    print(f"   ⚪ {table}: already empty")
                    
            except psycopg2.Error as e:
                print(f"   ⚠️  {table}: {e}")
                continue
        
        # Reset sequences for tables with serial IDs
        print("🔄 Resetting ID sequences...")
        sequences_to_reset = [
            ('categories', 'id'),
            ('item_images', 'id'),
            ('audit_logs', 'id')
        ]
        
        for table, column in sequences_to_reset:
            try:
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', '{column}'), 1, false)")
                print(f"   ✅ Reset {table}.{column} sequence")
            except psycopg2.Error:
                # Sequence might not exist, ignore
                pass
        
        # Commit changes
        conn.commit()
        
        print("")
        print("🎉 Database cleaning completed!")
        print(f"📊 Total records deleted: {total_deleted}")
        print("✅ All user data and items removed")
        print("📂 Categories preserved for new items")
        
        # Verify cleaning
        print("")
        print("🔍 Verification:")
        for table in ['users', 'items', 'claims', 'notifications']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                status = "✅ Empty" if count == 0 else f"❌ {count} records remain"
                print(f"   {table}: {status}")
            except:
                print(f"   {table}: ⚠️  Could not verify")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print(f"🗄️  Target Database: {os.getenv('DB_NAME')} on {os.getenv('DB_HOST')}")
    print("")
    
    confirm = input("⚠️  This will delete ALL users and items. Continue? (y/N): ")
    if confirm.lower() in ['y', 'yes']:
        clean_database()
    else:
        print("❌ Cancelled") 