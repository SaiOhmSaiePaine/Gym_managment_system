"""
Enhanced Lost & Found Campus API Server with PostgreSQL Database and AWS S3 Integration
"""
import http.server
import socketserver
import json
import urllib.parse
import uuid
import hashlib
import jwt
import mimetypes
import os
from datetime import datetime, timedelta
from database_config import DatabaseManager
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import S3 upload functionality
try:
    from s3_upload import upload_file_to_s3, test_s3_connection
    S3_AVAILABLE = True
    print("📦 S3 upload module loaded successfully")
except ImportError as e:
    print(f"⚠️  S3 upload module not available: {e}")
    S3_AVAILABLE = False
    def upload_file_to_s3(*args, **kwargs):
        raise NotImplementedError("S3 upload not available")
    def test_s3_connection():
        return False

# Configuration from environment variables
PORT = int(os.getenv('PORT', 8000))
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-this-in-production')
UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')

class PostgreSQLRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = DatabaseManager()
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def send_cors_response(self, status_code, data=None, content_type='application/json'):
        """Send response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-type', content_type)
        self.end_headers()
        
        if data:
            response = json.dumps(data, default=str) if content_type == 'application/json' else data
            self.wfile.write(response.encode())
    
    def get_user_from_token(self):
        """Extract user from JWT token"""
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            if not self.db.connect():
                return None
            
            query = "SELECT * FROM users WHERE id = %s"
            users = self.db.execute_query(query, (payload['user_id'],))
            self.db.disconnect()
            
            return dict(users[0]) if users else None
        except (jwt.InvalidTokenError, IndexError, psycopg2.Error):
            return None
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        try:
            # Block statistics-related API calls
            if path in ['/api/admin/statistics', '/api/admin/stats', '/api/statistics', '/api/stats']:
                self.send_cors_response(404, {'error': 'Statistics functionality disabled'})
                return
            
            if path == '/api/items':
                self.handle_get_items(query_params)
            elif path.startswith('/api/items/'):
                item_id = path.split('/')[-1]
                self.handle_get_item(item_id)
            elif path == '/api/users/me':
                self.handle_get_current_user()
            elif path == '/api/categories':
                self.handle_get_categories()
            elif path == '/admin/login':
                # Serve our custom admin login page
                self.handle_admin_page()
            elif path == '/admin' or path.startswith('/admin/'):
                # All other admin routes serve the React app (it handles routing internally)
                self.handle_react_admin_page()
            elif path.startswith('/static/'):
                self.handle_react_admin_static_file(path)
            elif path == '/api/admin/items':
                self.handle_get_admin_items(query_params)
            elif path == '/api/admin/users':
                self.handle_get_admin_users(query_params)
            elif path.startswith('/uploads/'):
                self.handle_static_file(path)
            elif path == '/':
                self.send_cors_response(404, {'error': 'Not found'})
            else:
                self.send_cors_response(404, {'error': 'Not found'})
        except Exception as e:
            print(f"❌ GET Error: {e}")
            self.send_cors_response(500, {'error': 'Internal server error'})
    
    def handle_get_items(self, query_params):
        """Get items with search, filter, and pagination"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            # Extract query parameters
            page = int(query_params.get('page', [1])[0])
            per_page = int(query_params.get('per_page', [12])[0])
            search = query_params.get('search', [''])[0]
            category = query_params.get('category', [''])[0]
            status = query_params.get('status', [''])[0]
            
            # Build query
            conditions = []
            params = []
            
            # ALWAYS exclude returned items from frontend view (users should not see returned items)
            conditions.append("status != %s")
            params.append("returned")
            
            if search:
                conditions.append("(title ILIKE %s OR description ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            if category:
                conditions.append("category = %s")
                params.append(category)
            
            if status:
                conditions.append("status = %s")
                params.append(status)
            
            where_clause = f"WHERE {' AND '.join(conditions)}"
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM items {where_clause}"
            total_result = self.db.execute_query(count_query, params)
            total = total_result[0]['count']
            
            # Get items with pagination - join with users table to get user names
            offset = (page - 1) * per_page
            items_query = f"""
                SELECT i.*, u.name as user_name, u.email as user_email
                FROM items i 
                LEFT JOIN users u ON i.user_id = u.id
                {where_clause} 
                ORDER BY i.created_at DESC 
                LIMIT %s OFFSET %s
            """
            
            items = self.db.execute_query(items_query, params + [per_page, offset])
            
            # Convert to list of dicts with actual user names
            items_list = []
            for item in items:
                item_dict = dict(item)
                # Fallback to 'Unknown' only if user not found (null join)
                if not item_dict.get('user_name'):
                    item_dict['user_name'] = 'Unknown'
                if not item_dict.get('user_email'):
                    item_dict['user_email'] = 'team@example.com'
                items_list.append(item_dict)
            
            response = {
                'items': items_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
            self.send_cors_response(200, response)
            
        except Exception as e:
            print(f"❌ Error getting items: {e}")
            self.send_cors_response(500, {'error': 'Failed to get items'})
        finally:
            self.db.disconnect()
    
    def handle_get_item(self, item_id):
        """Get single item by ID"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            query = """
                SELECT i.*, u.name as user_name, u.email as user_email
                FROM items i 
                LEFT JOIN users u ON i.user_id = u.id
                WHERE i.id = %s
            """
            items = self.db.execute_query(query, (item_id,))
            
            if not items:
                self.send_cors_response(404, {'error': 'Item not found'})
                return
            
            item = dict(items[0])
            # Fallback to defaults only if user not found (null join)
            if not item.get('user_name'):
                item['user_name'] = 'Unknown'
            if not item.get('user_email'):
                item['user_email'] = 'team@example.com'
            
            # Get additional images
            images_query = "SELECT * FROM item_images WHERE item_id = %s ORDER BY is_primary DESC"
            images = self.db.execute_query(images_query, (item_id,))
            item['additional_images'] = [dict(img) for img in images]
            
            self.send_cors_response(200, item)
            
        except Exception as e:
            print(f"❌ Error getting item: {e}")
            self.send_cors_response(500, {'error': 'Failed to get item'})
        finally:
            self.db.disconnect()
    
    def handle_get_current_user(self):
        """Get current user info from JWT token"""
        user = self.get_user_from_token()
        if not user:
            self.send_cors_response(401, {'error': 'Authentication required'})
            return
        
        # Remove sensitive data
        user.pop('password_hash', None)
        self.send_cors_response(200, user)
    
    def handle_get_categories(self):
        """Get all categories"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            query = "SELECT * FROM categories ORDER BY name"
            categories = self.db.execute_query(query)
            
            response = [dict(cat) for cat in categories]
            self.send_cors_response(200, response)
            
        except Exception as e:
            print(f"❌ Error getting categories: {e}")
            self.send_cors_response(500, {'error': 'Failed to get categories'})
        finally:
            self.db.disconnect()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/api/items':
                self.handle_create_item()
            elif path == '/api/users/register':
                self.handle_register()
            elif path == '/api/users/login':
                self.handle_login()
            elif path == '/api/admin/login':
                self.handle_admin_login()
            elif path.startswith('/api/items/') and path.endswith('/claim'):
                item_id = path.split('/')[-2]
                self.handle_claim_item(item_id)
            else:
                self.send_cors_response(404, {'error': 'Not found'})
        except Exception as e:
            print(f"❌ POST Error: {e}")
            self.send_cors_response(500, {'error': 'Internal server error'})
    
    def handle_create_item(self):
        """Create new item"""
        user = self.get_user_from_token()
        if not user:
            self.send_cors_response(401, {'error': 'Authentication required'})
            return
        
        content_type = self.headers.get('Content-Type', '')
        
        if content_type.startswith('application/json'):
            # Handle JSON data
            self.handle_create_item_json(user)
        elif content_type.startswith('multipart/form-data'):
            # Handle multipart form data (file upload)
            self.handle_create_item_multipart(user)
        else:
            self.send_cors_response(400, {'error': 'Content type must be application/json or multipart/form-data'})
            return

    def handle_create_item_json(self, user):
        """Handle JSON item creation"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if not self.db.connect():
                self.send_cors_response(500, {'error': 'Database connection failed'})
                return
            
            # Use the title as provided - no auto-generation since frontend requires it
            title = data.get('title', '').strip()
            if not title:
                self.send_cors_response(400, {'error': 'Title is required'})
                return
            
            # Insert item
            item_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO items (
                    id, title, description, category, status, location_found, 
                    date_found, image_url, user_id, custody_status, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            
            now = datetime.now()
            # Handle both 'location' and 'location_found' field names for compatibility
            location = data.get('location_found', '') or data.get('location', '')
            
            params = (
                item_id,
                title,
                data.get('description', ''),
                data.get('category', 'other'),
                data.get('status', 'found'),
                location,
                data.get('date_found', now.date()),
                data.get('image_url'),
                user['id'],
                data.get('custody_status'),  # Add custody status
                now,
                now
            )
            
            result = self.db.execute_insert(insert_query, params)
            
            if result:
                response = dict(result)
                response['user_name'] = user['name']
                self.send_cors_response(201, response)
            else:
                self.send_cors_response(500, {'error': 'Failed to create item'})
        
        except Exception as e:
            print(f"❌ Error creating item: {e}")
            self.send_cors_response(500, {'error': 'Failed to create item'})
        finally:
            self.db.disconnect()

    def handle_create_item_multipart(self, user):
        """Handle multipart form data item creation with file upload"""
        import cgi
        import io
        
        try:
            # Use cgi.FieldStorage for proper multipart parsing
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Create a file-like object from the request body
            fp = io.BytesIO(self.rfile.read(content_length))
            
            # Parse multipart form data using cgi.FieldStorage
            form = cgi.FieldStorage(
                fp=fp,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers.get('Content-Type', ''),
                    'CONTENT_LENGTH': str(content_length)
                }
            )
            
            # Extract form fields
            item_data = {}
            file_data = None
            filename = None
            
            print(f"🔍 Parsing multipart form with {len(form.keys())} fields")
            
            for field_name in form.keys():
                field = form[field_name]
                print(f"🏷️  Processing field: '{field_name}'")
                
                if field.filename:  # This is a file field
                    filename = field.filename
                    file_data = field.file.read()
                    print(f"📤 Found file: {filename} ({len(file_data)} bytes)")
                else:  # This is a regular form field
                    value = field.value if hasattr(field, 'value') else ''
                    item_data[field_name] = value
                    print(f"✅ Field '{field_name}': '{value}'")

            # Handle image upload with S3 PRIORITY and local backup
            image_url = None
            if filename and file_data:
                print(f"📤 Processing image upload: {filename}")
                
                # PRIORITY 1: Try AWS S3 first (always attempt if module available)
                s3_success = False
                if S3_AVAILABLE:
                    try:
                        image_url = upload_file_to_s3(file_data, filename)
                        if image_url:  # S3 upload successful
                            print(f"✅ Image uploaded to S3: {image_url}")
                            s3_success = True
                        else:
                            print("⚠️  S3 upload returned None, trying local backup...")
                    except Exception as e:
                        print(f"⚠️  S3 upload failed: {e}, falling back to local storage...")
                
                # BACKUP: Use local storage only if S3 failed or unavailable
                if not s3_success:
                    try:
                        print("💾 Using local storage as backup...")
                        os.makedirs(UPLOAD_DIR, exist_ok=True)
                        
                        file_ext = os.path.splitext(filename)[1]
                        unique_filename = str(uuid.uuid4()) + file_ext
                        file_path = os.path.join(UPLOAD_DIR, unique_filename)
                        
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        
                        image_url = f"/uploads/{unique_filename}"
                        print(f"✅ Image saved locally as backup: {image_url}")
                        
                    except Exception as e:
                        print(f"❌ Local storage backup also failed: {e}")
                        image_url = None
            else:
                print("📝 Creating item without image")
            
            # Use the title as provided - no auto-generation since frontend requires it
            title = item_data.get('title', '').strip()
            description = item_data.get('description', '').strip()
            status = item_data.get('status', 'found')
            category = item_data.get('category', 'other')
            
            # Debug: Print what we received
            print(f"🔍 Received form data: {item_data}")
            print(f"🏷️  Title received: '{title}'")
            print(f"📝 Description received: '{description}'")
            
            # Validate that title is provided since frontend requires it
            if not title:
                self.send_cors_response(400, {'error': 'Title is required'})
                return

            if not self.db.connect():
                self.send_cors_response(500, {'error': 'Database connection failed'})
                return

            try:
                # Insert item
                item_id = str(uuid.uuid4())
                insert_query = """
                    INSERT INTO items (
                        id, title, description, category, status, location_found, 
                        date_found, image_url, user_id, custody_status, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """
                
                now = datetime.now()
                params = (
                    item_id,
                    title,
                    description,
                    item_data.get('category', 'other'),
                    status,
                    item_data.get('location_found', ''),
                    item_data.get('date_found', now.date()),
                    image_url,
                    user['id'],
                    item_data.get('custody_status'),  # Add custody status
                    now,
                    now
                )
                
                result = self.db.execute_insert(insert_query, params)
                
                if result:
                    response = dict(result)
                    response['user_name'] = user['name']
                    print(f"✅ Created item with image: {title} (ID: {item_id})")
                    self.send_cors_response(201, response)
                else:
                    self.send_cors_response(500, {'error': 'Failed to create item'})
            
            except Exception as e:
                print(f"❌ Error creating item: {e}")
                self.send_cors_response(500, {'error': 'Failed to create item'})
            finally:
                self.db.disconnect()
                
        except Exception as e:
            print(f"❌ Error parsing multipart data: {e}")
            import traceback
            traceback.print_exc()
            self.send_cors_response(500, {'error': 'Failed to parse form data'})
    
    def handle_register(self):
        """Handle user registration"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            # Check if email already exists
            check_query = "SELECT id FROM users WHERE email = %s"
            existing = self.db.execute_query(check_query, (data['email'],))
            
            if existing:
                self.send_cors_response(400, {'error': 'Email already registered'})
                return
            
            # Create user
            user_id = str(uuid.uuid4())
            password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
            
            insert_query = """
                INSERT INTO users (id, name, email, password_hash, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, email, created_at
            """
            
            result = self.db.execute_insert(insert_query, (
                user_id,
                data['name'],
                data['email'],
                password_hash,
                datetime.now()
            ))
            
            if result:
                user_data = dict(result)
                token = jwt.encode({
                    'user_id': user_data['id'],
                    'exp': datetime.utcnow() + timedelta(days=7)
                }, JWT_SECRET, algorithm='HS256')
                
                response = {
                    'user': user_data,
                    'token': token
                }
                self.send_cors_response(201, response)
            else:
                self.send_cors_response(500, {'error': 'Failed to create user'})
        
        except Exception as e:
            print(f"❌ Error registering user: {e}")
            self.send_cors_response(500, {'error': 'Registration failed'})
        finally:
            self.db.disconnect()
    
    def handle_login(self):
        """Handle user login"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
            
            query = """
                SELECT id, name, email, created_at 
                FROM users 
                WHERE email = %s AND password_hash = %s
            """
            users = self.db.execute_query(query, (data['email'], password_hash))
            
            if not users:
                self.send_cors_response(401, {'error': 'Invalid credentials'})
                return
            
            user = dict(users[0])
            token = jwt.encode({
                'user_id': user['id'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }, JWT_SECRET, algorithm='HS256')
            
            response = {
                'user': user,
                'token': token
            }
            self.send_cors_response(200, response)
        
        except Exception as e:
            print(f"❌ Error logging in: {e}")
            self.send_cors_response(500, {'error': 'Login failed'})
        finally:
            self.db.disconnect()
    
    def handle_claim_item(self, item_id):
        """Handle item claim request"""
        user = self.get_user_from_token()
        if not user:
            self.send_cors_response(401, {'error': 'Authentication required'})
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = b''
        if content_length > 0:
            post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except json.JSONDecodeError:
            data = {}
        
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            # Check if item exists and is available for claiming
            item_query = "SELECT * FROM items WHERE id = %s AND status IN ('found', 'lost')"
            items = self.db.execute_query(item_query, (item_id,))
            
            if not items:
                self.send_cors_response(404, {'error': 'Item not found or not available for claiming'})
                return
            
            item = dict(items[0])
            
            # Check if user has already claimed this item
            existing_claim_query = "SELECT id FROM claims WHERE item_id = %s AND user_id = %s"
            existing_claims = self.db.execute_query(existing_claim_query, (item_id, user['id']))
            
            if existing_claims:
                self.send_cors_response(400, {'error': 'You have already claimed this item'})
                return
            
            # Create claim record
            claim_id = str(uuid.uuid4())
            claim_query = """
                INSERT INTO claims (id, item_id, user_id, claim_message, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """
            
            claim_result = self.db.execute_insert(claim_query, (
                claim_id,
                item_id,
                user['id'],
                data.get('message', 'I believe this item belongs to me.'),
                'pending',
                datetime.now()
            ))
            
            if claim_result:
                # Create notification for item owner if different from claimer
                if item['user_id'] != user['id']:
                    notification_id = str(uuid.uuid4())
                    notification_query = """
                        INSERT INTO notifications (id, user_id, type, title, message, item_id, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    notification_title = f"Claim request for your {item['status']} item"
                    notification_message = f"{user['name']} has requested to claim '{item['title']}'"
                    
                    self.db.execute_insert(notification_query, (
                        notification_id,
                        item['user_id'],
                        'claim_request',
                        notification_title,
                        notification_message,
                        item_id,
                        datetime.now()
                    ))
                
                # Log the claim in audit log
                audit_id = str(uuid.uuid4())
                audit_query = """
                    INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, details, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                audit_details = json.dumps({
                    'item_title': item['title'],
                    'claim_message': data.get('message', 'I believe this item belongs to me.'),
                    'item_owner_id': item['user_id']
                })
                
                self.db.execute_insert(audit_query, (
                    audit_id,
                    user['id'],
                    'claim_item',
                    'item',
                    item_id,
                    audit_details,
                    datetime.now()
                ))
                
                response = {
                    'message': 'Claim submitted successfully',
                    'claim': dict(claim_result),
                    'item': item
                }
                self.send_cors_response(201, response)
            else:
                self.send_cors_response(500, {'error': 'Failed to create claim'})
        
        except Exception as e:
            print(f"❌ Error handling claim: {e}")
            self.send_cors_response(500, {'error': 'Failed to process claim'})
        finally:
            self.db.disconnect()
    
    def handle_static_file(self, path):
        """Serve static files from uploads directory"""
        file_path = path[1:]  # Remove leading slash
        
        if os.path.exists(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_cors_response(404, {'error': 'File not found'})
    
    def handle_home(self):
        """Serve basic home page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lost & Found Campus API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>🔍 Lost & Found Campus API with PostgreSQL</h1>
            <p>Enhanced API server running with PostgreSQL database</p>
            
            <h2>📡 API Endpoints:</h2>
            <div class="endpoint"><strong>GET /api/items</strong> - Get all items (with search & pagination)</div>
            <div class="endpoint"><strong>GET /api/items/{id}</strong> - Get single item</div>
            <div class="endpoint"><strong>POST /api/items</strong> - Create new item (requires auth)</div>
            <div class="endpoint"><strong>GET /api/categories</strong> - Get all categories</div>
            <div class="endpoint"><strong>POST /api/users/register</strong> - Register new user</div>
            <div class="endpoint"><strong>POST /api/users/login</strong> - User login</div>
            <div class="endpoint"><strong>GET /api/users/me</strong> - Get current user (requires auth)</div>
            
            <h2>🗄️ Database Status:</h2>
            <p>✅ Connected to PostgreSQL database</p>
            <p>📊 Tables: users, items, categories, claims, notifications, audit_logs</p>
            
            <h2>🚀 Features:</h2>
            <ul>
                <li>✅ PostgreSQL database with proper relationships</li>
                <li>✅ JWT authentication</li>
                <li>✅ Advanced search and filtering</li>
                <li>✅ Image upload support</li>
                <li>✅ User management</li>
                <li>✅ Audit logging</li>
                <li>✅ Claims management</li>
                <li>✅ Notifications system</li>
            </ul>
        </body>
        </html>
        """
        
        self.send_cors_response(200, html, 'text/html')

    def do_PUT(self):
        """Handle PUT requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path.startswith('/api/items/'):
                item_id = path.split('/')[-1]
                self.handle_update_item(item_id)
            else:
                self.send_cors_response(404, {'error': 'Not found'})
        except Exception as e:
            print(f"❌ PUT Error: {e}")
            self.send_cors_response(500, {'error': 'Internal server error'})

    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path.startswith('/api/items/'):
                item_id = path.split('/')[-1]
                self.handle_delete_item(item_id)
            elif path.startswith('/api/admin/users/'):
                user_id = path.split('/')[-1]
                self.handle_delete_user(user_id)
            else:
                self.send_cors_response(404, {'error': 'Not found'})
        except Exception as e:
            print(f"❌ DELETE Error: {e}")
            self.send_cors_response(500, {'error': 'Internal server error'})

    def handle_update_item(self, item_id):
        """Update item (for admin - change status, notes, location, etc.)"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                update_data = json.loads(post_data.decode('utf-8'))
                
                print(f"🔍 Admin updating item {item_id} with data: {update_data}")
                
                # Build update query with all possible admin-updateable fields
                fields = []
                values = []
                
                # Map frontend field names to database field names
                field_mapping = {
                    'status': 'status',
                    'notes': 'admin_notes',  # Use the new admin_notes field
                    'admin_notes': 'admin_notes',
                    'location_found': 'location_found',
                    'location': 'location_found',  # Alternative field name
                    'title': 'title',
                    'description': 'description',
                    'category': 'category',
                    'custody_status': 'custody_status',
                    'contact_info': 'contact_info'
                }
                
                for frontend_field, db_field in field_mapping.items():
                    if frontend_field in update_data and update_data[frontend_field] is not None:
                        fields.append(f"{db_field} = %s")
                        values.append(update_data[frontend_field])
                
                if fields:
                    # Always update the updated_at timestamp
                    fields.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(item_id)
                    
                    query = f"UPDATE items SET {', '.join(fields)} WHERE id = %s RETURNING id, title, status, admin_notes"
                    
                    print(f"🔍 Executing query: {query}")
                    print(f"🔍 With values: {values}")
                    
                    result = self.db.execute_query(query, values)
                    
                    if result and len(result) > 0:
                        updated_item = result[0]
                        print(f"✅ Item updated successfully: {updated_item}")
                        self.send_cors_response(200, {
                            'message': 'Item updated successfully',
                            'item': dict(updated_item)
                        })
                    else:
                        print(f"❌ No item found with id: {item_id}")
                        self.send_cors_response(404, {'error': 'Item not found'})
                else:
                    print(f"❌ No valid fields provided for update")
                    self.send_cors_response(400, {'error': 'No valid fields to update'})
            else:
                self.send_cors_response(400, {'error': 'No data provided'})
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            self.send_cors_response(400, {'error': 'Invalid JSON data'})
        except Exception as e:
            print(f"❌ Error updating item: {e}")
            import traceback
            traceback.print_exc()
            self.send_cors_response(500, {'error': f'Failed to update item: {str(e)}'})
        finally:
            self.db.disconnect()

    def handle_delete_item(self, item_id):
        """Delete item (admin only)"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            # First delete related images
            self.db.execute_query("DELETE FROM item_images WHERE item_id = %s", (item_id,))
            
            # Then delete the item
            result = self.db.execute_query("DELETE FROM items WHERE id = %s", (item_id,))
            
            if result:
                self.send_cors_response(200, {'message': 'Item deleted successfully'})
            else:
                self.send_cors_response(404, {'error': 'Item not found'})
                
        except Exception as e:
            print(f"❌ Error deleting item: {e}")
            self.send_cors_response(500, {'error': 'Failed to delete item'})
        finally:
            self.db.disconnect()

    def handle_admin_login(self):
        """Handle admin login with simple credentials"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                credentials = json.loads(post_data.decode('utf-8'))
                
                # Simple admin credentials from environment or defaults
                admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
                
                if (credentials.get('username') == admin_username and 
                    credentials.get('password') == admin_password):
                    
                    # Generate simple session token
                    admin_token = "admin_" + str(datetime.now().timestamp())
                    
                    self.send_cors_response(200, {
                        "success": True,
                        "token": admin_token,
                        "message": "Admin login successful"
                    })
                else:
                    self.send_cors_response(401, {"error": "Invalid credentials"})
            else:
                self.send_cors_response(400, {"error": "No credentials provided"})
        except Exception as e:
            print(f"❌ Admin login error: {e}")
            self.send_cors_response(500, {"error": str(e)})

    def handle_get_admin_items(self, query_params):
        """Handle GET /api/admin/items - shows ALL items including returned ones for admin"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            # Get query parameters
            search = query_params.get('search', [''])[0]
            category = query_params.get('category', [''])[0]
            status = query_params.get('status', [''])[0]
            
            # Build query for ALL items (no status filtering for returned items)
            conditions = []
            params = []
            
            if search:
                conditions.append("(title ILIKE %s OR description ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            if category:
                conditions.append("category = %s")
                params.append(category)
            
            if status:
                conditions.append("status = %s")
                params.append(status)
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
            # Get ALL items without pagination for admin - join with users table to get user names
            items_query = f"""
                SELECT i.*, u.name as user_name, u.email as user_email
                FROM items i 
                LEFT JOIN users u ON i.user_id = u.id
                {where_clause} 
                ORDER BY i.created_at DESC
            """
            
            items = self.db.execute_query(items_query, params)
            
            # Convert to list of dicts with actual user names
            items_list = []
            for item in items:
                item_dict = dict(item)
                # Fallback to defaults only if user not found (null join)
                if not item_dict.get('user_name'):
                    item_dict['user_name'] = 'Unknown'
                if not item_dict.get('user_email'):
                    item_dict['user_email'] = 'team@example.com'
                items_list.append(item_dict)
            
            response = {
                'items': items_list,
                'total': len(items_list),
                'page': 1,
                'per_page': len(items_list)
            }
            
            self.send_cors_response(200, response)
            
        except Exception as e:
            print(f"❌ Error getting admin items: {e}")
            self.send_cors_response(500, {'error': 'Failed to get admin items'})
        finally:
            self.db.disconnect()

    def handle_get_admin_users(self, query_params):
        """Handle GET /api/admin/users - returns all users with their item statistics"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            # Get query parameters
            search = query_params.get('search', [''])[0]
            role = query_params.get('role', [''])[0]
            
            # Build query conditions
            conditions = []
            params = []
            
            if search:
                conditions.append("(u.name ILIKE %s OR u.email ILIKE %s)")
                params.extend([f"%{search}%", f"%{search}%"])
            
            if role and role != 'all':
                conditions.append("u.role = %s")
                params.append(role)
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
            # Get all users with their item statistics
            users_query = f"""
                SELECT 
                    u.id,
                    u.name,
                    u.email,
                    u.role,
                    u.created_at,
                    u.updated_at,
                    COUNT(i.id) as item_count,
                    COUNT(CASE WHEN i.status = 'lost' THEN 1 END) as lost_count,
                    COUNT(CASE WHEN i.status = 'found' THEN 1 END) as found_count,
                    COUNT(CASE WHEN i.status = 'returned' THEN 1 END) as returned_count
                FROM users u
                LEFT JOIN items i ON u.id = i.user_id
                {where_clause}
                GROUP BY u.id, u.name, u.email, u.role, u.created_at, u.updated_at
                ORDER BY u.created_at DESC
            """
            
            users = self.db.execute_query(users_query, params)
            
            # Convert to list of dicts
            users_list = []
            for user in users:
                user_dict = dict(user)
                # Ensure counts are integers (PostgreSQL returns them as strings sometimes)
                user_dict['item_count'] = int(user_dict['item_count'] or 0)
                user_dict['lost_count'] = int(user_dict['lost_count'] or 0)
                user_dict['found_count'] = int(user_dict['found_count'] or 0)
                user_dict['returned_count'] = int(user_dict['returned_count'] or 0)
                
                # Ensure role has a default value
                if not user_dict.get('role'):
                    user_dict['role'] = 'user'
                    
                users_list.append(user_dict)
            
            response = {
                'users': users_list,
                'total': len(users_list),
                'page': 1,
                'per_page': len(users_list)
            }
            
            self.send_cors_response(200, response)
            
        except Exception as e:
            print(f"❌ Error getting admin users: {e}")
            self.send_cors_response(500, {'error': 'Failed to get admin users'})
        finally:
            self.db.disconnect()

    def handle_delete_user(self, user_id):
        """Handle DELETE /api/admin/users/{id} - delete a user and all their items"""
        if not self.db.connect():
            self.send_cors_response(500, {'error': 'Database connection failed'})
            return
        
        try:
            # First check if user exists
            user_query = "SELECT id, name, email FROM users WHERE id = %s"
            user_result = self.db.execute_query(user_query, [user_id])
            
            if not user_result or len(user_result) == 0:
                self.send_cors_response(404, {'error': 'User not found'})
                return
            
            user = dict(user_result[0])
            print(f"🗑️ Admin deleting user: {user['name']} ({user['email']})")
            
            # Delete user's items first (foreign key constraint)
            items_delete_query = "DELETE FROM items WHERE user_id = %s"
            items_deleted = self.db.execute_query(items_delete_query, [user_id])
            print(f"🗑️ Deleted {len(items_deleted) if items_deleted else 0} items for user {user_id}")
            
            # Delete the user
            user_delete_query = "DELETE FROM users WHERE id = %s RETURNING id, name, email"
            deleted_user = self.db.execute_query(user_delete_query, [user_id])
            
            if deleted_user and len(deleted_user) > 0:
                deleted_user_data = dict(deleted_user[0])
                print(f"✅ User deleted successfully: {deleted_user_data}")
                self.send_cors_response(200, {
                    'message': 'User deleted successfully',
                    'deleted_user': deleted_user_data
                })
            else:
                self.send_cors_response(500, {'error': 'Failed to delete user'})
                
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
            import traceback
            traceback.print_exc()
            self.send_cors_response(500, {'error': f'Failed to delete user: {str(e)}'})
        finally:
            self.db.disconnect()

    def handle_admin_page(self):
        """Serve the admin dashboard HTML page"""
        admin_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lost & Found Campus - Admin Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
            position: relative;
            overflow: hidden;
        }
        
        /* Animated background elements */
        body::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: 
                radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 0%, transparent 50%);
            animation: float 20s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(30px, -30px) rotate(120deg); }
            66% { transform: translate(-20px, 20px) rotate(240deg); }
        }
        
        .container { 
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 450px;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #ff6b6b, #ffa500);
            border-radius: 20px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: white;
            font-weight: 700;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 8px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            font-weight: 300;
        }
        
        .login-form {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 25px;
            box-shadow: 
                0 25px 50px rgba(0,0,0,0.15),
                0 0 0 1px rgba(255,255,255,0.2);
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .login-form h2 { 
            color: #2d3748; 
            margin-bottom: 35px; 
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .input-group {
            position: relative;
            margin-bottom: 25px;
        }
        
        .login-form input {
            width: 100%;
            padding: 18px 25px;
            border: 2px solid #e2e8f0;
            border-radius: 15px;
            font-size: 16px;
            background: #f8fafc;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }
        
        .login-form input:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
        }
        
        .login-form input::placeholder {
            color: #a0aec0;
            font-weight: 400;
        }
        
        .login-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 30px;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
            position: relative;
            overflow: hidden;
        }
        
        .login-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }
        
        .login-btn:active {
            transform: translateY(-1px);
        }
        
        .login-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .login-btn:hover::before {
            left: 100%;
        }
        
        .error-message {
            color: #e53e3e;
            background: linear-gradient(135deg, #fed7d7, #feb2b2);
            border: 1px solid #fc8181;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: none;
            font-weight: 500;
            animation: shake 0.5s ease-in-out;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .security-note {
            margin-top: 25px;
            padding: 15px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            color: #4a5568;
            font-size: 14px;
            border-left: 4px solid #667eea;
        }
        
        /* Loading animation */
        .loading {
            display: none;
            margin: 10px auto;
        }
        
        .loading-spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #e2e8f0;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive design */
        @media (max-width: 480px) {
            .container {
                padding: 15px;
            }
            
            .login-form {
                padding: 35px 25px;
                border-radius: 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .logo {
                width: 60px;
                height: 60px;
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🔍</div>
            <h1>Lost & Found</h1>
            <p class="subtitle">Administrative Dashboard</p>
        </div>
        
        <div class="login-form">
            <h2>Welcome Back</h2>
            <div class="error-message" id="errorMessage"></div>
            
            <div class="input-group">
                <input type="text" id="username" placeholder="Username" value="admin">
            </div>
            
            <div class="input-group">
                <input type="password" id="password" placeholder="Password" value="admin123">
            </div>
            
            <button class="login-btn" onclick="login()">
                <span id="loginText">Sign In</span>
                <div class="loading" id="loading">
                    <div class="loading-spinner"></div>
                </div>
            </button>
            
            <div class="security-note">
                <strong>Security Notice:</strong> This is a secure admin area. All login attempts are monitored and logged.
            </div>
        </div>
    </div>
    
    <script>
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('errorMessage');
            const loginBtn = document.querySelector('.login-btn');
            const loginText = document.getElementById('loginText');
            const loading = document.getElementById('loading');
            
            // Show loading state
            loginBtn.disabled = true;
            loginText.style.display = 'none';
            loading.style.display = 'block';
            errorDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Success animation
                    loginBtn.style.background = 'linear-gradient(135deg, #48bb78, #38a169)';
                    loginText.textContent = 'Success!';
                    loginText.style.display = 'block';
                    loading.style.display = 'none';
                    
                    // Redirect after short delay
                    setTimeout(() => {
                        window.location.href = '/admin/dashboard';
                    }, 800);
                } else {
                    throw new Error(result.error || 'Login failed');
                }
            } catch (error) {
                // Reset button state
                loginBtn.disabled = false;
                loginText.style.display = 'block';
                loading.style.display = 'none';
                loginBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                
                // Show error
                errorDiv.textContent = 'Login failed: ' + error.message;
                errorDiv.style.display = 'block';
                
                // Shake animation
                errorDiv.style.animation = 'none';
                setTimeout(() => {
                    errorDiv.style.animation = 'shake 0.5s ease-in-out';
                }, 10);
            }
        }
        
        // Enter key support
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                login();
            }
        });
        
        // Auto-focus username field
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('username').focus();
        });
    </script>
</body>
</html>
        """
        
        self.send_cors_response(200, admin_html, 'text/html')

    def handle_react_admin_page(self):
        """Serve the React admin interface build"""
        try:
            # Path to the React admin build
            admin_build_path = os.path.join(os.path.dirname(__file__), 'admin_build', 'index.html')
            
            if os.path.exists(admin_build_path):
                with open(admin_build_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Inject admin mode configuration with statistics disabled
                admin_config = """
                <script>
                    window.ADMIN_MODE = true;
                    window.API_BASE_URL = window.location.origin;
                    window.DISABLE_STATISTICS = true;
                    window.FEATURES_DISABLED = ['statistics', 'dashboard', 'stats'];
                    console.log('🔧 Admin Mode Enabled:', {
                        ADMIN_MODE: window.ADMIN_MODE,
                        API_BASE_URL: window.API_BASE_URL,
                        DISABLE_STATISTICS: window.DISABLE_STATISTICS,
                        FEATURES_DISABLED: window.FEATURES_DISABLED,
                        port: window.location.port
                    });
                </script>
                """
                
                # Insert the config before the closing </head> tag
                html_content = html_content.replace('</head>', f'{admin_config}</head>')
                
                # Inject the admin interface modifier script to replace edit buttons with delete buttons
                modifier_script_path = os.path.join(os.path.dirname(__file__), 'admin_interface_modifier.js')
                if os.path.exists(modifier_script_path):
                    with open(modifier_script_path, 'r', encoding='utf-8') as f:
                        modifier_script = f.read()
                    
                    # Inject the script before the closing body tag
                    delete_button_script = f"""
                    <script type="text/javascript">
                    {modifier_script}
                    </script>
                    </body>"""
                    
                    html_content = html_content.replace('</body>', delete_button_script)
                    print(f"✅ Injected delete button functionality into admin interface")
                else:
                    print(f"⚠️  Admin modifier script not found at {modifier_script_path}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html_content.encode('utf-8'))))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
                
                print(f"✅ Served React admin interface from {admin_build_path} (Statistics disabled)")
            else:
                print(f"❌ Admin build not found at {admin_build_path}")
                self.send_cors_response(404, {'error': 'Admin interface not found. Please run build_admin.sh first.'})
        except Exception as e:
            print(f"❌ Error serving React admin page: {e}")
            self.send_cors_response(500, {'error': 'Failed to serve admin interface'})

    def handle_react_admin_static_file(self, path):
        """Handle static file requests for React admin interface"""
        try:
            # Remove the /static/ prefix to get the actual file path
            file_path = path[8:]  # Remove '/static/'
            admin_static_path = os.path.join(os.path.dirname(__file__), 'admin_build', 'static', file_path)
            
            if os.path.exists(admin_static_path):
                # Determine content type
                content_type, _ = mimetypes.guess_type(admin_static_path)
                if content_type is None:
                    content_type = 'application/octet-stream'
                
                # Read and serve the file
                with open(admin_static_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                # Add cache headers for static assets
                self.send_header('Cache-Control', 'public, max-age=31536000')
                self.end_headers()
                self.wfile.write(content)
                
                print(f"✅ Served React admin static file: {file_path}")
            else:
                print(f"❌ Admin static file not found: {admin_static_path}")
                self.send_cors_response(404, {'error': 'Static file not found'})
        except Exception as e:
            print(f"❌ Error serving React admin static file: {e}")
            self.send_cors_response(500, {'error': 'Failed to serve static file'})

def main():
    """Start the PostgreSQL-powered server with AWS S3 integration"""
    print("🗄️  Lost & Found Campus API Server with PostgreSQL & AWS S3")
    print("=" * 65)
    
    # Test database connection
    db = DatabaseManager()
    if db.connect():
        print("✅ PostgreSQL database connection successful")
        
        # Check if tables exist
        try:
            db.execute_query("SELECT COUNT(*) FROM users")
            print("✅ Database tables are ready")
        except psycopg2.Error:
            print("⚠️  Database tables not found. Run 'python database_config.py' to set up tables.")
        
        db.disconnect()
    else:
        print("❌ PostgreSQL database connection failed!")
        print("📋 Make sure PostgreSQL is running and database credentials are correct")
        print("💡 Check config/database.env.example for configuration")
        return
    
    # Test S3 connection
    print("\n🔧 Testing AWS S3 connection...")
    if S3_AVAILABLE:
        try:
            if test_s3_connection():
                print("✅ AWS S3 connection successful!")
                print("📤 Images will be stored in AWS S3")
            else:
                print("⚠️  AWS S3 connection failed - will use local storage as fallback")
        except Exception as e:
            print(f"⚠️  S3 connection error: {e} - will use local storage as fallback")
    else:
        print("⚠️  S3 module not available - using local storage only")
    
    # Ensure upload directory exists (for fallback)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    try:
        with socketserver.TCPServer(("", PORT), PostgreSQLRequestHandler) as httpd:
            print(f"\n🚀 Server running at http://localhost:{PORT}")
            print(f"📱 Frontend should be available at http://localhost:3000")
            print(f"🗄️  Database: PostgreSQL")
            print(f"☁️  Images: {'AWS S3' if S3_AVAILABLE and test_s3_connection() else 'Local Storage'}")
            print(f"📁 Upload directory: {UPLOAD_DIR}")
            print(f"🛡️  Admin panel: http://localhost:{PORT}/admin")
            print("💡 Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use!")
            print("💡 Try: lsof -i :8000 and kill existing processes")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()