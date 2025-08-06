"""
Database Seeding Script for Lost & Found Campus
Run this after setup_team_database.py to populate with sample data

This script loads sample items from lost_found_db.json and populates
the PostgreSQL database so all team members see the same items.
"""

import json
import sys
import os
from datetime import datetime
from database_config import DatabaseManager

def seed_database(auto_mode=False, force_reseed=False):
    """Populate database with sample data from JSON file
    
    Args:
        auto_mode (bool): If True, run without prompts (for automation)
        force_reseed (bool): If True, automatically clear existing data
    """
    if not auto_mode:
        print("🌱 Lost & Found Campus - Database Seeding")
        print("=" * 50)
    
    # Initialize database manager
    db = DatabaseManager()
    if not db.connect():
        if not auto_mode:
            print("❌ Database connection failed. Make sure:")
            print("   1. PostgreSQL is running")
            print("   2. You've run setup_team_database.py first")
            print("   3. Your .env file has correct database settings")
        sys.exit(1)
    
    try:
        # Check if data already exists
        db.cursor.execute("SELECT COUNT(*) FROM items")
        existing_count = db.cursor.fetchone()['count']
        
        if existing_count > 0:
            if auto_mode:
                if force_reseed:
                    print("🗑️  Clearing existing data...")
                    db.cursor.execute("DELETE FROM items")
                    db.connection.commit()
                else:
                    # In auto mode without force_reseed, just return success
                    print(f"✅ Database already has {existing_count} items. Keeping existing data.")
                    db.disconnect()
                    return
            else:
                print(f"ℹ️  Database already has {existing_count} items")
                response = input("🤔 Do you want to clear existing data and reseed? (y/N): ")
                if response.lower() != 'y':
                    print("✅ Keeping existing data. Seeding cancelled.")
                    db.disconnect()
                    return
                else:
                    print("🗑️  Clearing existing data...")
                    db.cursor.execute("DELETE FROM items")
                    db.connection.commit()
        
        # Load sample data from JSON file
        json_file_path = os.path.join(os.path.dirname(__file__), 'lost_found_db.json')
        
        if not os.path.exists(json_file_path):
            print(f"❌ Sample data file not found: {json_file_path}")
            sys.exit(1)
        
        if not auto_mode:
            print(f"📁 Loading sample data from {json_file_path}")
        
        with open(json_file_path, 'r') as f:
            sample_items = json.load(f)
        
        if not auto_mode:
            print(f"📋 Found {len(sample_items)} sample items to load")
        
        # Insert sample items into database
        inserted_count = 0
        
        for item in sample_items:
            try:
                # Convert the JSON item to match our database schema
                item_data = {
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'category': item.get('category', 'other'),
                    'status': item.get('status', 'found'),
                    'location_found': item.get('location_found', ''),
                    'date_found': item.get('date_found', datetime.now().isoformat()),
                    'image_url': item.get('image_url', ''),
                    'user_id': item.get('user_id', 'admin'),
                    'created_at': item.get('created_at', datetime.now().isoformat()),
                    'updated_at': item.get('updated_at', datetime.now().isoformat())
                }
                
                # Insert into database
                insert_query = """
                    INSERT INTO items (
                        title, description, category, status, location_found, 
                        date_found, image_url, user_id,
                        created_at, updated_at
                    ) VALUES (
                        %(title)s, %(description)s, %(category)s, %(status)s, %(location_found)s,
                        %(date_found)s, %(image_url)s, %(user_id)s,
                        %(created_at)s, %(updated_at)s
                    )
                """
                
                db.cursor.execute(insert_query, item_data)
                inserted_count += 1
                
            except Exception as e:
                print(f"⚠️  Error inserting item '{item.get('title', 'Unknown')}': {e}")
                continue
        
        # Commit all changes
        db.connection.commit()
        
        if auto_mode:
            print(f"✅ Database seeded with {inserted_count} sample items")
        else:
            print(f"✅ Successfully seeded database with {inserted_count} items!")
            print(f"📊 Database now contains {inserted_count} sample items")
            
            # Show summary of what was added
            db.cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM items 
                GROUP BY status 
                ORDER BY status
            """)
            
            status_summary = db.cursor.fetchall()
            print("\n📈 Item status summary:")
            for row in status_summary:
                print(f"   {row['status']}: {row['count']} items")
            
            print("\n🎉 Database seeding complete!")
            print("💡 All team members will now see the same sample data")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure database tables exist (run setup_team_database.py)")
        print("   2. Check that lost_found_db.json exists and is valid")
        print("   3. Verify database connection settings in .env")
        sys.exit(1)
    
    finally:
        db.disconnect()

def show_database_status():
    """Show current database status"""
    db = DatabaseManager()
    if not db.connect():
        print("❌ Cannot connect to database")
        return
    
    try:
        db.cursor.execute("SELECT COUNT(*) FROM items")
        total_items = db.cursor.fetchone()['count']
        
        db.cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM items 
            GROUP BY status 
            ORDER BY status
        """)
        
        status_breakdown = db.cursor.fetchall()
        
        print(f"📊 Database Status:")
        print(f"   Total items: {total_items}")
        for row in status_breakdown:
            print(f"   {row['status']}: {row['count']} items")
            
    except Exception as e:
        print(f"❌ Error checking database status: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        show_database_status()
    elif len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Auto mode for automated setup scripts
        force_reseed = len(sys.argv) > 2 and sys.argv[2] == "--force"
        seed_database(auto_mode=True, force_reseed=force_reseed)
    else:
        seed_database()
